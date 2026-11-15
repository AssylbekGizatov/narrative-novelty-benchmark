from pathlib import Path
import pandas as pd,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'savefig.bbox':'tight'})
d=pd.read_csv(ROOT/'results/detection_summary.csv')
fig,axs=plt.subplots(1,2,figsize=(8,2.9),sharey=True)
for ax,(game,title) in zip(axs,[('the_intercept','The Intercept'),('emoji','LD41 Emoji')]):
 sub=d[(d.game==game)&d.operation.isin(['collapse','permute'])]
 keys=['asset_word','paired_word','paired_char','transition'];names=['Asset\nwords','Paired\nwords','Paired\nchars','Aligned\npairs']
 for offset,op,color in [(-.17,'collapse','#205f85'),(.17,'permute','#d47c24')]:
  ss=sub[sub.operation==op].set_index('metric').loc[keys]
  ax.bar(np.arange(4)+offset,ss.nonzero_rate*100,width=.32,label=op.capitalize(),color=color)
  ax.errorbar(np.arange(4)+offset,ss.nonzero_rate*100,yerr=np.maximum(0,np.vstack([ss.nonzero_rate-ss.ci_low,ss.ci_high-ss.nonzero_rate])*100),fmt='none',color='#222',capsize=2)
 ax.set_xticks(range(4),names);ax.set_title(title);ax.set_ylim(0,110);ax.grid(axis='y',alpha=.18)
axs[0].set_ylabel('Mean change-detection rate (%)');axs[1].legend(loc='upper left',fontsize=8)
fig.tight_layout();fig.savefig(ROOT/'figures/detection.png',dpi=220);fig.savefig(ROOT/'figures/detection.pdf');plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(8,2.8))
p=pd.read_csv(ROOT/'results/path_saturation.csv')
for col,label,c in [('path_distance','Whole path','#b34344'),('transition_distance','Local transitions','#205f85'),('endpoint_distance','Endpoint','#4c7953')]:axs[0].plot(p.length,p[col],'o-',label=label,color=c,markersize=3)
axs[0].set_xscale('log',base=2);axs[0].set_xlabel('Chain length');axs[0].set_ylabel('Distance after one state edit');axs[0].legend(fontsize=7);axs[0].grid(alpha=.15)
s=pd.read_csv(ROOT/'results/coverage_simulation.csv')
for prob,label in [(1/64,'Rare outcome p = 1/64'),(1/256,'Rare outcome p = 1/256')]:
 a=s[s.rare_probability==prob];axs[1].plot(a.rollouts,a.false_directional_loss_rate*100,'o-',label=label,markersize=3)
axs[1].set_xscale('log',base=2);axs[1].set_xlabel('Rollouts per version');axs[1].set_ylabel('False directional loss (%)');axs[1].legend(fontsize=7);axs[1].grid(alpha=.15)
fig.tight_layout();fig.savefig(ROOT/'figures/robustness.png',dpi=220);fig.savefig(ROOT/'figures/robustness.pdf');plt.close(fig)
print('Two reproducible figures generated.')
