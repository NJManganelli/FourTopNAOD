#!/usr/bin/env python
from __future__ import print_function, division
import os, pwd, sys, time, datetime
import argparse
import subprocess
import pprint
import copy
import tempfile
from collections import OrderedDict, namedtuple
from glob import glob
from FourTopNAOD.Kai.tools.toolbox import getFiles
import pdb
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

SampleTuple = namedtuple("SampleTuple", "fileList era subera isData isSignal nEvents nEventsPositive nEventsNegative crossSection channel")

parser = argparse.ArgumentParser(description='Nanovisor handles submission and bookkeeping for physics samples.')
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
parser.add_argument('--fileLists', dest='fileLists', action='store', nargs='?', type=str, const='nanovisorFileLists', default=False,
                    help='Write out fileLists for samples, with optional folder specified afterwards. Default folder will be "nanovisorFileLists"')
parser.add_argument('--filter', dest='filter', action='store', type=str, default=None,
                    help='string to filter samples while checking events or generating configurations')
parser.add_argument('--local_run', dest='local_run', action='store_true',
                    help='run locally')
parser.add_argument('--crab_run', dest='crab_run', action='store_true',
                    help='run with crab')
parser.add_argument('--templates', dest='templates', action='store', nargs='*', type=str, default=["../scripts/crab_cfg_TEMPLATE.py", "../scripts/crab_script_TEMPLATE.sh", "../scripts/crab_script_TEMPLATE.py"],
                    help='path and name of the templates to be used, the keyword "TEMPLATE" will be replaced by the <requestName> in filenames.')
parser.add_argument('--percent_run', dest='percent_run', action='append', type=int,
                    help='percent (as an integer) of each sample to process for local_run')
parser.add_argument('--tag', dest='tag', action='store', type=str,
                    help='analysis tag for template production')
parser.add_argument('--source', dest='source', action='store', type=str, default='0',
                    help='Stage of data storage from which to begin supervisor actions, such as source: 0 which is the unprocessed and centrally maintained data/MC')
parser.add_argument('--redir', dest='redir', action='append', type=str, default='root://cms-xrd-global.cern.ch/',
                    help='redirector for XRootD, such as "root://cms-xrd-global.cern.ch/"')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    help='Enable more verbose output during actions')

