#!/bin/sh
pylint --rcfile pylintrc mbed_greentea -f parseable heroku -r n > pylint.log || exit 0