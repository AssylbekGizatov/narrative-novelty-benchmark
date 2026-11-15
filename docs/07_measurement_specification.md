# Measurement specification and reading guide

The experimental unit is a saved, executable decision context. An intervention changes its extracted successor records. It does not produce a new coherent whole game.

## Representations

For context s and action a, c(s,a) is a SHA-256 identity of the tuple (rendered response, changed global variables, sorted next-action source paths, terminal status). It is an observable signature, not an embedding or an expert semantic label. For a fixed source version, actions align through compiled source locations.

T_s = {(a, c(s,a)) : a in A_s}; C_s = {c(s,a) : a in A_s}.

| Measure | Definition | Interpretation and edge cases |
|---|---|---|
| Aligned-transition distance | 1 − intersection(T,T′) / union(T,T′) | Assignment change; zero for two empty sets. Eligible game contexts are nonempty. |
| Transition retention | intersection(T,T′) / size(T) | Fraction of reference assignments retained; implementation returns one for an empty reference. |
| Signed breadth loss | 1 − size(C′) / size(C) | Reduction in the represented consequence support. Can be negative for expansion. Implementation returns zero for an empty reference, which is outside this dataset's estimand. |
| Asset word distance | Jaccard over lowercased Unicode alphanumeric word sets | Ignores routing and word order; emoji-only text yields empty sets. |
| Asset character distance | Jaccard over whitespace-normalised character trigram sets | Preserves case and Unicode symbols. A nonempty string shorter than three characters contributes itself. |
| Asset TF-IDF distance | 1 − cosine of count × IDF vectors | Smoothed IDF fitted only to original inventories; both empty vectors return zero distance. |
| Paired response distance | Mean response Jaccard over original action IDs | Missing original actions receive distance one; new-only actions do not add a term. Therefore this is directional and not a complete symmetric edit distance. |
| Option-count change | number of displayed edited records − original records | Aliases can increase this without adding unique assignments or consequences. |

## Intervention contract

- Identity preserves everything.
- Typography modifies displayed strings but carries forward the reference action and consequence identities. Invariance therefore uses known labels; it does not demonstrate automatic paraphrase recognition.
- Duplicate copies each existing edge with the same aligned identity. This models display aliases, not genuinely different game actions.
- Reorder changes only order. Order can matter aesthetically; the set metrics intentionally discard it.
- Drop removes selected actions while keeping at least one. Removed narrative assets remain in the frozen inventory baseline.
- Collapse redirects selected actions to one existing successor record.
- Permute cycles selected successor records among actions. Consequence cardinality is preserved even when assignments change.

Drop/collapse/permute use nominal doses 0.25, 0.5 and 1.0 and five seeds. The realized intervention can be coarse because contexts have small option counts. Identity, typography, duplicate and reorder contribute one case per context. Complete manifests preserve realized indices and before/after records. Structural attempts with unchanged aligned pair sets are marked no-op and excluded from sensitivity summaries, but remain in raw rows.

## Estimands and uncertainty

Main detection rate: for a game and operation, first average the indicator distance > 1e−10 across eligible variants within each context, then average those context means. Bootstrap intervals resample contexts 2,000 times. They are descriptive stability bands for the selected corpus, not a confidence interval over game developers or a causal treatment effect.

Ablation summaries instead average mutation rows. This is explicitly a different weighting scheme. The paper identifies this difference; use the same weighting before making a numerical head-to-head comparison.

Annotation noise uses context-specific replicate seeds shared across rates (common random numbers) with 100 replicates at each rate. Counterexamples and Monte Carlo outcomes are separate procedural data, never pooled into the two-game sample.

## Identifiability limits

The instrument cannot infer individual creative intent, whole-game coherence, long-horizon semantic equivalence, collective homogenisation across unrelated works, or the causal effect of AI assistance. Those require additional data. It can expose whether a measurement implementation reacts to known local changes and whether its numerical interpretation survives controlled counterexamples.