def main():
    args = parser.parse_args()
    NanoAODPath = os.path.join(os.environ['CMSSW_BASE'], "src/PhysicsTools/NanoAODTools")
    username = pwd.getpwuid( os.getuid() )[ 0 ]
    bareRedir = args.redir.replace("root://", "").replace("/", "")
    if args.local_run and args.crab_run:
        print("Both local_run and crab_run have been set to True; this is not supported. Exiting")
        sys.exit()
    print("Nanovisor will check integrity of sample card's event counts: " + str(args.check_events))
    if args.crab_run:
        print("Nanovisor will create crab configurations for tag {0:s} using source {1:s}".format(args.tag, args.source))
        print("The templates that will be used in generation are: {}".format(args.templates))
    if args.local_run:
        print("Nanovisor will run samples locally... or it would, if this were supported. How unfortunate.")
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
            search_path = "glob:./{0:s}/*/".format(directory) + haddnano_regexp
            haddnano_dict[directory] = getFiles(query=search_path)
            if len(haddnano_dict[directory]) == 0:
                search_path = "glob:./{0:s}/".format(directory) + haddnano_regexp
                haddnano_dict[directory] = getFiles(query=search_path)
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
            search_path = "glob:./{0:s}/*/".format(directory) + hadd_regexp
            hadd_dict[directory] = getFiles(query=search_path)
            if len(hadd_dict[directory]) == 0:
                search_path = "glob:./{0:s}/".format(directory) + hadd_regexp
                hadd_dict[directory] = getFiles(query=search_path)
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

    SampleList = load_sample_cards(args.sample_cards)

    #Generate crab and local folder name using the current time, outside the sample loop
    tagFolder = "{0:s}_{1:s}".format(args.source, args.tag)
    dt = datetime.datetime.now()
    runFolder = "{0:d}{1:02d}{2:02d}_{3:02d}{4:02d}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    if args.crab_run:
        runFolder = os.path.join(tagFolder, runFolder)
        print("Creating directory {0:s} for crab configurations and scripts".format(runFolder))
        if not os.path.exists(tagFolder):
            os.makedirs(tagFolder)
        if not os.path.exists(runFolder):
            os.makedirs(runFolder)
        if not os.path.exists(runFolder+"/PSet.py"):
            with open(runFolder+"/PSet.py", "w") as PSet_py:
                PSet_py.write(get_PSet_py(NanoAODPath))
            with open(runFolder+"/crab_submit_all.py", "w") as crab_submit_all_py:
                crab_submit_all_py.write(get_crab_submit_all_py())
        else:
            print("runfolder '{0:s}' already exists. Rename or delete it and attempt recreation".format(runFolder))
            sys.exit()

    if args.local_run:
        runFolder = tagFolder + "/local_" + runFolder
        print("Creating directory {0:s} for local configurations and scripts".format(runFolder))
        if not os.path.exists(tagFolder):
            os.makedirs(tagFolder)
        if not os.path.exists(runFolder):
            os.makedirs(runFolder)
        else:
            print("runfolder '{0:s}' already exists. Rename or delete it and attempt recreation".format(runFolder))
            sys.exit()

    total_Data_size = 0
    total_Data_current_events = 0
    total_MC_size = 0
    total_MC_current_events = 0
    total_MC_processed_events = 0

    variety_pack_filelist = []
    variety_pack_tuples = []
    for sampleName, sample in SampleList.items():
        #Parse dataset portion
        era = sample.get('era')
        subera = sample.get('subera', 'NONE')
        channel = sample.get('channel', 'NONE')

        #Filter samples early
        if args.filter:
            if type(args.filter) is str:
                if args.filter not in sampleName+"_"+era:
                    continue

        isData = sample.get('isData')
        isSignal = sample.get('isSignal', False)
        crossSection = sample.get('crossSection', -1)
        nEvents = sample.get('nEvents', 0) #Default to 0 when key DNE
        nEventsPositive = sample.get('nEventsPositive', 0)
        nEventsNegative = sample.get('nEventsNegative', 0)
        
        #parse source portion
        source = sample.get('source')
        inputDataset = source.get(args.source, None)

        #Make outFileList.txt name combining sample, era, and source, if fileLists are requested
        if args.fileLists:
            #Make directory path which is nanovisorFileLists by default, optionally user-defined
            if not os.path.exists(args.fileLists):
                os.makedirs(args.fileLists)
            sampleOutFile = args.fileLists + "/" + sampleName + "_" + era + "_" + args.source + ".txt"
        else:
            sampleOutFile=None
    
        #write out the filelist to personal space in /tmp, if check_events or local_run is true, then use these to run
        if args.check_events != 'NOCHECK' or args.local_run or args.fileLists:
            if inputDataset is None:
                pass
                # print("\tSkipped check_events for sample {0}({1}) due to lack of valid source path ({2})".format(sampleName, era, args.source))
            elif "list:" in inputDataset or "glob:" in inputDataset or "dbs:" in inputDataset:
                if "dbs:" in inputDataset:
                    fileList = getFiles(query=inputDataset, redir=args.redir, outFileName=sampleOutFile)
                else:
                    fileList = getFiles(query=inputDataset, outFileName=sampleOutFile)
                if len(fileList) > 0: 
                    variety_pack_filelist.append(fileList[0])
                    variety_pack_tuples.append(SampleTuple(fileList=fileList[0:1], era=era, subera=subera, isData=isData, isSignal=isSignal, 
                                                           nEvents=nEvents, nEventsPositive=nEventsPositive, nEventsNegative=nEventsNegative, 
                                                           crossSection=crossSection, channel=channel))
            else:
                print("Need to append getFiles() query type to inputDataset, such as 'glob:' or 'list:' or 'dbs:'")
            

        if args.check_events != 'NOCHECK':
            if isData == False:
                current_events_in_files = 0
                events_in_files = 0
                # events_in_files_positive = 0
                # events_in_files_negative = 0
                if args.check_events == 'detailed':
                    events_in_files_positive = 0
                    events_in_files_negative = 0
                else:
                    events_in_files_positive = -999
                    events_in_files_negative = -999
                events_sum_weights = 0
                events_sum_weights2 = 0
                dataset_size = 0
                print("Checking {0:d} files".format(len(fileList)))
                for fn, fileName in enumerate(fileList):
                    if args.verbose: 
                        print("File {} of {}".format(fn, len(fileList)))
                        print("#", end="")
                    f = ROOT.TFile.Open(fileName, 'r')
                    dataset_size += int(f.GetSize())
                    tree = f.Get('Runs')
                    for en in xrange(tree.GetEntries()):
                        tree.GetEntry(en)
                        events_in_files += tree.genEventCount
                        events_sum_weights += tree.genEventSumw
                        events_sum_weights2 += tree.genEventSumw2
                    if args.check_events == 'detailed':
                        evtTree = f.Get('Events')
                        evtTree.SetBranchStatus("*", 0)
                        evtTree.SetBranchStatus("genWeight", 1)
                        eventsTreeEntries = evtTree.GetEntries()
                        current_events_in_files += int(eventsTreeEntries)
                        events_in_files_positive += int(evtTree.GetEntries('genWeight > 0'))
                        events_in_files_negative += int(evtTree.GetEntries('genWeight < 0'))
                        evtTree.SetBranchStatus("*", 1)
                    else:
                        evtTree = f.Get('Events')
                        eventsTreeEntries = evtTree.GetEntries()
                        current_events_in_files += int(eventsTreeEntries)
                    f.Close()                                
                            

                print("\n" + sampleName + "_" + era + ":")
                if inputDataset is None:
                    print("\tSkipped check_events for sample {0}({1}) due to lack of valid source path ({2})".format(sampleName, era, args.source))
                if events_in_files != nEvents:
                    print("\tMismatch in dataset {0}: nEvents = {1:d}, events_in_files = {2:d}".format(sampleName, nEvents, events_in_files))
                else:
                    print("\tIntegrity check successful for dataset {0}: {1:d}/{2:d} events".format(sampleName, events_in_files, nEvents))
                print("        nEvents: {0:d}\n        nEventsPositive: {1:d}\n        nEventsNegative: {2:d}\n        sumWeights: {3:f}\n        sumWeights2: {4:f}"\
                      "\n        processed_events: {5:d}\n        sample card nEvents: {6:d}"\
                      "\n        dataset_size: {7:4f}GB".format(current_events_in_files, 
                                                                events_in_files_positive,
                                                                events_in_files_negative, 
                                                                events_sum_weights, 
                                                                events_sum_weights2, 
                                                                events_in_files, 
                                                                nEvents,
                                                                dataset_size/1024**3)
                  )
                total_MC_size += dataset_size
                total_MC_current_events += current_events_in_files
                total_MC_processed_events += events_in_files
            else:
                #Distinguish the current event count, which is based on tree entries, from the event counter stored in MC showing how many events had been processed
                current_events_in_files = 0
                dataset_size = 0
                print("Checking {0:d} files".format(len(fileList)))
                for fn, fileName in enumerate(fileList):
                    if args.verbose:
                        print("#", end="")
                    f = ROOT.TFile.Open(fileName, 'r')
                    dataset_size += int(f.GetSize())
                    evtTree = f.Get('Events')
                    eventsTreeEntries = evtTree.GetEntries()
                    current_events_in_files += int(eventsTreeEntries)
                    if args.verbose:
                        print("Filename: {}\n\tEvents: {}\t EventTotal: {}".format(fileName, evtTree.GetEntries(), current_events_in_files))
                    f.Close()
                print("\n" + sampleName + "_" + era + ":")
                if inputDataset is None:
                    print("\tSkipped check_events for sample {0}({1}) due to lack of valid source path ({2})".format(sampleName, era, args.source))
                if current_events_in_files != nEvents:
                    print("\tMismatch in dataset {0}: nEvents = {1:d}, current_events_in_files = {2:d}".format(sampleName, nEvents, current_events_in_files))
                else:
                    print("\tIntegrity check successful for dataset {0}: {1:d}/{2:d} events".format(sampleName, current_events_in_files, nEvents))
                print("        nEvents: {0:d}\n        sample card nEvents: {1:d}\n        dataset_size: {2:4f}GB".format(current_events_in_files, nEvents, dataset_size/1024**3))
                total_Data_size += dataset_size
                total_Data_current_events += current_events_in_files

        if args.crab_run:
            theLumi = {"2017": 41.53, "2018": 59.97}
            requestName = era + "_" + sampleName
            splitting = sample.get('crab_cfg', {}).get("splitting", "FileBased")
            inputDataset = sample.get('source', {}).get(args.source, None)
            if len(inputDataset.split(" instance=")) > 1:
                cleanInputDataset = inputDataset.split(" instance=")[0].replace("dbs:", "")
                dbs = inputDataset.split(" instance=")[1].replace("prod/", "")
            else:
                cleanInputDataset = inputDataset.replace("dbs:", "")
                dbs = "global"
            unitsPerJob = sample.get('crab_cfg', {}).get("unitsPerJob", 1)
            storageSite = "T2_CH_CERN"
            publication = True
            isData = sample.get('isData')
            isSignal = sample.get('isSignal', False)
            isUltraLegacy = sample.get('isUltraLegacy', False)
            era = sample.get('era')
            templateEra = '\"{}\"'.format(sample.get('era')) if sample.get('era', None) is not None else None
            templateSubera = '\"{}\"'.format(sample.get('subera')) if sample.get('subera', None) is not None else None
            preselection = None
            crossSection = sample.get('crossSection', -1) if not isData else None
            equivLumi = theLumi.get(era, -123)
            nEvents = sample.get('nEvents', 1) if not isData else None #Default to 0 when key DNE
            nEventsPositive = sample.get('nEventsPositive', 1) if not isData else None
            nEventsNegative = sample.get('nEventsNegative', 0) if not isData else None
            sumWeights = sample.get('sumWeights')
            triggerChannel = '\"{}\"'.format(sample.get('channel')) if sample.get('channel', None) is not None else None
            tag=args.tag

            
            replacement_tuples = [("$REQUEST_NAME", requestName),
                                  ("$INPUT_DATASET", cleanInputDataset),
                                  ("$SPLITTING", splitting),
                                  ("$DBS", dbs),
                                  ("$UNITS_PER_JOB", unitsPerJob),
                                  ("$STORAGE_SITE", storageSite),
                                  ("$PUBLICATION", str(publication)),
                                  ("$IS_DATA", str(isData)),
                                  ("$IS_ULTRA_LEGACY", str(isUltraLegacy)),
                                  ("$ERA", templateEra),
                                  ("$SUBERA", templateSubera),
                                  ("$PRESELECTION", preselection),
                                  ("$CROSS_SECTION", crossSection),
                                  ("$LUMI", equivLumi),
                                  ("$N_EVENTS", nEvents),
                                  ("$N_EVENTS_POSITIVE", nEventsPositive),
                                  ("$N_EVENTS_NEGATIVE", nEventsNegative),
                                  ("$SUM_WEIGHTS", sumWeights),
                                  ("$TRIGGER_CHANNEL", triggerChannel),
                                  ("$TAG", tag),
                              ]
            #move keys which are subelements of other keys to end of replacement list
            replacement_tuples = sorted(replacement_tuples, key=lambda tup: sum([tup[0] in l[0] for l in replacement_tuples]), reverse=False)

            for template in args.templates:
                with open("./{0:s}/{1:s}".format(runFolder, template.split("/")[-1].replace("TEMPLATE", requestName)), "w") as generated:
                    modifiedTemplate = replace_template_parameters(load_template(template), replacement_tuples=replacement_tuples)
                    for line in modifiedTemplate:
                        generated.write(line)

    if args.check_events != 'NOCHECK':
        print("All samples:\n\ttotal_Data_size = {0:f}GB, total_Data_current_events = {1:d}\n\t"\
              "total_total_MC_size = {2:f}GB, total_MC_current_events = {3:d}, "\
              "total_MC_processed_events = {4:d}".format(total_Data_size/1024**3, total_Data_current_events, total_MC_size/1024**3,
                                                         total_MC_current_events, total_MC_processed_events))
    if args.fileLists:
        variety_outfile = args.fileLists + "/" + "variety_pack" + "_" + era + "_" + args.source + ".txt"
        variety_outfile_tuples = args.fileLists + "/" + "variety_pack_tuples" + "_" + era + "_" + args.source + ".txt"
        
        with open(variety_outfile, "w") as out_f:
            for line in variety_pack_filelist: 
                out_f.write(line + "\n")
        with open(variety_outfile_tuples, "w") as out_t:
            for tup in variety_pack_tuples: 
                out_t.write( tup.fileList[0] + "," + tup.era + "," + tup.subera + "," + str(tup.isData) + "," + str(tup.isSignal) + 
                             "," + str(tup.nEvents) + "," + str(tup.nEventsPositive) + "," + str(tup.nEventsNegative) + "," + 
                             str(tup.crossSection) + "," + str(tup.channel) + "\n")

