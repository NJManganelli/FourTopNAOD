#!/usr/bin/env python
from __future__ import print_function, division
import os, sys, time, datetime
import argparse
import subprocess
import pprint
from collections import OrderedDict
from ruamel.yaml import YAML
from glob import glob
import tempfile
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser(description='Supervisor handles submission and bookkeeping for physics samples.')
parser.add_argument('--sample_cards', dest='sample_cards', action='store', nargs='*', type=str,
                    help='path and name of the sample card(s) to be used')
parser.add_argument('--hadd', dest='hadd', action='store', nargs='?', type=str, const='hist*.root', default='NOJOIN',
                    help='path of grandparent directory in which to join ROOT files on a per-directory bases, using hadd. Default arguments are hist.root, '\
                    'with the assumption that NanoAOD files are inside subdirectories and will be joined as haddnano parsed_name.root hist_1.root hist_2.root ...'\
                    ' Default parsed_name will be derived from the grandparent folder, as it is tailored to CRAB output structure.')
parser.add_argument('--haddnano', dest='haddnano', action='store', nargs='?', type=str, const='tree*.root', default='NOJOIN',
                    help='path of grandparent directory in which to join NanoAOD files on a per-directory bases. Default arguments is tree.root, '\
                    'with the assumption that NanoAOD files are inside subdirectories and will be joined as haddnano parsed_name.root tree_1.root tree_2.root ...'\
                    ' Default parsed_name will be derived from the grandparent folder, as it is tailored to CRAB output structure.')
parser.add_argument('--check_events', dest='check_events', action='store', nargs='?', type=str, const='simple', default='NOCHECK',
                    help='check that the number of events in source files match those in the sample card, optional argument "local" for files in the user space or optional argument "dbs" for lookup using dasgoclient query')
# parser.add_argument('--check_size', dest='check_size', action='store_true',
#                     help='check total dataset sizes')
parser.add_argument('--local_run', dest='local_run', action='store_true',
                    help='run locally')
parser.add_argument('--crab_run', dest='crab_run', action='store_true',
                    help='run with crab')
parser.add_argument('--percent_run', dest='percent_run', action='append', type=int,
                    help='percent (as an integer) of each sample to process for local_run')
parser.add_argument('--stage', dest='stage', action='store', type=str,
                    help='analysis stage to be produced')
parser.add_argument('--source', dest='source', action='store', type=str, default='0',
                    help='Stage of data storage from which to begin supervisor actions, such as source: 0 which is the unprocessed and centrally maintained data/MC')
parser.add_argument('--redir', dest='redir', action='append', type=str, default='root://cms-xrd-global.cern.ch/',
                    help='redirector for XRootD, such as "root://cms-xrd-global.cern.ch/"')
parser.add_argument('--btagger', dest='btagger', action='store', nargs='+', type=str, default=['DeepCSV', 'M'],
                    help='tagger algorithm and working point to be used')

