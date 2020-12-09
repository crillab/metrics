# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
MDDIR         = md
RSTDIR        = .
BUILDDIR      = build

MDFILES     = $(shell ls $(MDDIR)/*.md)
RSTFILES    = $(subst $(MDDIR),$(RSTDIR),$(patsubst %.md,%.rst,$(MDFILES)))

PANDOCOPTIONS = --lua-filter raw-rst.lua

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(RSTDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile html

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
html: Makefile $(RSTFILES) 
	@$(SPHINXBUILD) -M $@ "$(RSTDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

$(RSTDIR):
	mkdir -p $(RSTDIR)
	cp conf.py $(RSTDIR)

$(RSTDIR)/%.rst: $(MDDIR)/%.md $(RSTDIR)
	pandoc $(PANDOCOPTIONS) --output $@ $<