def replace_template_parameters(input_list, replacement_tuples=[("$CAMPAIGN", "TestCampaign")] ):
    return_list = []
    for l in input_list:
        temp = copy.copy(l)
        for tup in replacement_tuples:
            rin, rout = tup
            temp = temp.replace(rin, str(rout))
        return_list.append(temp)
    return return_list

def load_template(template_file):
    template_lines = []
    try:
        with open(template_file, "r") as template:
            for line in template:
                template_lines.append(line)
        return template_lines
    except:
        raise IOError("template file {} not found".format(template_file))
            
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

def get_crab_submit_all_py():
    ret = """#!/usr/bin/env python
import os, sys, datetime, subprocess
from glob import glob
cfg_files = glob("./crab_cfg_*")
cfg_files = [f for f in cfg_files if ".pyc" not in f]
for f in cfg_files:
    cmd = "crab submit -c {0:s} > submission_{1:s}.log".format(f.replace("./", ""), f.replace("crab_cfg_", "").replace(".py","").replace("./", ""))
    # subprocess.Popen(args="print '{}'".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))
    subprocess.Popen(args="{}".format(cmd), shell=True, executable="/bin/zsh", env=dict(os.environ))"""
    return ret

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

def load_sample_cards(sample_cards):
    SampleList = None
    try:
        import ruamel.yaml as yaml
    except:
        print("Cannot load ruamel package to convert yaml file. Consider installing in a virtual environment with 'pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps'")
    for scard in sample_cards:
        with open(scard) as sample:
            if SampleList is None:
                SampleList = yaml.load(sample, Loader=yaml.Loader)
            else:
                SampleList.update(yaml.load(sample, Loader=yaml.Loader))
    return SampleList

if __name__ == '__main__':
    main()
