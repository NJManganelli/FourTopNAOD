from __future__ import division, print_function
import os, sys
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor 
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from FourTopNAOD.Kai.tools.toolbox import *
import collections, copy, json, math
from array import array
import multiprocessing, tempfile


class EventCounter(Module):
    def __init__(self, verbose=False, isData=False):
        # self.writeHistFile=True
        self.verbose=verbose
        #event counters
        self.nPositiveEvents = 0
        self.nNegativeEvents = 0
        self.nZeroEvents = 0
        self.nEvents = 0

    # def beginJob(self,histFile=None,histDirName=None):
    #     Module.beginJob(self,histFile,histDirName)
    
    def endJob(self):
        # print("nEvents: {0}\t nPositivEvents: {1}\t nNegativeEvents: {2}\t nZeroEvents: {3}".format(
        #     self.nEvents, self.nPositiveEvents, self.nNegativeEvents, self.nZeroEvents)
        # )
        Module.endJob(self)
        

    # def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
    #     self.out = wrappedOutputTree

    def analyze(self, event): #called by the eventloop per-event
        """process event, return True (go to next module) or False (fail, go to next event)"""
        if event.genWeight > 0: self.nPositiveEvents += 1
        elif event.genWeight < 0: self.nNegativeEvents += 1
        else: self.nZeroEvents += 1
        self.nEvents += 1
        return True
Tuples = []
filesTTTT=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/BD738994-6BD2-6D41-9D93-E0AC468497A5.root"]
# files=["/eos/home-n/nmangane/AODStorage/TestingSamples/TTTT_TuneCP5_PSweights_102X.root"]
hNameTTTT="evtCounterTTTTv6.root"
hNameTTTTw="evtCounterTTTTv6w.root"
hNameTTTTabsw="evtCounterTTTTv6absw.root"
# Tuples.append((filesTTTT, hNameTTTT, 0)) #Central test configuration, no weights
Tuples.append((filesTTTT, hNameTTTTw, 1))
# Tuples.append((filesTTTT, hNameTTTTabsw, 2))

filesTT=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/80000/FB2C8D48-139E-7647-90C2-1CF1767DB0A1.root"]
hNameTT="evtCounterTTv6.root"
hNameTTw="evtCounterTTv6w.root"
hNameTTabsw="evtCounterTTv6absw.root"
# Tuples.append((filesTT, hNameTT, 0))
# Tuples.append((filesTT, hNameTTw, 1))
# Tuples.append((filesTT, hNameTTabsw, 2))
filesTTGF=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/E565691C-17D4-6046-865E-8393F1FE0414.root"]
hNameTTGF="evtCounterTTGF.root"
hNameTTGFw="evtCounterTTGFw.root"
hNameTTGFabsw="evtCounterTTGFabsw.root"
# Tuples.append((filesTTGF, hNameTTGF, 0))
Tuples.append((filesTTGF, hNameTTGFw, 1))
# Tuples.append((filesTTGF, hNameTTGFabsw, 2))

filesTT_MG=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv4/TTJets_TuneCP5_13TeV-madgraphMLM-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/90000/79097697-485B-9542-8E6B-43A747EA7F4B.root"]
hNameTT_MG="evtCounterTT_MGv6.root"
hNameTT_MGw="evtCounterTT_MGv6w.root"
hNameTT_MGabsw="evtCounterTT_MGv5v6absw.root"
# Tuples.append((filesTT_MG, hNameTT_MGw, 0))
# Tuples.append((filesTT_MG, hNameTT_MGw, 1))
# Tuples.append((filesTT_MG, hNameTT_MGabsw, 2))


def multiplier(fileList, connection):
    old_stdout = sys.stdout
    try:
        # with tempfile.NamedTemporaryFile() as fout:
        # connection.send(['Hello there!', fout.name])
        # sys.stdout = fout
        sys.stdout = open("/tmp/nmangane/" + str(os.getpid()) + ".out", "w")
        sys.stderr = open("/tmp/nmangane/" + str(os.getpid()) + "_err.out", "w")
        connection.send({'stdout': str(os.getpid()) + ".out", 'stderr': str(os.getpid()) + "_err.out"})
        if type(fileList) is str:
            fileList = [fileList]
        p=PostProcessor(".",
                        fileList,
                        modules=[EventCounter()],
                        noOut=True,
                        # branchsel='keepdrop.txt',
                        maxEntries=None,
                        firstEntry=0,
                        prefetch=False,
                        longTermCache=False,
        )
        p.run()
        connection.send({'nEvents': p.modules[0].nEvents, 'nPositiveEvents': p.modules[0].nPositiveEvents, 
                         'nNegativeEvents': p.modules[0].nNegativeEvents, 'nZeroEvents': p.modules[0].nZeroEvents})
        # print("nEvents: {0}\t nPositivEvents: {1}\t nNegativeEvents: {2}\t nZeroEvents: {3}".format(
        #     p.modules[0].nEvents, p.modules[0].nPositiveEvents, p.modules[0].nNegativeEvents, p.modules[0].nZeroEvents)
        # )
        # for line in fout:
        #     pass
    finally:
        pass
        # sys.stdout = old_stdout
    
pList = []
connList = []
# print("Tuple: " + str(Tuples))
for tup in Tuples:
    base_conn, outpost_conn = multiprocessing.Pipe()
    connList.append(base_conn)
    p = multiprocessing.Process(target=multiplier, args=(tup[0], outpost_conn,))
    pList.append(p)

for pi, p in enumerate(pList):
    p.start()

for p in pList:
    p.join()
for pi, p in enumerate(pList):
    print(connList[pi].recv())
    print(connList[pi].recv())


print("Test this outside a subprocess, now...")
sys.stdout = open("/tmp/nmangane/" + str(os.getpid()) + ".out", "w")
sys.stderr = open("/tmp/nmangane/" + str(os.getpid()) + "_err.out", "w")
p=PostProcessor(".",
                Tuples[0][0],
                modules=[EventCounter()],
                noOut=True,
                # branchsel='keepdrop.txt',
                maxEntries=None,
                firstEntry=0,
                prefetch=False,
                longTermCache=False,
)
p.run()
print("nEvents: {0}\t nPositivEvents: {1}\t nNegativeEvents: {2}\t nZeroEvents: {3}".format(
    p.modules[0].nEvents, p.modules[0].nPositiveEvents, p.modules[0].nNegativeEvents, p.modules[0].nZeroEvents))