def main():
    args = parser.parse_args()
    NanoAODPath = "{0:s}/src/PhysicsTools/NanoAODTools".format(os.environ['CMSSW_BASE'])
    username = 'nmangane'
    bareRedir = args.redir.replace("root://", "").replace("/", "")
    if args.local_run and args.crab_run:
        print("Both local_run and crab_run have been set to True; this is not supported. Exiting")
        sys.exit()
    print("Supervisor will check integrity of sample card's event counts: " + str(args.check_events))
    print("Supervisor will use the following algorithm and working point for any btagging related SF calculations and event selection: " + str(args.btagger))
    if args.crab_run:
        print("Supervisor will create crab configurations for stage {0:s} using source {1:s}".format(args.stage, args.source))
    if args.local_run:
        print("Supervisor will run samples locally... or it would, if this were supported. How unfortunate.")
    if args.sample_cards:
        print("The path and name of the sample cards(s) are: ")
        for card in args.sample_cards:
            print("\t{0:s}".format(card))

    #FIXME: Spin off into a function that takes as input the command (hadd, haddnano.py), the file (tree.root, hist.root), and does this instead of Copy+Paste code
    if args.haddnano is not 'NOJOIN':
        print("Joining NanoAOD ROOT files containing {:s}".format(args.haddnano))
        haddnano_regexp = args.haddnano #.replace(".root", "_*.root")
        haddnano_dict = {}
        for directory in os.listdir('.'):
            # haddnano_dict[directory] = glob("./{0:s}/*/".format(directory) + haddnano_regexp)
            haddnano_dict[directory] = getFiles(globPath="./{0:s}/*/".format(directory), globFileExp=haddnano_regexp)
            if len(haddnano_dict[directory]) == 0:
                haddnano_dict[directory] = glob("./{0:s}/".format(directory) + haddnano_regexp)
            if len(haddnano_dict[directory]) == 0:
                _ = haddnano_dict.pop(directory)
        if len(haddnano_dict) > 1:
            joinFolder = "JoinedFiles"
            if not os.path.exists(joinFolder):
                os.makedirs(joinFolder)
            for directory, joinlist in haddnano_dict.iteritems():
                try:
                    joinlist.sort(key=lambda f: int(f.split('_')[-1].replace('.root', '')))
                except Exception:
                    print("Could not sort files prior to joining with haddnano")
                strlistlist = []
                strlistlist.append("")
                strlistsize = []
                strlistsize.append(0)
                for f in joinlist:
                    if strlistsize[-1] + os.path.getsize(f) < 3758096384: #3.5GB file size soft limit
                        strlistlist[-1] += "{0:s} ".format(f)
                        strlistsize[-1] += os.path.getsize(f)
                    else:
                        strlistlist.append("")
                        strlistsize.append(0)
                        strlistlist[-1] += "{0:s} ".format(f)
                        strlistsize[-1] += os.path.getsize(f)
                cmdlist = []
                for s, strlist in enumerate(strlistlist):
                    directorystripped = directory.replace('crab_', '', 1).replace('local_', '', 1).replace('condor_', '', 1)
                    cmdlist.append("haddnano.py {0:s}/{1:s}_{2:d}.root ".format(joinFolder, directorystripped, s+1) + strlist)
                    try:
                        os.system(cmdlist[-1])
                    except Exception:
                        print("Command evaluation failed: \n" + str(cmdlist[-1]))

    
    if args.hadd is not 'NOJOIN':
        print("Joining ROOT files containing {:s}".format(args.hadd))
        hadd_regexp = args.hadd #.replace(".root", "_*.root")
        hadd_dict = {}
        for directory in os.listdir('.'):
            # hadd_dict[directory] = glob("./{0:s}/*/".format(directory) + hadd_regexp)
            hadd_dict[directory] = getFiles(globPath="./{0:s}/*/".format(directory), globFileExp=hadd_regexp)
            if len(hadd_dict[directory]) == 0:
                hadd_dict[directory] = glob("./{0:s}/".format(directory) + hadd_regexp)
            if len(hadd_dict[directory]) == 0:
                #Remove directory from dictionary, since it contains nothing of interest
                _ = hadd_dict.pop(directory)
        if len(hadd_dict) > 1:
            joinFolder = "JoinedFiles"
            if not os.path.exists(joinFolder):
                os.makedirs(joinFolder)
            for directory, joinlist in hadd_dict.iteritems():
                try:
                    joinlist.sort(key=lambda f: int(f.split('_')[-1].replace('.root', '')))
                except Exception:
                    print("Could not sort files prior to joining with haddnano")
                strlistlist = []
                strlistlist.append("")
                strlistsize = []
                strlistsize.append(0)
                for f in joinlist:
                    if strlistsize[-1] + os.path.getsize(f) < 3758096384: #3.5GB file size soft limit
                        strlistlist[-1] += "{0:s} ".format(f)
                        strlistsize[-1] += os.path.getsize(f)
                    else:
                        strlistlist.append("")
                        strlistsize.append(0)
                        strlistlist[-1] += "{0:s} ".format(f)
                        strlistsize[-1] += os.path.getsize(f)
                cmdlist = []
                for s, strlist in enumerate(strlistlist):
                    directorystripped = directory.replace('crab_', '', 1).replace('local_', '', 1).replace('condor_', '', 1)
                    cmdlist.append("hadd {0:s}/{1:s}_hist_{2:d}.root ".format(joinFolder, directorystripped, s+1) + strlist)
                    try:
                        os.system(cmdlist[-1])
                    except Exception:
                        print("Command evaluation failed: \n" + str(cmdlist[-1]))

    if not args.sample_cards: 
        print("Finishing operations that require no sample card(s)")
        sys.exit()

    SampleList = []
    yaml = YAML() #default roundtrip type
    for scard in args.sample_cards:
        # print("\t" + scard) #Already printed elsewhere
        with open(scard) as sample:
            SampleList += yaml.load(sample)

    #Generate crab and local folder name using the current time, outside the sample loop
    stageFolder = "Stage_{0:s}_to_{1:s}".format(args.source, args.stage)
    dt = datetime.datetime.now()
    runFolder = "{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    if args.crab_run:
        runFolder = stageFolder + "/crab_" + runFolder
        print("Creating directory {0:s} for crab configurations and scripts".format(runFolder))
        if not os.path.exists(stageFolder):
            os.makedirs(stageFolder)
        if not os.path.exists(runFolder):
            os.makedirs(runFolder)
        if not os.path.exists(runFolder+"/PSet.py"):
            with open(runFolder+"/PSet.py", "w") as PSet_py:
                PSet_py.write(get_PSet_py(NanoAODPath))
        else:
            print("runfolder '{0:s}' already exists. Rename or delete it and attempt resubmission".format(runFolder))
            sys.exit()

    if args.local_run:
        runFolder = stageFolder + "/local_" + runFolder
        print("Creating directory {0:s} for local configurations and scripts".format(runFolder))
        if not os.path.exists(stageFolder):
            os.makedirs(stageFolder)
        if not os.path.exists(runFolder):
            os.makedirs(runFolder)
        else:
            print("runfolder '{0:s}' already exists. Rename or delete it and attempt resubmission".format(runFolder))
            sys.exit()

    total_data_size = 0
    total_MC_size = 0
    for samplenumber, sample in enumerate(SampleList):
        #Parse dataset portion
        dataset = sample.get('dataset')
        sampleName = dataset.get('name')
        era = dataset.get('era')
        isData = dataset.get('isData')
        nEvents = dataset.get('nEvents', 0) #Default to 0 when key DNE

        #parse source portion
        source = sample.get('source')
        inputDataset = source.get(args.source, None)

        #parse crab portion
        crab_cfg = sample['crab_cfg']

        #parse crab portion
        postprocessor = sample['postprocessor']
    
        #write out the filelist to personal space in /tmp, if check_events or local_run is true, then use these to run
        if args.check_events != 'NOCHECK' or args.local_run: # or args.check_size:
            # query='--query="file dataset=' + inputDataset.replace("dbs:","") + '"'
            # tmpFileLoc = '/tmp/{0:s}/sample_{1:d}_fileList.txt'.format(username, samplenumber)
            # cmd = 'dasgoclient ' + query + ' > ' + tmpFileLoc
            # os.system(cmd)
        
            # # Load the filelist names including redirector
            # fileList = []
            # with open(tmpFileLoc, "r") as rawFileList:
            #     for line in rawFileList:
            #         tempName = args.redir + line
            #         tempName = tempName.rstrip()
            #         fileList.append(tempName)
            if inputDataset is None:
                print("Skipping check_events for sample {0}({1}) due to lack of valid source path ({2})".format(sampleName, era, args.source))
            elif "list:" in inputDataset:
                fileList = getFiles(inFileName=inputDataset.replace("list:",""))
            elif "glob:" in inputDataset:
                fileList = getFiles(globPath=inputDataset.replace("glob:",""), globFileExp="")
                if len(fileList) == 0 and len(fileList = getFiles(globPath=inputDataset.replace("glob:",""), globFileExp="tree_*.root")) > 0:
                    fileList = fileList = getFiles(globPath=inputDataset.replace("glob:",""), globFileExp="tree_*.root")
            else: # "dbs:" in inputDataset:
                fileList = getFiles(dbsDataset=inputDataset.replace("dbs:",""), redir="root://cms-xrd-global.cern.ch/")

        # if args.check_size:
        #     #This will probably be abandoned in favor of using ROOT::Tfile::GetSize()
        #     for fileName in fileList:
        #         cmd = "xrdfs {0:s} stat {1:s} | awk '$1 ~ /Size/ {print $2}'".format(bareRedir, fileName.replace(args.redir, ""))
        #         print(cmd)
        
        if args.check_events != 'NOCHECK':
            if isData == False:
                current_events_in_files = 0
                events_in_files = 0
                if args.check_events == 'detailed':
                    events_in_files_positive = 0
                    events_in_files_negative = 0
                else:
                    events_in_files_positive = -999
                    events_in_files_negative = -999
                events_sum_weights = 0
                events_sum_weights2 = 0
                dataset_size = 0
                for fileName in fileList:
                    # print("Opening {0}".format(fileName))
                    f = ROOT.TFile.Open(fileName, 'r')
                    dataset_size += int(f.GetSize())
                    tree = f.Get('Runs')
                    for en in xrange(tree.GetEntries()):
                        tree.GetEntry(en)
                        events_in_files += tree.genEventCount
                        events_sum_weights += tree.genEventSumw
                        events_sum_weights2 += tree.genEventSumw2
                    evtTree = f.Get('Events')
                    eventsTreeEntries = evtTree.GetEntries()
                    current_events_in_files += eventsTreeEntries
                    if args.check_events == 'detailed':#Only do this for MC
                        for i in xrange(eventsTreeEntries):
                            evtTree.GetEntry(i)
                            if evtTree.genWeight > 0:
                                events_in_files_positive += 1
                            elif evtTree.genWeight < 0:
                                events_in_files_negative += 1
                            else:
                                raise RuntimeError("event with weight 0 in file: {0} run: {1} lumi: {2} event: {3}".format(f.GetName(), evtTree.run, 
                                                                                                                           evtTree.luminosityBlock, 
                                                                                                                           evtTree.event))
                            if i % 10000 == 0:
                                print("processed {0} events in file: {1}".format(i, f.GetName()))
                                
                            
                    # f.Close() #Will this speed things up any?
                if events_in_files != nEvents:
                    print("Mismatch in dataset {0}: nEvents = {1:d}, events_in_files = {2:d}".format(sampleName, nEvents, events_in_files))
                else:
                    print("Integrity check successful for dataset {0}: {1:d}/{2:d} events".format(sampleName, events_in_files, nEvents))
                print("nEvents = {0:d}, events_in_files = {1:d}, events_sum_weights = {2:f}, "\
                      "events_sum_weights2 = {3:f}, current_events_in_files = {4:d}, events_in_files_positive = {5:d}"\
                      ", events_in_files_negative = {6:d}, dataset_size = {7:f}GB".format(nEvents, events_in_files, 
                                                      events_sum_weights, events_sum_weights2, 
                                                      current_events_in_files,events_in_files_positive,
                                                      events_in_files_negative, dataset_size/1024**3)
                  )
                total_MC_size += dataset_size
            else:
                #Distinguish the current event count, which is based on tree entries, from the event counter stored in MC showing how many events had been processed
                current_events_in_files = 0
                dataset_size = 0
                for fileName in fileList:
                    # print("Opening {0}".format(fileName))
                    f = ROOT.TFile.Open(fileName, 'r')
                    dataset_size += int(f.GetSize())
                    evtTree = f.Get('Events')
                    current_events_in_files += evtTree.GetEntries()
                if current_events_in_files != nEvents:
                    print("Mismatch in dataset {0}: nEvents = {1:d}, current_events_in_files = {2:d}".format(sampleName, nEvents, current_events_in_files))
                else:
                    print("Integrity check successful for dataset {0}: {1:d}/{2:d} events".format(sampleName, current_events_in_files, nEvents))
                print("nEvents = {0:d}, current_events_in_files = {1:d}, dataset_size = {2:f}GB".format(nEvents, current_events_in_files, dataset_size/1024**3))
                total_data_size += dataset_size

        if args.crab_run:
            coreName = sampleName + "_" + era

            with open("./{0:s}/crab_cfg_{1:s}.py".format(runFolder, coreName), "w") as sample_cfg:
                sample_cfg.write(get_crab_cfg(runFolder, requestName = coreName, NanoAODPath = NanoAODPath, 
                                              splitting = crab_cfg['splitting'], inputDataset=inputDataset, stage=args.stage))
            if 'extNANO' not in args.stage:
                with open("./{0:s}/crab_script_{1:s}.sh".format(runFolder, coreName), "w") as sample_script_sh:
                    sample_script_sh.write(get_crab_script_sh(runFolder, requestName = coreName, stage=args.stage))
                with open("./{0:s}/crab_script_{1:s}.py".format(runFolder, coreName), "w") as sample_script_py:
                    sample_script_py.write(get_crab_script_py(runFolder, requestName = coreName, stage=args.stage, sampleConfig = sample, btagger = args.btagger))

    if args.check_events != 'NOCHECK':
        print("total_data_size = {0:f}GB, total_MC_size = {1:f}GB".format(total_data_size/1024**3, total_MC_size/1024**3))
            
