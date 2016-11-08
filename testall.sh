#!/bin/sh

## this script calls each unit test script
## if no error is found, the final success statement is shown
## if error occurs, this script stops at the error

./start_unit_tests.sh && start_end-to-end-test.sh && \
echo "\n\n           All tests ended successfully! :-)\n\n"

#end
