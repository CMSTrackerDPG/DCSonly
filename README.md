# DCSonly

Script to extract the list of runs of a specified Class type and within a run numbe range. 

### Setup

Run `source setenv.sh` in order to install all the needed python packages and setup the needed enviromental variables.  
In order to interact with RunRegitry usercert.pem and userkey.pem files need to be correctly set on either ./globus or private/ dir.

### OMS API

In order to fetch information from OMS a secret code needs to be added MANUALLY inside the code ([line 12](https://github.com/arossi83/DCSonly/blob/main/dcsonly_2022.py#L12)).  
Please send a request to : cms-trk-dqm-conveners@cern.ch

### Use

The script need 3 option:
* -c, --class : Run Class Type
* -m, --min : Minimum Run Number
* -M, --max : Maximum Run Number

The maximum run number is not mandatory. 

Example: `./dcsonly_2021.py -c Cosmics21 -m 342682`.  
if the previous gives an error try with : `python3 dcsonly_2021.py -c Cosmics21 -m 342682`
