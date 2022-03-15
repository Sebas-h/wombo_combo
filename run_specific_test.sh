#!/bin/bash

testfile=$(ls tests/test_* | fzf)
echo Test file: $testfile
test ! -z "$testfile" \
    && python \
        -m green \
        --verbose --verbose \
        --failfast \
        "$testfile"
