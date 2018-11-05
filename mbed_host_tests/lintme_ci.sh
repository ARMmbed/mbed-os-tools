#!/bin/sh
pylint --rcfile pylintrc -f parseable -r n mbed_host_tests > pylint.log || exit 0
