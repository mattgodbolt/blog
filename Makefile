default: dist

.PHONY: venv
venv:
	python3 -mvenv venv

venv/.requirements: requirements.txt | venv
	venv/bin/pip install -r requirements.txt
	touch venv/.requirements

.PHONY: deps
deps: venv venv/.requirements
.PHONY: dist
dist: deps
	./publish.sh

.PHONY: serve
serve: deps
	(cd pygen && ../venv/bin/python ./main.py)
	./venv/bin/python ./serve.py
