"""Aligned-version measurement primitives. None is an originality score."""
import re, math, json
from collections import Counter

def words(text):
    return set(re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE))

def grams(text, n=3):
    text=' '.join(text.split())
    return {text[i:i+n] for i in range(max(0,len(text)-n+1))} or ({text} if text else set())

def jaccard(a,b):
    a,b=set(a),set(b)
    return 1-len(a&b)/len(a|b) if a|b else 0.0

def transitions(edges):
    return {(e['id'],e['outcome']) for e in edges}

def retention(a,b):
    return len(set(a)&set(b))/len(set(a)) if a else 1.0

def relative_loss(a,b):
    return 1-len(set(b))/len(set(a)) if a else 0.0

def paired_response(a,b,tokenizer):
    old={e['id']:e for e in a};new={e['id']:e for e in b}
    return sum(1 if key not in new else jaccard(tokenizer(e['text']),tokenizer(new[key]['text'])) for key,e in old.items())/len(old)

def cosine_distance(a,b,idf):
    ca=Counter(re.findall(r"[^\W_]+",a.lower()));cb=Counter(re.findall(r"[^\W_]+",b.lower()))
    va={k:v*idf.get(k,1) for k,v in ca.items()};vb={k:v*idf.get(k,1) for k,v in cb.items()}
    na=math.sqrt(sum(v*v for v in va.values()));nb=math.sqrt(sum(v*v for v in vb.values()))
    if not na or not nb:return 0.0 if not na and not nb else 1.0
    return max(0.0,1-sum(v*vb.get(k,0) for k,v in va.items())/(na*nb))

def profile(context,variant,base_assets,variant_assets,idf):
    a,b=context['edges'],variant;ta,tb=transitions(a),transitions(b)
    return dict(asset_word=jaccard(words(base_assets),words(variant_assets)),
      asset_char=jaccard(grams(base_assets),grams(variant_assets)),
      asset_tfidf=cosine_distance(base_assets,variant_assets,idf),
      paired_word=paired_response(a,b,words),paired_char=paired_response(a,b,grams),
      transition=jaccard(ta,tb),retention=retention(ta,tb),
      outcome_loss=relative_loss({e['outcome'] for e in a},{e['outcome'] for e in b}),
      option_count_change=len(b)-len(a))

def consequence(edge,mode):
    if mode=='full':return edge['outcome']
    if mode=='text':return edge['text']
    if mode=='state':return json.dumps([edge['delta'],sorted(edge['next_actions']),edge['terminal']],sort_keys=True)
    if mode=='terminal':return str(edge['terminal'])
    raise ValueError(mode)
