#!/bin/bash

source ../bin/activate

if [[ $1 == "--load-db" ]]
then
    echo -e "\e[1;37mLaunching XLV.Seven server…"
    echo -e "Press Ctrl+C to shut it down!\e[0;37m"
    python3 main.py --load-db
elif [[ $1 == "--nodrop" ]]
then
    echo -e "\e[1;37mLaunching XLV.Seven server without dropping database…"
    echo -e "Press Ctrl+C to shut it down!\e[0;37m"
    python3 main.py --nodrop
elif [[ $1 == "" ]]
then
    echo -e "\e[1;37mLaunching XLV.Seven server with empty database…"
    echo -e "Press Ctrl+C to shut it down!\e[0;37m"
    python3 main.py
fi
