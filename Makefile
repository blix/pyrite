PYTHON=python

local:
	$(PYTHON) setup.py version
	$(PYTHON) setup.py build_ext -i
	$(PYTHON) setup.py build_py -c -d .

clean:
	-$(PYTHON) setup.py clean --all # ignore errors of this command
	find . -name '*.py[cdo]' -exec rm '{}' ';'
	rm -f MANIFEST pyrite/__version__.py

install:
	$(PYTHON) setup.py version
	$(PYTHON) setup.py install

install-home:
	$(PYTHON) setup.py version
	$(PYTHON) setup.py install --home="$(HOME)" --force

test: local
	(cd test && $(PYTHON) TestSuite.py)
