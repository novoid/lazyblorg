#!/usr/bin/env sh
## this script calls each unit test script
## if no error is found, the final success statement is shown
## if error occurs, this script stops at the error

uv --project . run pytest && \
echo "\n           All Python unit tests ended successfully :-)\n"

#end
