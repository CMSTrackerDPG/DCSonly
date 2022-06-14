#!/usr/bin/env python3
import json
import argparse
parser = argparse.ArgumentParser(description='Prepare the final json',prog='DCSonly')
parser.add_argument('-i','--inputfile', dest='infile', type=str, action='store', default='lsinfo_DCSONLY_cosmics.txt', help='file with lsinfo for runs')

parser.add_argument('-o','--output', dest='outfile', type=str, action='store', default='craftGOODwithALLON.json', help='final output json file')

parser.add_argument('--checkPixel', dest='cPix', action='store_true', default=False)

args = parser.parse_args()

print(args.cPix)

with open(args.infile) as f:
  data = json.load(f)

runJson={}
for run, lsinfo in data.items():
    print(run)
#    print(lsinfo)
    runJson[run]=[]
    if len(lsinfo)!=0: 
      print("processing...")
      for infokey in lsinfo:
        if infokey == 'err' : continue
        if not 'start' in infokey.keys() : continue
        if not 'end' in infokey.keys() : continue
        if not 'tracker-strip' in infokey.keys() : continue
        if not 'tracker-pixel' in infokey.keys() : continue
        if not 'tracker-track' in infokey.keys() : continue
        if args.cPix:
          if (infokey['tracker-strip']['status']!="GOOD")  or (infokey['tracker-track']['status']!="GOOD") or (infokey['tracker-pixel']['status']!="GOOD"): 
            print("Run %s BAD" % run)
            continue
        else:
          if (infokey['tracker-strip']['status']!="GOOD")  or (infokey['tracker-track']['status']!="GOOD"): 
            print("Run %s BAD" % run)
            continue

        lsblock=[]
        lsblock.append(infokey['start'])
        lsblock.append(infokey['end'])
        runJson[run].append(lsblock)
      else:
        print("Run %s empty" % run) 

finalRuns={}
count=0
for run, lsv in runJson.items():
  if len(lsv) == 0 : continue
  finalRuns[run]=lsv
  count+=1
#print(runJson)
with open(args.outfile, 'w') as json_file:
  json.dump(finalRuns, json_file, indent=4)

print("Total runs:" + str(count))