def get_crab_cfg(runFolder, requestName, NanoAODPath='.', splitting='', unitsPerJob = 1, inputDataset = '', storageSite = 'T2_CH_CERN', publication=True, stage='Baseline'):
    #Options for splitting:
    #'Automatic'
    #'EventAwareLumiBased'
    #'FileBased'
    #FIXMEs : scriptExe, inputFiles (including the haddnano script), allow undistributed CMSSW?, publication boolean, 
    if stage == 'Baseline':
        crab_cfg = """from WMCore.Configuration import Configuration
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
config.JobType.inputFiles = ['crab_script_{1:s}.py', '{8:s}/scripts/haddnano.py'] #, '../../../PhysicsTools/NanoAODTools/scripts/haddnano.py'] #hadd nano will not be needed once nano tools are in cmssw
config.JobType.outputFiles = ['hist.root']
config.JobType.sendPythonFolder  = True
config.section_("Data")
config.Data.inputDataset = '{4:s}'
config.Data.inputDBS = 'global'
config.Data.splitting = '{2:s}'
if config.Data.splitting == 'FileBased':
    config.Data.unitsPerJob = {3:d}

config.Data.outLFNDirBase = '/store/user/%s/{0:s}' % (getUsernameFromSiteDB())
config.Data.publication = {6:s}
config.Data.outputDatasetTag = '{1:s}'
config.section_("Site")
config.Site.storageSite = '{5:s}'
"""
        ret = crab_cfg.format(runFolder, requestName, splitting, unitsPerJob, inputDataset, storageSite, str(publication), stage, str(NanoAODPath))
    else:
        print("We haven't made a stage {0:s} configuration yet... Exiting".format(stage))
        sys.exit()
    return ret

