import unittest,sys,copy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.metrics import *
from scripts.run_experiments import mutate
def fixture():
 return {'edges':[{'id':str(i),'outcome':str(i),'text':f'Outcome {i}','action_text':f'Action {i}','delta':{},'next_actions':[],'terminal':True} for i in range(3)]}
class MeasurementTests(unittest.TestCase):
 def test_jaccard_boundaries(self):
  self.assertEqual(jaccard([],[]),0);self.assertEqual(jaccard([1],[2]),1);self.assertAlmostEqual(jaccard([1,2],[2,3]),2/3)
 def test_alias_duplication_invariance(self):
  c=fixture();v,_=mutate(c,'duplicate',1,0);self.assertEqual(jaccard(transitions(c['edges']),transitions(v)),0);self.assertEqual(len(v),6)
 def test_permutation_is_not_breadth_loss(self):
  c=fixture();v,_=mutate(c,'permute',1,0);self.assertEqual(jaccard(transitions(c['edges']),transitions(v)),1);self.assertEqual(relative_loss([e['outcome'] for e in c['edges']],[e['outcome'] for e in v]),0)
 def test_drop_has_direction(self):
  self.assertAlmostEqual(relative_loss(['a','b'],['a']),.5);self.assertEqual(relative_loss(['a'],['a','b']),-1)
 def test_missing_action_penalty(self):
  c=fixture();self.assertAlmostEqual(paired_response(c['edges'],c['edges'][:2],words),1/3)
 def test_emoji_word_failure_is_visible(self):
  self.assertEqual(words('😸'),set());self.assertEqual(jaccard(words('😸'),words('😿')),0);self.assertEqual(jaccard(grams('😸'),grams('😿')),1)
 def test_no_source_mutation(self):
  c=fixture();old=copy.deepcopy(c);mutate(c,'collapse',1,4);self.assertEqual(c,old)
 def test_extracted_integrity(self):
  root=Path(__file__).resolve().parents[1]
  for game in ['emoji','the_intercept']:
   cs=json.loads((root/f'data/processed/{game}.contexts.json').read_text())
   self.assertEqual(len({c['context_id'] for c in cs}),len(cs))
   for c in cs:
    self.assertGreaterEqual(len(c['edges']),2);self.assertEqual(len({e['id'] for e in c['edges']}),len(c['edges']))
 def test_permutation_at_every_seed_preserves_support(self):
  c=fixture()
  for seed in range(100):
   v,_=mutate(c,'permute',.5,seed);self.assertEqual({e['outcome'] for e in c['edges']},{e['outcome'] for e in v})
if __name__=='__main__':unittest.main()
