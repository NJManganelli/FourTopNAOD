from __future__ import division, print_function
import ROOT
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

class HistCloser(Module):
    def __init__(self):
        self.writeHistFile=False
    def beginJob(self,histFile=None,histDirName=None):
        if histFile != None and histDirName != None:
            self.writeHistFile=True
            # prevdir = ROOT.gDirectory
            self.histFile = histFile
            # self.histFile.cd()
            # self.dir = self.histFile.mkdir( histDirName )
            # prevdir.cd()
            # self.objs = []
    def endJob(self):
        if hasattr(self, 'objs') and self.objs != None:
            # prevdir = ROOT.gDirectory
            # self.dir.cd()
            # for obj in self.objs:
            #     obj.Write()
            # prevdir.cd()
            if hasattr(self, 'histFile') and self.histFile != None :
                self.histFile.Close()

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """Always return True to pass event through to output, close any open histogram file at the end of a series of modules"""
        return True
