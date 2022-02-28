#!/bin/bash

testfn=$(cat tests/test_* | awk '/def test_/ {print $2}' | sed 's/(.*$//' | cut -c 6- | fzf)

echo Test fn: $testfn

test ! -z "$testfn" \
    && python \
        -m green \
        --verbose --verbose \
        --failfast \
        tests/test*.py -n "*$testfn"

