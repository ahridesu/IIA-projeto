#!/bin/bash

# kill all terminals, except the one this is running
kill $(pgrep bash)

activate_venv() {
	source venv/bin/activate
}

export -f activate_venv

VENV=""

if [ $# -eq 0 ]
then
    echo $'Running without Python Virtual Environment...\n'
else
	if [ $1 = 'venv' ]
	then
		VENV="activate_venv;"
		activate_venv
	fi
fi

gnome-terminal --tab --title="SOKOBAN SERVER" -- bash -c "${VENV}pip3 -V;echo ""; python3 server.py"
gnome-terminal --tab --title="SOKOBAN VIEWER" -- bash -c "${VENV}pip3 -V;echo ""; python3 viewer.py"

# check if xdotool is installed
if ! command -v xdotool &> /dev/null;
then
	echo $'Couldn\'t return focus to first tab because xdtool missing.\nPlease consider installing it with:\n$ sudo apt install xdotool\n'
else
	# change back to first tab
	xdotool key alt+1
fi

pip3 -V
echo ""
python3 student.py