default: dist

venv:
	python3 -mvenv venv

venv/.requirements: requirements.txt | venv
	venv/bin/pip install -r requirements.txt
	touch venv/.requirements

deps: venv venv/.requirements
dist: deps
	./publish.sh
.PHONY: dist deps

