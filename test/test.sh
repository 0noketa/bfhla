#!/bin/bash

for i in *.bf; do
    ./check_broken_output.sh $i
done
