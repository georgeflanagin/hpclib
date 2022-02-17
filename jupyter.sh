# export __author__='George Flanagin'
# export __copyright__='Copyright 2022'
# export __version__=1.0
# export __maintainer__='George Flanagin'
# export __email__='gflanagin@richmond.edu'
# export __status__='preliminary'
# export __license__='MIT'

jupyter()
{
    if [[ "$1" == "-?" ]]; then
        echo "Usage: jupyter"
        echo "  Runs a jupyter instance on a compute node of Spydur."
        echo "  The output of this program is a URL that you copy"
        echo "  to your browser to connect to your Jupyter Notebook."
        return
    fi

    # Pick a suitably high port, and see if it is busy. Keep going
    # until we find one that is not busy.
    export localport=${1:-10200}
    while true; do
        netstat -ant | grep -q $localport
        if [ ! $? ]; then
            break
        else
            localport=$(( localport+1 ))
        fi
    done

    # This echo is for entertainment purposes only.
    echo "Using local port $localport"

    export destport=$localport
    echo "We will connect $localport on this computer to $destport on Spydur."
    export me=$(whoami)
    
    # Fill out the salloc command with appropriate values. In this config, 
    # it gives you two hours. 
    cmd="salloc --account $me -p basic --nodes=1 --mem=10 --ntasks=2 --time=2:00:00 --no-shell > salloc.txt 2>&1"

    # Get a slice of a node. 
    ssh "$me@spydur" "$cmd" 

    # Determine the ID of the job that owns the slice of the node.
    scp "$me@spydur:~/salloc.txt" .
    # The job ID is the last field in the first line.
    export slurm_jobid=$(cat salloc.txt | head -1 | awk '{print $NF}')

    # Now do something similar to determine which node in the
    # cluster owns the job. The first line is a header (who cares?)
    # and the second line (last line) is the node.
    cmd="squeue -o %N -j $slurm_jobid | tail -1 > squeue.txt"
    echo "Ready to execute $cmd"

    ssh "$me@spydur" "$cmd" 2>/dev/null
    echo "done."
    echo "retrieving squeue.txt"
    scp "$me@spydur:~/squeue.txt" .
    export jnode=$(cat squeue.txt | head -1) 

    # Print the data.
    echo "SLURM_JOBID is $slurm_jobid"
    echo "The node is $jnode"

    #############################################
    # Now we have the allocation we need, and we know the job number, and it is
    # time to create the command to run on spydur. 
    #   cmd1 -- start the notebook on the compute node
    #   cmd2 -- write the name of the most recent notebook file to jinfo.txt
    #   cmd3 -- get the file with that info, and bring it to the head node.
    #############################################
    jupyter_cmd1="ssh $me@$jnode \"nohup /usr/local/sw/anaconda/anaconda3/bin/jupyter notebook --no-browser 1>/dev/null 2>&1 &\""
    jupyter_cmd2="ssh $me@$jnode \"ls -rt /home/gflanagi/.local/share/jupyter/runtime/*html | tail -1 > ~/jinfo.txt\""
    jupyter_cmd3="scp $me@$jnode:~/jinfo.txt ."
    echo $jupyter_cmd1  > j.sh 
    echo $jupyter_cmd2 >> j.sh
    echo $jupyter_cmd3 >> j.sh

    # Remember ... it needs to be executable.
    chmod 700 j.sh
    # Move it to Spydur
    scp j.sh "$me@spydur:~/jupyter.sh"
    # Execute it.
    ssh $me@spydur "./jupyter.sh"
    # Now go get that file and bring it here.
    scp $me@spydur:~/jinfo.txt .
    # put the name of the file into an environment variable.
    export f=$(cat jinfo.txt)

    # Repeat the above steps between Spydur and the allocated compute node.
    echo "scp $me@$jnode:$f ." > j.sh
    chmod 700 j.sh
    scp j.sh $me@spydur:~/j.sh
    ssh $me@spydur "j.sh"
    
    # Now we copy the file back from the headnode
    scp "$me@spydur:$f" .

    #######
    # Put the line that has the port number and token in an environment variable.
    # It will be something that looks like this:
    #    window.location.href = "http://localhost:8892/tree?token=d55ff......52ac5e4";
    # We need the URL that is in quotes.
    #######
    # The file is in *this* directory, so we are done with the directory
    # part of the name.
    #######
    export f=$(basename $f)
    # Find the line.
    location=$(cat $f | grep window.location | awk '{print $NF}')
    # use our friend sed, the only editor anyone really needs.
    token=$(echo $location | sed 's/^.*=//' | sed 's/";$//')
    jport=$(echo $location | sed 's/^.*localhost://' | sed 's!/.*$!!') 

    # Now create the tunnel and tell the user what to do. Note that the tunnel
    # is placed in the background; otherwise the script just sits here ....
    remote_tunnel="ssh -L $destport:localhost:$jport -N $me@$jnode"
    ssh -L "$localport:localhost:$destport" "$me@spydur" $remote_tunnel &

    # We are done.
    echo Tunnel spec ::: ssh -L "$localport:localhost:$destport" "$me@spydur" $remote_tunnel 
    echo "point your browser to "
    echo "http://localhost:$localport/tree?token=$token"
}


