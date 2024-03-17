default: dist

PYTHON=$(CURDIR)/.venv/bin/python

.PHONY: venv
venv:
	python3 -mvenv .venv

.venv/.requirements: requirements.txt | venv
	.venv/bin/pip install -r requirements.txt
	touch .venv/.requirements

.PHONY: deps
deps: venv .venv/.requirements

.PHONY: update
update: deps
	mkdir -p www/feed
	(cd pygen && ${PYTHON} ./main.py)

.PHONY: publish
publish: update
	./publish.sh

.PHONY: serve
serve: update
	${PYTHON} ./serve.py
