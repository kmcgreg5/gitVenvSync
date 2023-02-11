#!/bin/bash
script_dir=$(dirname "$0")

if [ $script_dir = '.' ]
then
script_dir=$(pwd)
fi

if [ -d "$script_dir/penv" ]; then
    source "$script_dir/penv/bin/activate"
    python "$script_dir/main.py" "$@"
    deactivate
else
    python3 "$script_dir/main.py" "$@"
fi
