#!/bin/sh
pylint --rcfile pylintrc -f parseable -r n mbed_lstools > pylint.log || exit 0
