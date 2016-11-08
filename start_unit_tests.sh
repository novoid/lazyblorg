#!/bin/sh

## this script calls each unit test script
## if no error is found, the final success statement is shown
## if error occurs, this script stops at the error


cd lib/tests && \
./orgparser_test.sh && \
./utils_test.sh && \
./htmlizer_test.sh && \
./pypandoc_test.sh && \
cd ../../tests && \
./lazyblorg_test.sh && \
cd .. && \
echo "\n           All Python unit tests ended successfully :-)\n"

#end
