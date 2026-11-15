from pathlib import Path
import argparse, ast, sys
import nbformat as nbf
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--in-process',action='store_true',help='Execute Python cells with IPython display capture, without a kernel socket.')
args=parser.parse_args()
def execute_in_process(nb):
 from IPython.core.interactiveshell import InteractiveShell
 from IPython.utils.capture import capture_output
 from IPython.display import display
 shell=InteractiveShell.instance()
 shell.reset(new_session=True)
 namespace=shell.user_ns
 count=0
 for cell in nb.cells:
  if cell.cell_type!='code':continue
  count+=1
  tree=ast.parse(cell.source,filename=f'notebook-cell-{count}')
  last=tree.body.pop() if tree.body and isinstance(tree.body[-1],ast.Expr) else None
  with capture_output() as captured:
   exec(compile(tree,f'notebook-cell-{count}','exec'),namespace)
   if last is not None:
    value=eval(compile(ast.Expression(last.value),f'notebook-cell-{count}','eval'),namespace)
    if value is not None:display(value)
  outputs=[]
  if captured.stdout:outputs.append(nbf.v4.new_output('stream',name='stdout',text=captured.stdout))
  if captured.stderr:outputs.append(nbf.v4.new_output('stream',name='stderr',text=captured.stderr))
  outputs.extend(nbf.v4.new_output('display_data',data=o.data,metadata=o.metadata) for o in captured.outputs)
  cell.outputs=outputs;cell.execution_count=count
 nb.metadata['execution_method']='In-process Python AST execution with IPython rich display capture; no Jupyter socket.'
def md(s):return nbf.v4.new_markdown_cell(s)
def code(s):return nbf.v4.new_code_cell(s)
setup="""from pathlib import Path
import json, sys
import pandas as pd
ROOT = Path.cwd()
if not (ROOT / 'data').exists(): ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
from src.metrics import *
"""
books={
'01_corpus_and_runtime.ipynb':[
md('# Corpus and runtime audit\n\nTwo existing MIT-licensed games, simulated playthroughs, no human participants. Read provenance before interpreting sample sizes. All cells below were executed.'),code(setup),
code("manifest = json.loads((ROOT/'data/source_manifest.json').read_text())\npd.DataFrame(manifest['files'])"),
code("summary = pd.read_json(ROOT/'data/processed/extraction_summary.json')\nsummary[['game','runs','eligible_states','retained_states','extracted_edges','error_runs','truncated']]"),
md('## One observed decision\nThe context and responses are creator-authored source material. Outcome IDs encode an observable proxy; they are not independent human semantic annotations.'),
code("contexts = json.loads((ROOT/'data/processed/the_intercept.contexts.json').read_text())\nc = contexts[0]\nprint(c['context'])\npd.DataFrame(c['edges'])[['action_text','text','delta','terminal']]"),
code("import subprocess\nr = subprocess.run(['node','scripts/verify_replay.cjs'],cwd=ROOT,text=True,capture_output=True,check=True)\nprint(r.stdout)"),
md('### Interpretation\nA valid local context can precede an error later in the full playthrough. Invalid immediate successors are excluded and logged. These states do not constitute independent games or writers.')],
'02_metrics_and_results.ipynb':[
md('# Compare observation units and modalities\n\nRecompute one case, then inspect all precomputed experimental rows. Counts of variants are not participant sample sizes.'),code(setup),
code("from scripts.run_experiments import mutate, assets\nc = json.loads((ROOT/'data/processed/the_intercept.contexts.json').read_text())[0]\nv, _ = mutate(c, 'collapse', 1.0, 0)\npd.Series(profile(c,v,assets(c),assets(c),{}))"),
code("rows=pd.read_csv(ROOT/'results/metric_rows.csv.gz')\nfacts=json.loads((ROOT/'results/facts.json').read_text())\nassert len(rows)==facts['attempted_rows']\npd.Series(facts)"),
code("d=pd.read_csv(ROOT/'results/detection_summary.csv')\nd.pivot_table(index=['game','operation'],columns='metric',values='nonzero_rate').round(4)"),
md('### Challenge the claim\nThe paired word baseline detects the tested prose edits. The inventory baseline is blind by design. Perfect aligned-pair sensitivity follows mathematically from the eligibility definition. None is an originality classification accuracy.'),
code("from IPython.display import Image, display\ndisplay(Image(filename=str(ROOT/'figures/detection.png')))"),
code("perm=rows[(rows.operation=='permute') & rows.eligible]\nassert perm.outcome_loss.abs().max()<1e-12\nperm.groupby('game')[['transition','outcome_loss']].mean()")],
'03_counterexamples_and_robustness.ipynb':[
md('# Adversarial checks\n\nThese are explicitly procedural counterexamples and Monte Carlo simulations, reported separately from the two-game corpus.'),code(setup),
code("chains=pd.read_csv(ROOT/'results/path_saturation.csv')\nassert ((chains.transition_distance-4/(chains.length+2)).abs()<1e-12).all()\nchains"),
code("sampling=pd.read_csv(ROOT/'results/coverage_simulation.csv')\nsampling[sampling.rare_probability==1/64]"),
code("noise=pd.read_csv(ROOT/'results/label_noise.csv.gz')\nnoise.groupby(['game','rate']).false_distance.mean()"),
code("pd.read_csv(ROOT/'results/ablation_summary.csv').pivot_table(index=['game','operation'],columns='representation',values='detected')"),
code("from IPython.display import Image, display\ndisplay(Image(filename=str(ROOT/'figures/robustness.png')))"),
md('### Limits\nAn unchanged game can show apparent loss under incomplete sampling. Frozen labels can conceal semantic errors. A one-step signature cannot establish long-horizon possibility, perceived agency, originality, or an AI treatment effect.')]
}
for name,cells in books.items():
 nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':sys.version.split()[0]}})
 if args.in_process:execute_in_process(nb)
 else:NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
 (ROOT/'notebooks').mkdir(exist_ok=True)
 nbf.write(nb,ROOT/'notebooks'/name);print('Executed',name)
