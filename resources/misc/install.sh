#!/bin/bash
# A simple shell script for installing & configuring
# the project at https://github.com/MojiRiAnt/tyi-server

echo "NOTE: The script is going to import project here!"

read -p "Does current working directory suit you? (y/n) " ANSWER

if [[ $ANSWER != "y" ]] && [[ $ANSWER != "Y" ]]
then
    exit 1
fi


echo -e "\e[5mPreparing your virtual environment...\e[0m"

python3 -m venv tyi-server-env
source tyi-server-env/bin/activate

EXPECTED_ENV=$(pwd)"/tyi-server-env"

if [[ $VIRTUAL_ENV == $EXPECTED_ENV ]]
then
    echo -ne "\e[1A\e[K\r\e[1;92mEnvironment prepared successfully!\e[0m\n"
else
    echo -ne "\e[1;31mThere was an error while entering the virtual environment.\e[0m\n"
    deactivate
    rm -Rf tyi-server-env
    exit 1
fi

cd tyi-server-env
git clone https://github.com/MojiRiAnt/tyi-server.git

pip3 install -r resources/misc/requirements.txt

echo ""
echo -e "\e[1;92mScript finished successfully!\e[0m"
echo -e "\e[1mNOTE: To remove the project, simply remove the tyi-server-env directory.\e[0m"
