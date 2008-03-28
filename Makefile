PYTHON=python

local:
	$(PYTHON) setup.py build_ext -i
	$(PYTHON) setup.py build_py -c -d .

build:
	$(PYTHON) setup.py build

clean:
	-$(PYTHON) setup.py clean --all # ignore errors of this command
	find . -name '*.py[cdo]' -exec rm '{}' ';'
	rm -f MANIFEST pyrite/__version__.py

install: build
	$(PYTHON) setup.py install

install-home: build
	$(PYTHON) setup.py install --home="$(HOME)" --force
