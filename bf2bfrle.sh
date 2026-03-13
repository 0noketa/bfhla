#!/bin/bash

if [ "$2" == "--prefix" ]; then
    python3 bf_optimize.py -tbfrlep < "$1" > "$1.bfrle"
else
    python3 bf_optimize.py -tbfrle < "$1"  > "$1.bfrle"
fi
