"""Reproduce all stress-test rows and summary tables from runtime contexts."""
from pathlib import Path
import sys, json, csv, copy, random, math, hashlib, gzip
from collections import Counter
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.metrics import *
ROOT=Path(__file__).resolve().parents[1]

def assets(c):
    # Inventory baseline: unplayed assets are intentionally retained after routing edits.
    return '\n'.join([c['context']]+[e['action_text']+'\n'+e['text'] for e in c['edges']])

def mutate(c,kind,dose,seed):
    es=copy.deepcopy(c['edges']);r=random.Random(seed);n=len(es);k=max(1,math.ceil(n*dose));indices=r.sample(range(n),min(k,n));changed=[]
    if kind=='typography':
        for e in es:e['text']=e['text'].upper()+' !!!';e['action_text']=e['action_text'].upper()
    elif kind=='duplicate':es += copy.deepcopy(es)
    elif kind=='reorder':es.reverse()
    elif kind=='drop':
        indices=indices[:min(k,n-1)];es=[e for i,e in enumerate(es) if i not in indices];changed=indices
    elif kind=='collapse':
        target=r.randrange(n)
        for i in indices:
            if i==target:continue
            for key in ['outcome','text','delta','next_actions','terminal']:es[i][key]=copy.deepcopy(es[target][key])
        changed=indices
    elif kind=='permute':
        indices=r.sample(range(n),min(n,max(2,k)));old=copy.deepcopy(es)
        for i,j in zip(indices,indices[1:]+indices[:1]):
            for key in ['outcome','text','delta','next_actions','terminal']:es[i][key]=copy.deepcopy(old[j][key])
        changed=indices
    return es,changed

def main():
    contexts=[]
    for game in ['the_intercept','emoji']:
        contexts+=json.loads((ROOT/f'data/processed/{game}.contexts.json').read_text())
    inv=[assets(c) for c in contexts];df=Counter(t for s in inv for t in words(s));idf={t:1+math.log((1+len(inv))/(1+v)) for t,v in df.items()}
    rows=[];ablation=[];manifest=[]
    for c in contexts:
        cases=[(k,1.0,0) for k in ['identity','typography','duplicate','reorder']]
        cases += [(k,d,s) for k in ['drop','collapse','permute'] for d in [.25,.5,1.] for s in range(5)]
        for kind,dose,seed in cases:
            v,edits=mutate(c,kind,dose,seed);a=assets(c);b=assets({**c,'context':c['context'].upper()+' !!!','edges':v}) if kind=='typography' else a
            structural=kind in ['drop','collapse','permute'];changed=transitions(c['edges'])!=transitions(v)
            row={'game':c['game'],'context_id':c['context_id'],'operation':kind,'dose':dose,'seed':seed,'changed':changed,'eligible':not structural or changed,'n_options':len(c['edges']),**profile(c,v,a,b,idf)}
            rows.append(row)
            manifest.append({'game':c['game'],'context_id':c['context_id'],'operation':kind,'dose':dose,'seed':seed,'eligible':row['eligible'],'changed_indices':edits,'outcome_map':[{'action':e['id'],'outcome':e['outcome']} for e in v]})
            if structural and changed:
                for mode in ['full','text','state','terminal']:
                    aa={(e['id'],consequence(e,mode)) for e in c['edges']};bb={(e['id'],consequence(e,mode)) for e in v}
                    ablation.append({'game':c['game'],'context_id':c['context_id'],'operation':kind,'dose':dose,'seed':seed,'representation':mode,'distance':jaccard(aa,bb)})
    frame=pd.DataFrame(rows);(ROOT/'results/metric_rows.csv.gz').write_bytes(gzip.compress(frame.to_csv(index=False).encode(),mtime=0))
    (ROOT/'results/ablation_rows.csv.gz').write_bytes(gzip.compress(pd.DataFrame(ablation).to_csv(index=False).encode(),mtime=0))
    (ROOT/'data/generated/mutation_manifest.jsonl.gz').write_bytes(gzip.compress(''.join(json.dumps(r)+'\n' for r in manifest).encode(),mtime=0))
    metrics=['asset_word','asset_char','asset_tfidf','paired_word','paired_char','transition']
    summary=[];intervals=[]
    for (game,op),g in frame[frame.eligible].groupby(['game','operation']):
        for metric in metrics:
            vals=(g[metric]>1e-10).groupby(g.context_id).mean().to_numpy();r=np.random.default_rng(20261115)
            boots=np.array([r.choice(vals,len(vals),replace=True).mean() for _ in range(2000)])
            summary.append({'game':game,'operation':op,'metric':metric,'rows':len(g),'contexts':len(vals),'nonzero_rate':float(vals.mean()),'ci_low':float(np.quantile(boots,.025)),'ci_high':float(np.quantile(boots,.975)),'mean_distance':g[metric].mean()})
    pd.DataFrame(summary).to_csv(ROOT/'results/detection_summary.csv',index=False)
    frame[frame.eligible].groupby(['game','operation','dose'])[['transition','outcome_loss','retention']].mean().reset_index().to_csv(ROOT/'results/dose_summary.csv',index=False)
    pd.DataFrame(ablation).assign(detected=lambda d:d.distance>1e-10).groupby(['game','operation','representation']).detected.mean().reset_index().to_csv(ROOT/'results/ablation_summary.csv',index=False)
    # Positive equivalence checks, modality audit and noisy labels are reported separately.
    modality=[];noise=[]
    for c in contexts:
        n=len(c['edges']);modality.append({'game':c['game'],'context_id':c['context_id'],'options':n,'wordless_responses':sum(not words(e['text']) for e in c['edges']),'full_outcomes':len({e['outcome'] for e in c['edges']}),'text_outcomes':len({e['text'] for e in c['edges']}),'state_outcomes':len({consequence(e,'state') for e in c['edges']}),'terminal_outcomes':len({e['terminal'] for e in c['edges']})})
        for rate in [0,.1,.25,.5]:
            for seed in range(100):
                v=copy.deepcopy(c['edges']);r=random.Random(int(hashlib.sha256(f"{c['context_id']}:{seed}".encode()).hexdigest()[:16],16))
                for e in v:
                    if r.random()<rate:e['outcome']='erroneous_'+e['outcome']
                noise.append({'game':c['game'],'context_id':c['context_id'],'rate':rate,'seed':seed,'false_distance':jaccard(transitions(c['edges']),transitions(v))})
    pd.DataFrame(modality).to_csv(ROOT/'results/modality.csv',index=False)
    (ROOT/'results/label_noise.csv.gz').write_bytes(gzip.compress(pd.DataFrame(noise).to_csv(index=False).encode(),mtime=0))
    facts={'contexts':len(contexts),'edges':sum(len(c['edges']) for c in contexts),'attempted_rows':len(frame),'eligible_rows':int(frame.eligible.sum()),'excluded_noop_rows':int((~frame.eligible).sum()),'eligible_structural_rows':int((frame.eligible&frame.changed).sum()),'negative_control_rows':int(frame.operation.isin(['identity','typography','duplicate','reorder']).sum())}
    (ROOT/'results/facts.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))

if __name__=='__main__':main()
