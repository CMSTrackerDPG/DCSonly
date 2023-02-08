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

parser.add_argument('-o','--output', dest='outfile', type=str, action='store', default='lsinfo_DCSONLY_cosmics.txt', help='Input run & LS info json file')

args = parser.parse_args()
headers = {"content-type": "application/x-www-form-urlencoded"}

def getls(runNumber, dataset, outDict):
    #runregistry.get_lumisection_ranges
    print("runregistry.get_lumisection_ranges(%s, %s)" % (runNumber, args.dataset))
    lsrange = runregistry.get_lumisection_ranges(runNumber, args.dataset)
    print(lsrange)
    print(run)
    outDict[runNumber] = lsrange

with open(args.infile) as f:
  data = json.load(f)
try:
    with open(args.outfile) as f:
        datadone = json.load(f)
        print(datadone.keys())
except:
    datadone={}

lsinfo={}
#Completed Runs List
print("Generating completed runs list...")
allruns=list(data.keys())
print("runregistry.get_datasets(filter={'run_number':{'and':[{'>=': %s},{'<=': %s}]},'dataset_name':{'=': %s},'tracker_state': {'=': 'COMPLETED'}})" % (min(allruns),max(allruns), args.dataset)) 
ddata=runregistry.get_datasets(filter={'run_number':{'and':[{'>=':min(allruns)},{'<=': max(allruns)}]},'dataset_name':{'=': args.dataset},'tracker_state': {'=': "COMPLETED"}})
completedRuns=[]
for r in ddata:
    completedRuns.append(r['run_number'])
print(completedRuns)
print("Total completed runs : %d" % len(completedRuns))

for run in data.keys():
    if int(run) in completedRuns:
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
    else:
        print("Run %s not COMPLETED" % run)
