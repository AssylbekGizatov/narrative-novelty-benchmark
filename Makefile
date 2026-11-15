.PHONY: install data experiments verify figures notebooks paper all
install:
	npm ci
	python -m pip install -r requirements.txt
data:
	node scripts/extract_ink.cjs
experiments:
	python scripts/run_experiments.py
	python scripts/stress_tests.py
verify:
	python -m unittest discover -s tests -v
	node scripts/verify_replay.cjs
figures:
	python scripts/make_figures.py
notebooks:
	python scripts/build_notebooks.py
paper:
	python scripts/build_paper.py
all: data experiments verify figures notebooks paper
