#!/usr/bin/env python
from __future__ import print_function, division
import os
import sys
import time, datetime
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
                    help='percent (as an integer) of each sample to process for local_run')
parser.add_argument('--stage', dest='stage', action='store', type=str,
                    help='analysis stage to be produced')
parser.add_argument('--stagesource', dest='stagesource', action='store', type=str, default='0',
                    help='Stage of data storage from which to begin supervisor actions, such as stagesource: 0 which is the unprocessed and centrally maintained data/MC')
parser.add_argument('--sample_card', dest='sample_cards', action='append', type=str,
                    help='path and name of the sample card(s) to be used')
parser.add_argument('--redir', dest='redir', action='append', type=str, default='root://cms-xrd-global.cern.ch/',
                    help='redirector for XRootD, such as "root://cms-xrd-global.cern.ch/"')

def main():
    args = parser.parse_args()
    username = 'nmangane'
    if args.local_run and args.crab_run:
        print("Both local_run and crab_run have been set to True; this is not supported. Exiting")
        sys.exit()
    # args = parser.parse_args('--check_events --sample_card sampletest.yml'.split())
    print("Supervisor will check integrity of sample card's event counts: " + str(args.check_events))
    print("Supervisor will run samples locally: " + str(args.local_run))
    print("Supervisor will run samples on CRAB: " + str(args.crab_run))
    if args.crab_run:
        print("Supervisor will run create crab configurations for stage {0:s} using stagesource {1:s}".format(args.stage, args.stagesource))
    print("The path and name of the sample cards(s) are: ")
    SampleList = []
    yaml = YAML() #default roundtrip type
    for scard in args.sample_cards:
        print("\t" + scard)
        with open(scard) as sample:
            SampleList += yaml.load(sample)

    #Generate crab and local folder name using the current time, outside the sample loop
    dt = datetime.datetime.now()
    runFolder = "{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    if args.crab_run:
        runFolder = "crab_" + runFolder
        print("Creating directory {0:s} for crab configurations and scripts".format(runFolder))
        if not os.path.exists(runFolder):
            os.makedirs(runFolder)
        else:
            print("runfolder '{0:s}' already exists. Rename or delete it and attempt resubmission".format(runFolder))
            sys.exit()

    if args.local_run:
        runFolder = "local_" + runFolder
        print("Creating directory {0:s} for local configurations and scripts".format(runFolder))
        if not os.path.exists(runFolder):
            os.makedirs(runFolder)
        else:
            print("runfolder '{0:s}' already exists. Rename or delete it and attempt resubmission".format(runFolder))
            sys.exit()

    
    for samplenumber, sample in enumerate(SampleList):
        if samplenumber > 1: continue
        dataset = sample['dataset']
        sampleName = dataset['name']
        era = dataset['era']
        isData = dataset['isData']
        nEvents = dataset['nEvents']
        # print(sample['stagesource'])
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
        
        if args.crab_run:
            coreName = sampleName + "_" + era

            with open("./{0:s}/crab_cfg_{1:s}.py".format(runFolder, coreName), "w") as sample_cfg:
                sample_cfg.write(get_crab_cfg(runFolder, requestName = coreName, inputDataset=inputDataset, stage=args.stage))
            if args.stage != '0Ext':
                with open("./{0:s}/crab_script_{1:s}.sh".format(runFolder, coreName), "w") as sample_script_sh:
                    sample_script_sh.write(get_crab_script_sh(runFolder, requestName = coreName, stage=args.stage))
                with open("./{0:s}/crab_script_{1:s}.py".format(runFolder, coreName), "w") as sample_script_py:
                    sample_script_py.write(get_crab_script_py(runFolder, requestName = coreName, stage=args.stage, sampleConfig = sample))
            
