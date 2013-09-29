#!/bin/bash

# Real Python executables to use
PYVER=2.7
PYTHON=/Library/Frameworks/Python.framework/Versions/$PYVER/bin/python$PYVER

# Figure out the root of your EPD env
ENV=`$PYTHON -c "import os; print os.path.abspath(os.path.join(os.path.dirname(\"$0\"), '..'))"`

# Run Python with your env set as Python's PYTHONHOME
export PYTHONHOME=$ENV
exec $PYTHON "$@"

# Give it executable permission and use it to launch your wxPython app instead of the python executable.
# Source: http://stackoverflow.com/questions/10386600/wxpython-2-9-on-mac-os-x