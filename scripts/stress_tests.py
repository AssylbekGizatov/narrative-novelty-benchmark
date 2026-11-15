"""Analytic counterexamples and explicitly synthetic sampling simulations."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.metrics import jaccard
ROOT=Path(__file__).resolve().parents[1]
def main():
    rows=[]
    # In a chain, a single relabelled intermediate consequence changes two
    # adjacent transitions. Entire-path equality saturates at distance one.
    for length in [4,8,16,32,64,128]:
        nodes=[f's{i}' for i in range(length+1)];edited=nodes.copy();edited[length//2]='altered_state'
        old={(nodes[i],'continue',nodes[i+1]) for i in range(length)}
        new={(edited[i],'continue',edited[i+1]) for i in range(length)}
        rows.append({'family':'chain','length':length,'transition_distance':jaccard(old,new),'path_distance':jaccard({tuple(nodes)},{tuple(edited)}),'endpoint_distance':jaccard({nodes[-1]},{edited[-1]})})
    pd.DataFrame(rows).to_csv(ROOT/'results/path_saturation.csv',index=False)
    # Delayed differences are hidden at any observation horizon before delay.
    delay=[]
    for depth in [2,4,8,16,32]:
        for horizon in [1,2,4,8,16,32]:
            a=['shared']*(depth-1)+['outcome_A'];b=['shared']*(depth-1)+['outcome_B']
            delay.append({'delay':depth,'horizon':horizon,'detected':int(a[:horizon]!=b[:horizon])})
    pd.DataFrame(delay).to_csv(ROOT/'results/delayed_consequences.csv',index=False)
    # Two independent rollouts of an identical two-ending game can disagree
    # about support. Estimate false loss and nondirectional difference separately.
    rng=np.random.default_rng(20261115);sampling=[]
    for p in [1/2,1/8,1/64,1/256]:
        for n in [16,64,256,1024]:
            a=rng.binomial(n,p,10000);b=rng.binomial(n,p,10000)
            sa=(a>0).astype(int)+(a<n).astype(int);sb=(b>0).astype(int)+(b<n).astype(int)
            q=(1-p)**n
            sampling.append({'rare_probability':p,'rollouts':n,'replicates':10000,'rare_miss_rate':float((a==0).mean()),'exact_rare_miss':q,'false_directional_loss_rate':float((sa>sb).mean()),'false_support_difference_rate':float((sa!=sb).mean())})
    pd.DataFrame(sampling).to_csv(ROOT/'results/coverage_simulation.csv',index=False)
    (ROOT/'data/generated/procedural_specs.json').write_text(json.dumps({'chains':[4,8,16,32,64,128],'delays':[2,4,8,16,32],'horizons':[1,2,4,8,16,32],'rare_probabilities':[.5,.125,.015625,.00390625],'rollouts':[16,64,256,1024],'replicates_per_condition':10000,'seed':20261115},indent=2))
    print('6 chain counterexamples, 30 delay/horizon conditions, 16 sampling conditions executed.')
if __name__=='__main__':main()
