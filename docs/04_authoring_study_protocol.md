# Human–AI authoring validation protocol

Status: prepared instrument, NOT executed and NOT ethics approval.

## Research question
Does a defined AI-assistance workflow change individual narrative originality, collective plot diversity, or consequence diversity relative to unaided writing, under matched budgets?

Use human-only, idea-assistance, and draft/revision-assistance conditions; keep any model-only condition separate. Randomize within genre/experience blocks. Fix time, maximum word budget, allowable game assets, interface and choice budget. Log initial author concept, prompts, model version and settings, proposals, accept/reject decisions, edits, timestamps, and executable game versions. Do not infer co-authorship from finished prose or AI detectors.

## Outcomes and validation
Primary dimensions must be declared before data collection. Blind expert raters assess originality relative to a declared reference corpus, not a model's confidence. Players assess perceived agency and meaningfulness. Rate narrative coherence, enjoyment, cultural specificity and author control separately. Retain expressive choices even when endpoints coincide. A smaller game can be more original; do not optimise the study to reward branch quantity.

Two independently trained annotators align state, intent and consequence descriptions across versions. Record disagreements and a chance-corrected agreement statistic appropriate to the coding task; adjudicate with a documented procedure. Keep raw labels and pre-adjudication scores. Never use the same LLM as both sole generator and sole evaluator.

## Statistical plan
Use pilot variance and the smallest practically meaningful effect to set sample size. No numerical power or participant count is claimed before those quantities are justified. The unit of randomization is the author or author-task assignment; repeated choices are nested data. Estimate signed changes separately by dimension. Use author/task-level randomization inference or a justified hierarchical model; do not count thousands of perturbations as independent participants. Report uncertainty, missingness, model/version moderators, and zero or positive AI effects.

## Ethics and access
Obtain applicable institutional review and informed consent before recruitment; specify AI use, recording, retention, withdrawal and licensing. Do not release participant identity, chat histories or proprietary game scripts without authorization. This repository has no approval, recruitment or completed consent records.

## Logging schema
session_id, anonymized_author_id, assignment_id, condition, model_id, model_version, timestamp, event_type, proposal_id, accepted, source_span, resulting_span, game_commit, annotation_version.

The completed computational study establishes instrument failure modes; it does not replace this validation stage.
