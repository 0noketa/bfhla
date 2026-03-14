#!/bin/bash

python3 ../bfhla_disasm.py < "$1" > "$1.0.bfhla"
if [ "$2" == "-nooptimize" ]; then
    python3 ../bfhla_asm.py -tbf < "$1.0.bfhla" > "$1.0.out"
else
    python3 ../bfhla_asm.py -tbf < "$1.0.bfhla" | python3 ../bf_optimize.py > "$1.0.out"
fi

python3 ../bfhla_disasm.py < "$1.0.out" > "$1.1.bfhla"
if [ "$2" == "-nooptimize" ]; then
    python3 ../bfhla_asm.py -tbf < "$1.1.bfhla" > "$1.1.out"
else
    python3 ../bfhla_asm.py -tbf < "$1.1.bfhla" | python3 ../bf_optimize.py > "$1.1.out"
fi

if cmp "$1.0.out" "$1.1.out"; then
    echo "ok"
else
    echo "error"
fi
