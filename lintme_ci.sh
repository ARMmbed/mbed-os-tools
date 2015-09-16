#!/bin/sh
pylint --rcfile pylintrc -f parseable -r n mbed_greentea > pylint.log || exit 0
