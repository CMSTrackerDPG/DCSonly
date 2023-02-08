#!/usr/bin/python3
import json
import os
import sys
import runregistry
import urllib
import argparse
from termcolor import colored

parser = argparse.ArgumentParser(description='Extract runs list filtering with DCS informations.',prog='DCSonly')
parser.add_argument('-d','--dataset', dest='dataset', type=str, action='store', default='/PromptReco/Cosmics21/DQM',
                    help='Dataset Name')
parser.add_argument('-i','--inputdata', dest='infile', type=str, action='store', default='json_DCSONLY_cosmics.txt', help='Input run info json produced from dcsonly script')

parser.add_argument('-o','--output', dest='outfile', type=str, action='store', default='completed_DCSONLY_cosmics.txt', help='Input run & LS info json file')

args = parser.parse_args()
headers = {"content-type": "application/x-www-form-urlencoded"}

def getState(minrun, maxrun, outDict):
    #runregistry.get_lumisection_ranges
    #dd= runregistry.get_dataset(runNumber,args.dataset)
    #print("Run %s state : %s" % (runNumber,dd["dataset_attributes"]["tracker_state"]))
    #if dd["dataset_attributes"]["tracker_state"] == "COMPLETED":
    print("runregistry.get_datasets(filter={'run_number':{and':[{'>=':%s},{'<=': %s}]},'dataset_name':{'=': %s}})" % (minrun,maxrun,args.dataset))
    lsrange = runregistry.get_lumisection_ranges(runNumber, args.dataset)
    print(lsrange)
    print(run)
    outDict[runNumber] = lsrange
    #else:
    #    print("Run %s NOT COMPLETED" % runNumber)

with open(args.infile) as f:
  data = json.load(f)
try:
    with open(args.outfile) as f:
        datadone = json.load(f)
        print(datadone.keys())
except:
    datadone={}

lsinfo={}

for run in data.keys():
    if run not in datadone.keys():
        done=False
        while(not done):
            try:
                getls(run, args.dataset, lsinfo)
            except:
                done=False
            else:
                done=True
    else:
        lsinfo[run]=datadone[run]
        print("%s already done" % run)
    with open(args.outfile, 'w') as json_file:
        json.dump(lsinfo, json_file)
