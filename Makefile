#############################################################################
##                MAKEFILE FOR LINTING AND RUNNING TESTS OF METRICS        ##
#############################################################################


###############
## VARIABLES ##
###############


# The name of the package to build.
PACKAGE_NAME = crillab-metrics

MODULE_NAME = metrics

DOCKER_ORGANIZATION = thibaultfalque

# The version of the package to build.

VERSION = 1.0.4


# The directory of the unit tests for the package to build.
TESTS = tests


# The directory where to put build files.
OUTDIR = build


#############
## TARGETS ##
#############


# Declares non-file targets.
.PHONY: test pylint sonar register package upload clean help


##################
## Test Targets ##
##################


# Executes unit tests with code coverage.
test: $(OUTDIR)/nosetests.xml $(OUTDIR)/coverage.xml


# Stores unit tests and code coverage results into files.
$(OUTDIR)/nosetests.xml $(OUTDIR)/coverage.xml: $(OUTDIR) $(MODULE_NAME)/*.py $(TESTS)/*/test*.py
	nosetests --with-xunit --with-coverage --cover-package $(MODULE_NAME) --cover-xml $(TESTS)/*/test*.py
	mv nosetests.xml .coverage coverage.xml $(OUTDIR)


#####################
## Linting Targets ##
#####################


# Executes the Pylint static analysis.
pylint: $(OUTDIR)/pylint.out


# Stores the result of the Pylint analysis into a file.
$(OUTDIR)/pylint.out: $(OUTDIR) $(MODULE_NAME)/*.py $(TESTS)/*/*.py
	pylint $(MODULE_NAME) $(TESTS) -r n --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" | tee $(OUTDIR)/pylint.out


# Executes the SonarQube static analysis.
sonar: test pylint
	if test -z "$$SONAR_ORGA"; then sonar-scanner -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONAR_TOKEN} -Dsonar.projectKey=${SONAR_KEY};else sonar-scanner -Dsonar.host.url=${SONAR_HOST} -Dsonar.login=${SONAR_TOKEN} -Dsonar.projectKey=${SONAR_KEY} -Dsonar.organization=${SONAR_ORGA}; fi
	


##################
## PyPI Targets ##
##################


# Registers the project on PyPI.
register:
	python3 setup.py register


# Packages the project to upload it on PyPI.
package: dist/$(PACKAGE_NAME)-$(VERSION).tar.gz


# Packages the project into a gzipped-tarball archive.
dist/$(PACKAGE_NAME)-$(VERSION).tar.gz:
	python3 setup.py sdist


# Uploads the project on PyPI.
upload:
	twine upload dist/*

deploy: clean package upload

####################
## Docker Targets ##
####################

docker-build:
	docker build -t $(DOCKER_ORGANIZATION)/$(MODULE_NAME):latest .
docker-push:
	docker push $(DOCKER_ORGANIZATION)/$(MODULE_NAME):latest

#####################
## Utility Targets ##
#####################


# Creates the directory where to put build files.
$(OUTDIR):
	mkdir $(OUTDIR)


# Deletes the build files.
clean:
	rm -rf $(OUTDIR) *.egg *.egg-info dist


# Displays a message describing the available targets.
help:
	@echo
	@echo "Linting and Running Tests of Metrics"
	@echo "===================================="
	@echo
	@echo "Available targets are:"
	@echo "    - test (default)  -> executes unit tests with code coverage"
	@echo "    - pylint          -> executes the Pylint static analysis"
	@echo "    - sonar           -> executes the SonarQube static analysis"
	@echo "    - register        -> registers the project on PyPI"
	@echo "    - package         -> packages the project to upload it on PyPI"
	@echo "    - upload          -> uploads the project on PyPI"
	@echo "    - clean           -> deletes the build files"
	@echo "    - help            -> displays this message"
	@echo
