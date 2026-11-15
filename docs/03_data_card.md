# Data card

## Provenance and rights
Original author-created games: inkle, The Intercept; Pat Scott, LD41 Emoji (the source displays an alarm-clock title). Both source scripts are distributed in inkle/ink-library under MIT. Exact upstream commit, source paths, SHA-256 hashes and byte lengths are in data/source_manifest.json. Preserve licenses/ink-library-MIT.txt when redistributing source or derived text. The scripts, analyses and paper in this project are new; the source narratives are not.

## Units and production
400 programmatic playthroughs; 200 per game. These are simulated uniform-choice agents, not humans. Seed 1000 + run index initializes both narrative random state and a separate policy RNG. Horizon 120 choices. Reservoir seed 731 selects at most 120 distinct eligible saved states per game, without replacement from the encountered-state stream. Identity hashes remove the top-level storySeed and previousRandom fields but retain gameplay histories. This is convenience sampling of reachable contexts, not complete coverage of either game.

Preserved state snapshots allow exact runtime replay. At every retained branching state, every available action is executed until the next choice or termination. Contexts with any logged runtime issue are excluded. We do not silently repair original scripts. A failed walkthrough may still contribute an earlier valid local context; later failure does not invalidate the already executed local transition.

## Schema
context_id: SHA-256 of serialized state with the two RNG fields removed; game: corpus ID; run/step: discovery location; context: latest rendered passage; state: complete Ink save JSON; edges: enumerated actions.

Each edge stores id (compiled source location), index, action_text, text (rendered successor), delta (changed global variables), next_actions (next offered source locations), terminal, and outcome (SHA-256 of those successor observables). outcome is an operational identity, NOT an expert semantic label. Compiled action locations align existing versions of one narrative; they do not align unrelated stories.

## Derived data
mutation_manifest.jsonl.gz contains reversible/reconstructible operation specifications. Changed successors are assigned in extracted records, not recompiled as complete altered games. Rows share contexts and source games. Structural eligibility excludes no-op assignments; all attempted rows are retained with an eligibility field. No external language-model generations, participant surveys or creativity ratings are included.

## Known limitations
Only two games, one narrative engine, convenience source selection, short local horizon, non-human action policy, latent history loss in the observable signature, and no validation of perceived originality. Unicode word tokenization removes emoji symbols; this is measured rather than hidden. The reference alignment is an explicit dependency. Frozen labels under text edits are an oracle convention, not a discovered capability of a semantic parser.

## Splits
No train/test split is asserted because no model is trained or selected. Report per-game results. In downstream model development, split by entire story or author, never randomly by perturbation row.
