script_dir=$(dirname "$0")

if [ $script_dir = '.' ]
then
script_dir=$(pwd)
fi

source "$script_dir/penv/bin/activate"
python gitVenvSync.py "$@"
deactivate