def get_crab_script_sh(runFolder, requestName, stage='Baseline'):
    crab_script_sh = """#this is not mean to be run locally
#
echo Check if TTY
if [ "`tty`" != "not a tty" ]; then
  echo "YOU SHOULD NOT RUN THIS IN INTERACTIVE, IT DELETES YOUR LOCAL FILES"
else

ls -ltr .
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
ls -ltr
fi
"""
    ret = crab_script_sh.format(requestName)
    return ret

def get_crab_script_py(runFolder, requestName, stage='Baseline', sampleConfig = None, stageConfig = None, btagger = ['None', 'None']):
    eLumiDict = {'2016': 35,
                 '2017': 41.53,
                 '2018': 50
                 }
    name = sampleConfig['dataset'].get('name')
    isData = sampleConfig['dataset'].get('isData')
    era = sampleConfig['dataset'].get('era')
    subera = sampleConfig['dataset'].get('subera')
    crossSection = sampleConfig['dataset'].get('crossSection')
    equivLumi = eLumiDict.get(era)
    nEvents = sampleConfig['dataset'].get('nEvents')
    sumWeights = sampleConfig['dataset'].get('sumWeights')
    isSignal = sampleConfig['dataset'].get('isSignal')
    
    
    
    preselection = sampleConfig['postprocessor']['filter']
    if preselection != "":
        preselection = "\"" + preselection + "\""
    else:
        preselection = None
    
    if sampleConfig == None:
        print("No sample configuration found, cannot generate meaningful crab_script.py for sample request {0:s}".format(requestName))
        sys.exit()
    if stage == 'Baseline':
        crab_script_py = """#!/usr/bin/env python
import os, time, collections, copy, json, multiprocessing
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import * 
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *
from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from FourTopNAOD.Kai.modules.BaselineSelector import BaselineSelector
from FourTopNAOD.Kai.modules.trigger import Trigger
from FourTopNAOD.Kai.modules.MCTreeDev import MCTrees
SC_isData = {0:s}
SC_era = "{1:s}"
SC_subera = "{2:s}"
SC_thePreselection = {3:s}
SC_crossSection = {4:s}
SC_equivLumi = {5:s}
SC_nEvents = {6:s}
SC_sumWeights = {7:s}
Sup_BTagger = {8:s}

theFiles = inputFiles()

triggers=["HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8",
          "HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ",
          "HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ",
          "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
          ]

#Double braces to escape them inside the literal string template used by Supervisor (with .format method)
dataRecalib = {{"2017": {{"B": jetRecalib("Fall17_17Nov2017B_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "C": jetRecalib("Fall17_17Nov2017C_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "D": jetRecalib("Fall17_17Nov2017DE_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "E": jetRecalib("Fall17_17Nov2017DE_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "F": jetRecalib("Fall17_17Nov2017F_V32_DATA","Fall17_17Nov2017_V32_DATA"),
                          "NONE": "NothingToSeeHere"
                      }}
            }}

if SC_isData:
    theLumis = runsAndLumis()
    moduleCache=[Trigger(triggers),
                 dataRecalib[SC_era][SC_subera],
                 BaselineSelector(maxevt=-1, 
                                  probEvt=None,
                                  isData=SC_isData,
                                  era=SC_era,
                                  lepPt=13, 
                                  MET=40, 
                                  HT=350, 
                                  jetPtVar="pt_nom",
                                  jetMVar="mass_nom"
                              ),
             ]
else:
    theLumis = None
    moduleCache=[puWeightProducer("auto",
                                   pufile_data2017,
                                   "pu_mc",
                                   "pileup",
                                   verbose=False
                                 ),
                 Trigger(triggers),
                 jetmetUncertaintiesProducer("2017", 
                                             "Fall17_17Nov2017_V32_MC", 
                                             [ "All" ], 
                                             redoJEC=True
                                         ),
                 BaselineSelector(maxevt=-1, 
                                  probEvt=None,
                                  isData=SC_isData,
                                  genEquivalentLuminosity=SC_equivLumi,
                                  genXS=SC_crossSection,
                                  genNEvents=SC_nEvents,
                                  genSumWeights=SC_sumWeights,
                                  era=SC_era,
                                  lepPt=13, 
                                  MET=40, 
                                  HT=350, 
                                  jetPtVar="pt_nom",
                                  jetMVar="mass_nom"
                              ),
                 ]

p=PostProcessor(".", 
                theFiles,       
                modules=moduleCache, 
                cut=SC_thePreselection, 
                provenance=True, 
                fwkJobReport=True, 
                jsonInput=theLumis, 
                histFileName="hist.root",
                histDirName="plots"
                )
p.run()
"""
    elif stage == '':
        crab_script_py = """
"""
    else:
        crab_script_py = """#There's nothing here. There's no python script. There's no hope.
#You
#Are
#DOOMED"""
    ret = crab_script_py.format(str(isData), str(era), str(subera), str(preselection), str(crossSection), str(equivLumi), str(nEvents), str(sumWeights), str(btagger))
    return ret