def get_crab_cfg(runFolder, requestName, splitting='Automatic', unitsPerJob = 1, inputDataset = '', storageSite = 'T2_CH_CERN', publication=True, stage='1'):
    #Options for splitting:
    #'Automatic'
    #'EventAwareLumiBased'
    #'FileBased'
    #FIXMEs : scriptExe, inputFiles (including the haddnano script), allow undistributed CMSSW?, publication boolean, 
    if stage == '1':
        crab_cfg = """
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB

config = Configuration()

config.section_("General")
config.General.requestName = '{1:s}'
config.General.transferLogs = True
config.section_("JobType")
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script_{1:s}.sh'
config.JobType.inputFiles = ['crab_script_{1:s}.py', '../../../PhysicsTools/NanoAODTools/scripts/haddnano.py'] #hadd nano will not be needed once nano tools are in cmssw
config.JobType.sendPythonFolder  = True
config.section_("Data")
config.Data.inputDataset = '{4:s}'
config.Data.inputDBS = 'global'
config.Data.splitting = '{2:s}'
if config.Data.splitting == 'FileBased':
    config.Data.unitsPerJob = {3:d}

config.Data.outLFNDirBase = '/store/user/%s/Stage_{7:s}/{0:s}' (getUsernameFromSiteDB())
config.Data.publication = {6:s}
config.Data.outputDatasetTag = '{1:s}'
config.section_("Site")
config.Site.storageSite = {5:s}
"""
        ret = crab_cfg.format(runFolder, requestName, splitting, unitsPerJob, inputDataset, storageSite, str(publication), stage)
    else:
        print("We haven't made a stage {0:s} configuration yet... Exiting".format(stage))
        sys.exit()
    return ret

def get_crab_script_sh(runFolder, requestName, stage='1'):
    crab_script_sh = """
#this is not mean to be run locally
#
echo Check if TTY
if [ "`tty`" != "not a tty" ]; then
  echo "YOU SHOULD NOT RUN THIS IN INTERACTIVE, IT DELETES YOUR LOCAL FILES"
else

ls -lR .
echo "ENV..................................."
env 
echo "VOMS"
voms-proxy-info -all
echo "CMSSW BASE, python path, pwd"
echo $CMSSW_BASE 
echo $PYTHON_PATH
echo $PWD 
rm -rf $CMSSW_BASE/lib/
rm -rf $CMSSW_BASE/src/
rm -rf $CMSSW_BASE/module/
rm -rf $CMSSW_BASE/python/
mv lib $CMSSW_BASE/lib
mv src $CMSSW_BASE/src
mv module $CMSSW_BASE/module
mv python $CMSSW_BASE/python

echo Found Proxy in: $X509_USER_PROXY
python crab_script_{0:s}.py $1
fi
"""
    ret = crab_script_sh.format(requestName)
    return ret

def get_crab_script_py(runFolder, requestName, stage='1', sampleConfig = None, stageConfig = None):
    isData = sampleConfig['dataset']['isData']
    era = sampleConfig['dataset']['era']
    
    if sampleConfig == None:
        print("No sample configuration found, cannot generate meaningful crab_script.py for sample request {0:s}".format(requestName))
        sys.exit()
    if stage == '1':
        crab_script_py = """
#!/usr/bin/env python
import os
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis
from FourTopNAOD.Kai.modules.MCTreeDev import MCTrees
isData = {0:s}
era = {1:s}

if isData:
    moduleCache = [
                   #Modules go here
                  ]
else:
    moduleCache = [
                   MCTrees(maxevt=-1),
                  ]
p=PostProcessor(".", inputFiles(), modules=moduleCache, provenance=True, fwkJobReport=True, jsonInput=runsAndLumis())
p.run()
"""
    elif stage == '':
        crab_script_py = """
"""
    else:
        crab_script_py = """There's nothing here. There's no python script. There's no hope.
You
Are
DOOMED"""
    ret = crab_script_py.format(str(isData), str(era))
    return ret




if __name__ == '__main__':
    main()
