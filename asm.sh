#!/bin/bash
python3 bfhla_asm.py < "$1" # > "${1%.*}.bfhla"
