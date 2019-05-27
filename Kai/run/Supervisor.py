#!/usr/bin/env python
from __future__ import print_function, division
import os
import sys
import time
import argparse
import subprocess
import pprint
from collections import OrderedDict
from ruamel.yaml import YAML
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='Supervisor handles submission and bookkeeping for physics samples.')
parser.add_argument('--check_events', dest='check_events', action='store_true',
                    help='check that the number of events in source files match those in the sample card')
parser.add_argument('--local_run', dest='local_run', action='store_true',
                    help='run locally')
parser.add_argument('--crab_run', dest='crab_run', action='store_true',
                    help='run with crab')
parser.add_argument('--percent_run', dest='percent_run', action='append', type=int,
                    help='percent (as an integer) of each sample to process')
parser.add_argument('--sample_card', dest='sample_cards', action='append', type=str,
                    help='path and name of the sample card(s) to be used')
parser.add_argument('--stagesource', dest='stagesource', action='append', type=int, default='0',
                    help='Stage of data storage from which to begin supervisor actions, such as stagesource: 0 which is the unprocessed and centrally maintained data/MC')
parser.add_argument('--redir', dest='redir', action='append', type=str, default='root://cms-xrd-global.cern.ch/',
                    help='redirector for XRootD, such as "root://cms-xrd-global.cern.ch/"')

def main():
    args = parser.parse_args()
    if args.local_run and args.crab_run:
        print("Both local_run and crab_run have been set to True; this is not supported. Exiting")
        sys.exit()
    username = 'nmangane'
    # args = parser.parse_args('--check_events --sample_card sampletest.yml'.split())
    print("Supervisor will check integrity of sample card's event counts: " + str(args.check_events))
    print("Supervisor will run samples locally: " + str(args.local_run))
    print("Supervisor will run samples on CRAB: " + str(args.crab_run))
    print("The path and name of the sample cards(s) are: ")
    SampleList = []
    yaml = YAML() #default roundtrip type
    for scard in args.sample_cards:
        print("\t" + scard)
        with open(scard) as sample:
            SampleList += yaml.load(sample)
    
    for samplenumber, sample in enumerate(SampleList):
        if samplenumber > 0: continue
        dataset = sample['dataset']
        sampleName = dataset['name']
        isData = dataset['isData']
        nEvents = dataset['nEvents']
        print(sample['stagesource'])
        inputDataset = sample['stagesource'][args.stagesource]
        # inputDataset = dataset['inputDataset']
    
        crab_cfg = sample['crab_cfg']
    
        postprocessor = sample['postprocessor']
    
        #write out the filelist to personal space in /tmp, if check_events or local_run is true, then use these to run
        if args.check_events or args.local_run:
            query='--query="file dataset=' + inputDataset + '"'
            tmpFileLoc = '/tmp/{0:s}/sample_{1:d}_fileList.txt'.format(username, samplenumber)
            cmd = 'dasgoclient ' + query + ' > ' + tmpFileLoc
            os.system(cmd)
        
        #Load the filelist names including redirector
        fileList = []
        with open(tmpFileLoc, "r") as rawFileList:
            for line in rawFileList:
                tempName = args.redir + line
                tempName = tempName.rstrip()
                fileList.append(tempName)
    
        if args.check_events:
            if isData == False:
                events_in_files = 0
                for fileName in fileList:
                    f = ROOT.TFile.Open(fileName, 'r')
                    tree = f.Get('Runs')
                    for en in xrange(tree.GetEntries()):
                        tree.GetEntry(en)
                        events_in_files += tree.genEventCount
                if events_in_files != nEvents:
                    print("Mismatch in dataset {0}: nEvents = {1:d}, events_in_files = {2:d}".format(sampleName, nEvents, events_in_files))
                else:
                    print("Integrity check successful for dataset {0}: {1:d}/{2:d} events".format(sampleName, events_in_files, nEvents))
            else:
                print("Skipping dataset {0} for check_events integrity, as it is marked isData".format(sampleName))
        






if __name__ == '__main__':
    main()
