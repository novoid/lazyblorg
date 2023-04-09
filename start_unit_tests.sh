#!/bin/sh -e

## this script calls each unit test script
## if no error is found, the final success statement is shown
## if error occurs, this script stops at the error

## activate Python3 virtualenv:
test ! -d venv || . ./venv/bin/activate

(
set -e
cd lib/tests
./orgparser_test.sh
./utils_test.sh
./htmlizer_test.sh
./pypandoc_test.sh
cd ../../tests
./lazyblorg_test.sh
)
echo "\n           All Python unit tests ended successfully :-)\n"

#end
