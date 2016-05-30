#!/bin/bash

# full path to the python interpretor
export PYTHON="/work/zope/bin/python"

# path to ZOPE_HOME/lib/python
export SOFTWARE_HOME="/work/zope/zope272/lib/python"

# path to your instance. Don't set it if you aren't having  instance
export INSTANCE_HOME="/work/zopefarm/272"

${PYTHON} run_tests.py