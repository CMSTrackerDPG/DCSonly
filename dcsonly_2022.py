#!/usr/bin/python3
import requests
import json
import os
import sys
import runregistry
import urllib
import argparse
from termcolor import colored

# OMS API secret code
CLIENT_SECRET="ask for secret code! alessandro.rossi@cern.ch"


# Suppress InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.exceptions import ConnectionError
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Extract runs list filtering with DCS informations.',prog='DCSonly')
parser.add_argument('-c','--class', dest='rclass', type=str, action='store', default='Cosmics22',
                    help='Run Class for which the run list will be created')
parser.add_argument('-m','--min', dest='minrun', type=int, action='store',default=342000,
                    help='Minimum run number to be included in the list')
parser.add_argument('-M','--max', dest='maxrun', type=int, action='store',default=999999,
                    help='Maximum run number to be included in the list')
parser.add_argument('-f','--fill', dest='fill', action='store_true',
                    help='Produce Fill List file for HDQM')

args = parser.parse_args()
headers = {"content-type": "application/x-www-form-urlencoded"}

def exchange_tokens(token):
    data = {
        "client_id": "dcsonly",
        "client_secret": CLIENT_SECRET,
        "audience": "cmsoms-prod",
        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
        "subject_token": token,
    }
    data = requests.post(
        url="https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/token",
        data=data,
        headers=headers,
    )

    try:
        data_ = data.json()
        access_token = data_["access_token"]
        expires_in = data_["expires_in"]
        return {"access_token": access_token, "expires_in": expires_in}

    except Exception as e:
        return "Error: " + str(e)



def get_token():
    data = {
        "client_id": "dcsonly",
        "client_secret": CLIENT_SECRET,
        "audience": "cmsoms-prod",
        "grant_type": "client_credentials",
    }

    data = requests.post(
        url="https://auth.cern.ch/auth/realms/cern/protocol/openid-connect/token",
        data=data,
        headers=headers,
    )
    try:
        data_ = json.loads(data.text)
        access_token = data_["access_token"]
        data_access_token_and_expires_in = exchange_tokens(access_token)

        def get_expires_in_value():
            return data_access_token_and_expires_in["expires_in"]

        def get_access_token_value():
            return data_access_token_and_expires_in["access_token"]

        data_access_token = get_access_token_value()
        return data_access_token

    except Exception as e:
        print(str(e))
        return "Error: " + str(e)

def dcsonly(rclass,minrun,maxrun=999999):
    print("Fetching run list from RR...")
    rr_runs = runregistry.get_runs(
        filter={
            'run_number': {
                'and':[
                    {'>': minrun},
                    {'<': maxrun}
                ]
            },
            'class': {
                'like': rclass+'%'
            }
        }
    )
    runList=[]
    for r in rr_runs:
        runList.append(int(r['run_number']))
    runList.sort()
    print(runList)
    print("...Done!")
    #Strips Mode
    print("Fetching mode list from DB...")
    link = " http://ebutz.web.cern.ch/ebutz/cgi-bin/getReadOutmodeMulti.pl?FIRSTRUN=" + str(minrun) + "&LASTRUN=" + str(maxrun)
    f = urllib.request.urlopen(link)
    json_data = f.read()
    dblist = json.loads(json_data)
    print("...Done!")

    token=get_token()
    headers = {"Authorization": "Bearer %s" % (token)}
    print("Total run : %d" % len(runList))
    output={}
    outputD={}
    outputP={}
    for i in runList:
        url=("https://cmsoms.cern.ch/agg/api/v1/lumisections?filter[run_number][eq]=%s&fields=bpix_ready,fpix_ready,tibtid_ready,tecm_ready,tecp_ready,tob_ready&page[limit]=9999" % i)
        data=requests.get(url,headers=headers,verify=False).json()
        partitions=["bpix-","bpix+","fpix-","fpix+","tibtid","tob","tec-","tec+"]
        fedin={}
        color=['red','green']
        if len(data["data"])>=1:
            url=("https://cmsoms.cern.ch/agg/api/v1/daqreadouts?filter[run_number][eq]=%s" % i)
            daq=requests.get(url,headers=headers,verify=False).json()
            for idx in range(len(dblist)) :
                if( dblist[idx][0] == str(i) ) :
                    dbmode = dblist[idx][1]
                    break
            for subd in daq["data"]:
                if subd["attributes"]["partition"] in partitions:
                    fedin[subd["attributes"]["partition"]]=100*len(subd["attributes"]["feds_included"])/(len(subd["attributes"]["feds_excluded"])+len(subd["attributes"]["feds_included"]))
                    #print("%s -> %f" % (subd["attributes"]["partition"],fedin[subd["attributes"]["partition"]]))
                for pp in list(set(partitions) - set(fedin.keys())):
                    fedin[pp]=0
            bpix_ls=[]
            fpix_ls=[]
            tibtid_ls=[]
            tob_ls=[]
            tecm_ls=[]
            tecp_ls=[]
            for lsinfo in data["data"]:
                bpix_ls.append(lsinfo["attributes"]["bpix_ready"])
                fpix_ls.append(lsinfo["attributes"]["fpix_ready"])
                tibtid_ls.append(lsinfo["attributes"]["tibtid_ready"])
                tob_ls.append(lsinfo["attributes"]["tob_ready"])
                tecm_ls.append(lsinfo["attributes"]["tecm_ready"])
                tecp_ls.append(lsinfo["attributes"]["tecp_ready"])
            bpix=any(bpix_ls)
            fpix=any(fpix_ls)
            tibtid=any(tibtid_ls)
            tob=any(tob_ls)
            tecm=any(tecm_ls)
            tecp=any(tecp_ls)
            print("Run %d - Mode %s" % (i,dbmode))
            print("\tDCS:\tBPix:"+colored("%s" % bpix,color[bpix])+"\t\t\tFPix:"+colored("%s" % fpix,color[fpix])+"\t\t\tTIB/TID:"+colored("%s" % tibtid,color[tibtid])+"\tTOB:"+colored("%s" % tob,color[tob])+"\tTEC-:"+colored("%s" % tecm,color[tecm])+"\tTEC+:"+colored("%s" % tecp,color[tecp]))
            print("\tDAQ:\tBPix-:%.1f%%\tBPix+:%.1f%%\tFPix-:%.1f%%\tFPix+:%.1f%%\tTIB/TID:%.1f%%\tTOB:%.1f%%\tTEC-:%.1f%%\tTEC+:%.1f%%" % (fedin["bpix-"],fedin["bpix+"],fedin["fpix-"],fedin["fpix+"],fedin["tibtid"],fedin["tob"],fedin["tec-"],fedin["tec+"]))
            if "Cosmics" in rclass :
                if tibtid and tob and tecm and tecp:
