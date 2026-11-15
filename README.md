# Narrative Novelty Benchmark

**A reproducible computational study of measurement failure modes in novelty-loss benchmarks for human–AI game narrative authoring.**

Repository: https://github.com/AssylbekGizatov/narrative-novelty-benchmark

Author: Gizatov Assylbek, Kh. Dosmukhamedov Atyrau University. Research draft, 15 November 2026.

This repository contains a completed instrument audit, not a human-authoring trial. No LLM treatment effect or player-perceived originality has been measured. The source games belong to inkle and Pat Scott; the present contribution is the extraction, experimental design, analysis and measurement critique.

## Main deliverables

- `paper/Novelty_Benchmark_DiGRA.docx` and `.pdf`: editable and rendered manuscript, maximum ten pages including references.
- `paper/Novelty_Benchmark_DiGRA_Anonymous.docx` and `.pdf`: anonymous review copies.
- `paper/manuscript.md`: source manuscript with equations, figures and author–date references.
- `paper/conference_abstract.txt`: separate 150–300-word regional conference abstract.
- `notebooks/`: three **executed** Jupyter notebooks, including outputs and interpretation.
- `docs/`: protocol, adversarial audit, data card, future human-authoring protocol, source appraisal and submission requirements.
- `scripts/` and `src/`: runtime extractor, deterministic interventions, metrics, uncertainty summaries, stress tests and document builders.
- `data/`: pinned MIT-licensed original scripts, runtime saves, compiled stories and complete mutation manifests.
- `results/`: every attempted case, eligibility flags, exclusions, summaries, simulations and replay verification.

## Executed study

| Quantity | Value |
|---|---:|
| Source games | 2 |
| Seeded simulated playthroughs | 400 |
| Retained branching contexts | 234 |
| Exactly replayed local transitions | 679 |
| Attempted variants | 11,466 |
| Nontrivial structural cases | 9,341 |
| Prespecified controls | 936 |
| Flagged no-op structural attempts | 1,189 |

Key result: pairing a textual response with its action detects the tested prose edits; an inventory of written assets does not. Word tokenization erases the emoji-based modality; character comparison recovers almost all detections. Assignment distance is not breadth loss. Additional tests expose alignment error, exact-path saturation and false observed loss from incomplete sampling.

Perfect detection by aligned-pair Jaccard is a definitional check, **not** proof of originality measurement. See the adversarial audit before quoting a score.

## Reproduce

Python 3.12 and Node.js 20+ are recommended. From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm ci
make all
```

The pinned raw files are included; `python scripts/fetch_sources.py` can refetch and checksum them. `make all` executes extraction, experiments, tests, exact replay, plots, notebooks and Word generation. Pandoc is needed only for Word generation. The PDFs can be recreated with LibreOffice:

```bash
libreoffice --headless --convert-to pdf --outdir paper paper/Novelty_Benchmark_DiGRA.docx
libreoffice --headless --convert-to pdf --outdir paper paper/Novelty_Benchmark_DiGRA_Anonymous.docx
```

To inspect the existing results without rerunning the corpus, open the executed notebooks. The main scripts require no API key, paid model, login or external service after dependency installation.

For hosts that block local Jupyter sockets, run `python scripts/build_notebooks.py --in-process`. This executes the same Python cells with IPython rich-display capture; this mode produced the checked-in outputs. Large row-level CSV/JSONL files use lossless gzip; pandas reads `.csv.gz` directly. Decompressed hashes are recorded in `results/compression_integrity.json`.

## Data and interpretation

Original raw scripts and derived narrative text remain under their upstream MIT notice in `licenses/ink-library-MIT.txt`. Preserve attribution. Code and new methodological documentation are released under the repository MIT licence. No paid paper PDFs or private datasets are redistributed. The research provenance and limitations are documented; working notes should not be mistaken for independent peer review.

The regional CFP currently specifies an abstract first. The international DiGRA track's 5,000–7,000-word requirement is separate; the compact ten-page manuscript follows the user's page limit and the DiGRA layout, not a claim of automatic compliance with every DiGRA track.