def get_PSet_py(NanoAODPath):
    PSet_py = """#this fake PSET is needed for local test and for crab to figure the output filename
#you do not need to edit it unless you want to do a local test using a different input file than
#the one marked below
import FWCore.ParameterSet.Config as cms
process = cms.Process('NANO')
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(),
#	lumisToProcess=cms.untracked.VLuminosityBlockRange("254231:1-254231:24")
)
process.source.fileNames = [
	'{0:s}/test/lzma.root' ##you can change only this line
]
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(10))
process.output = cms.OutputModule("PoolOutputModule", fileName = cms.untracked.string('tree.root'))
process.out = cms.EndPath(process.output)
"""
    return PSet_py.format(str(NanoAODPath))





#import glob, os, tempfile
def getFiles(globPath=None, globFileExp="*.root", globSort=lambda f: int(f.split('_')[-1].replace('.root', '')), dbsDataset=None, inFileName=None, redir="", outFileName=None):
    """Use one of several different methods to acquire a list or text file specifying the filenames.

Method follows after globPath, inFileName, or dbsDataset is specified, with precedence going glob > dbs > file.
globPath should be globbable in python. For example "./my2017ttbarDir/*/results"
globPath has additional option globFileExp which defaults to "*.root", but can be changed to "tree_*.root" or "SF.txt" for example
dbsDataset should just be a string as would be used in DAS/dasgoclient search, such as "/DoubleMuon/*/NANOAOD"
inFileName should specify the path to a file storing the filenames as plain text.

additional options:
outFileName will write the filelist to the specified file path + name
redir will prepend the redirector to the beginning of the paths, such as redir="root://cms-xrd-global.cern.ch/"
"""
    #methods to support: "dbs" using dasgoclient query, "glob" using directory path, "file" using text file
    fileList = []
    with tempfile.NamedTemporaryFile() as f:
        #check file exists as additional check?
        if inFileName:
            if True:
                raise RuntimeError("getFiles() attempted using meth='file' without a inFileName specified")
            else:
                pass
        elif globPath:
            if False:
                raise RuntimeError("getFiles() attempted using meth='glob' without a globbable globPath specified")
            else:
                fileList = glob("{0}".format(globPath) + globFileExp)
                try:
                    fileList.sort(key=globSort)
                except Exception:
                    print("Could not sort files prior to joining with haddnano")
        elif dbsDataset:
            if False:
                raise RuntimeError("getFiles() attempted using meth='dbs' without a dbsDataset specified")
            else:
                cmd = 'dasgoclient --query="file dataset={0:s}" > {1:s}'.format(dbsDataset,f.name)
                os.system(cmd)
                for line in f:
                    tmpName = redir + line
                    tmpName = tmpName.rstrip()
                    fileList.append(tmpName)
    if outFileName:
        raise NotImplementedError("returning file not eimplemented yet")
        
    return fileList

if __name__ == '__main__':
    main()