#                    if all(i >=80 for i in list(fedin.values())[2:]):
                    output.setdefault(i,{"StripMode":dbmode,"readyFlags":[bpix,fpix,tibtid,tob,tecm,tecp],"FEDin":list(fedin.values())})
                    if dbmode=="DECO":
                        outputD.setdefault(i,{"StripMode":dbmode,"readyFlags":[bpix,fpix,tibtid,tob,tecm,tecp],"FEDin":list(fedin.values())})
                    if dbmode=="PEAK":
                        outputP.setdefault(i,{"StripMode":dbmode,"readyFlags":[bpix,fpix,tibtid,tob,tecm,tecp],"FEDin":list(fedin.values())})                 
            else:
                if bpix and fpix and tibtid and tob and tecm and tecp:
#                    if all(i >=80 for i in fedin.values()):
                    output.setdefault(i,{"StripMode":dbmode,"readyFlags":[bpix,fpix,tibtid,tob,tecm,tecp],"FEDin":list(fedin.values())})
                    if dbmode=="DECO":
                        outputD.setdefault(i,{"StripMode":dbmode,"readyFlags":[bpix,fpix,tibtid,tob,tecm,tecp],"FEDin":list(fedin.values())})
                    if dbmode=="PEAK":
                        outputP.setdefault(i,{"StripMode":dbmode,"readyFlags":[bpix,fpix,tibtid,tob,tecm,tecp],"FEDin":list(fedin.values())})
    if "Cosmics" in rclass :
        filename = "json_DCSONLY_cosmics.txt"
        filenameD = "json_DCSONLY_cosmics_DECO.txt"
        filenameP = "json_DCSONLY_cosmics_PEAK.txt"
    else:    
        filename = "json_DCSONLY.txt"
        filenameD = "json_DCSONLY_DECO.txt"
        filenameP = "json_DCSONLY_PEAK.txt"
    outfile = open('./'+filename, 'w')
    json.dump(output, outfile, indent=2, sort_keys=True)
    print("Total Selected runs : %d" % len(output.keys()))
    outfile = open('./'+filenameD, 'w')
    json.dump(outputD, outfile, indent=2, sort_keys=True)
    print("Total Selected DECO mode runs : %d" % len(outputD.keys()))
    outfile = open('./'+filenameP, 'w')
    json.dump(outputP, outfile, indent=2, sort_keys=True)
    print("Total Selected PEAK mode runs : %d" % len(outputP.keys()))


def FillList(rclass):
    lst = []
    if "Cosmics" in rclass :
        input_file =open('json_DCSONLY_cosmics.txt','r')
        json_outfile = "Run_LHCFill_RunDuration_Cosmics.json"
        cosmics=True
    else :
        input_file =open('json_DCSONLY.txt','r')
        json_outfile = "Run_LHCFill_RunDuration.json"
        cosmics=False
      
          
    rlist = json.load(input_file)
    token=get_token()
    headers = {"Authorization": "Bearer %s" % (token)}      
    print("Getting run duration info........")
    print(len(rlist.keys()))
    for idx,key in enumerate(rlist.keys()):
        url=("https://cmsoms.cern.ch/agg/api/v1/runs?filter[run_number][eq]=%s&fields=fill_number,duration" % key)
        data=requests.get(url,headers=headers,verify=False).json()
        lhcfill=data["data"][0]["attributes"]["fill_number"]
        dur=data["data"][0]["attributes"]["duration"]
        if idx%100==0 :
            print("{0} - Run = {1} - Fill {2} - Dur. {3}".format(idx,key,lhcfill,dur))
        d={}
        d['run']=key
        d['lhcfill']=lhcfill
        d['rundur']=dur
        lst.append(d)
        
    lst=sorted(lst,key=lambda x:x['run']) 
    obj ={}
    obj[json_outfile]=lst		

    outfile=open(json_outfile, 'w')
    json.dump(obj, outfile,indent=4)
    print(".....done! Output on {0}".format(json_outfile))
    
######
dcsonly(args.rclass,args.minrun,args.maxrun)
if args.fill :
    FillList(args.rclass)
