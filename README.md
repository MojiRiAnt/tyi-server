# TYI-2018 Back-End Server

This is an API Server for TYI-2018 Project. It handles the café system & answers HTTP queries.

## Technologies used

* Language: Python3
* Framework: Flask

## Installation guide

Installing our project is as simple as follows:
```console
$ cd ~/Downloads  # navigate to your Downloads directory
$ wget https://raw.githubusercontent.com/MojiRiAnt/tyi-server/master/resources/misc/install.sh
 # download our installation script
$ cd ~/your/import/directory  # navigate to where you want
$ bash ~/Downloads/install.sh  # execute the script
```

Some more useful commands:
```console
$ source ~/your/import/directory/tyi-server-env/bin/activate # enter our environment
$ python3 ~/your/import/directory/tyi-server-env/tyi-server/main.py # run our project
$ deactivate # exit our environment
```

## Project structure

|   File  |      Purpose      |
|:-------:|:-----------------:|
| main.py | The main app file |

## Codestyle rules

Code is divided in parts with the following format:
```
#======[SECTION NAME]====== » SECTION STATUS (TO BE DONE / IN DEVELOPMENT / READY TO GO)

the actual code with 1 line before & 1 line after

```

The important bits of code which should be revised later are marked with 'WARNING' as follows:
```
some code here # WARNING : some notes (optional)
```

