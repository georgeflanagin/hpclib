function bp
{
    command pushd $HOME/bpcli > /dev/null
    python bp.py $@
    command popd > /dev/null
}
