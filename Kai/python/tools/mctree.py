from __future__ import (division, print_function)
from FourTopNAOD.Kai.tools.intools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.tools import *
import copy
import math

def getHadFlav(pdgId):
    """Get Hadron flavour, after stripping sign information.
    
    Errors are characterized by a return value of -7, -8, -9, or -10.
    These correspond to:
        -7) receiving a non-(int, float) value for pdgId
        -8) abs(pdgId) over 99 and are in special set indicating other (i.e. pomeron, regerron)
        -9) abs(pdgId) between 9 and 100
        -10) Leading digit of abs(pdgId) after subtracting all multiples of 10000 is not in [1, 8]
        -21, -22, -23, -24, -25) Gauge Bosons, Higgs
    Technically should return value of any quark with abs(pdgId) between 1 and 8
    Technically should return value of any hadron with leading quark abs(pdgId) between 1 and 8"""
    if type(pdgId) is float:
        pdgId = int(pdgId)
    elif type(pdgId) is not int:
        return -7
    absPdgId = abs(pdgId)
    if absPdgId in set([21, 22, 23, 24, 25]):
        return -absPdgId
    #For pomeron, regerron, etc.
    #Hadrons should always have a non-zero last digit, regardless of spin (function(quark flavours) + 2*spin + 1)
    #except for K_0 Long and Short (130, 310)
    #if absPdgId > 99 and absPdgId % 10 == 0:
    if absPdgId > 99 and absPdgId in set([110,990,9900110,9900210,9900220,9900330,9900440,9902110,9902210]):
        #Special states, like pomeron, regerron, etc.
        return -8
    #Classify Mesons with additional n*(10000) by stripping
    while(absPdgId > 10000):
        absPdgId -= 10000
    #
    if absPdgId < 100:
        if 0 < absPdgId < 9:
            return absPdgId
        else:
            return -9
    else:
        calc = absPdgId // pow(10, int(math.log10(absPdgId)))
        if 0 < calc < 9:
            return calc
        else:
            return -10

class MCTree:
    """A class for storing a tree of all Gen Particles and the Particle Flow Objects linked to them.
    
    Principle structure is a dictionary where values are lists containing the keys of daughter particles, and the key is the array index of the particle in the Gen Particle Collection. PF Objects are linked by storing a string and the array index inside a string

    """
    def __init__(self, genPartCollection, muonCollection=None, 
                 electronCollection=None, tauCollection=None,
                 jetCollection=None, genJetCollection=None,
                 fatJetCollection=None, genJetAK8Collection=None, 
                 verbose=False, runLumEvt=None, debug=False, evt=None):
        
        #################
        ### The Trees ###
        #################
        self.tree = {}
        self.treeElectron = {}
        self.treeMuon = {}
        self.treeTau = {}
        self.treeJet = {}
        self.treeGenJet = {}
        self.treeFatJet = {}
        self.treeSubJet = {}
        self.treeGenJetAK8 = {}
        self.treeSubGenJetAK8 = {}
        self.treeJetTuple = {}
        self.treeGenJetTuple = {}
        self.treeFatJetTuple = {}
        self.treeSubJetTuple = {}
        self.treeGenJetAK8Tuple = {}
        self.treeSubGenJetAK8Tuple = {}
        
        ##############################
        ### Gen and PF Collections ###
        ##############################
        
        self.event = evt
        self.gens = genPartCollection
        self.muons = muonCollection
        self.electrons = electronCollection
        self.taus = tauCollection
        self.jets = jetCollection
        self.genjets = genJetCollection
        self.fatjets = fatJetCollection
        self.genfatjets = genJetAK8Collection
        #verbose option for some extra information
        self.verbose = verbose
        self.debug = debug
        self.rLE = runLumEvt
        #Keys for bits
        self.bits = {'isPrompt':0b000000000000001,
                     'isDecayedLeptonHadron':0b000000000000010,
                     'isTauDecayProduct':0b000000000000100,
                     'isPromptTauDecayProduct':0b000000000001000,
                     'isDirectTauDecayProduct':0b000000000010000,
                     'isDirectPromptTauDecayProduct':0b000000000100000,
                     'isDirectHadronDecayProduct':0b000000001000000,
                     'isHardProcess':0b000000010000000,
                     'fromHardProcess':0b000000100000000,
                     'isHardProcessTauDecayProduct':0b000001000000000,
                     'isDirectHardProcessTauDecayProduct':0b000010000000000,
                     'fromHardProcessBeforeFSR':0b000100000000000,
                     'isFirstCopy':0b001000000000000,
                     'isLastCopy':0b010000000000000,
                     'isLastCopyBeforeFSR':0b100000000000000
                    }
        
        ######################
        ### Sort Functions ###
        ######################
        self.sortByAbsId = lambda a : abs(self.gens[a].pdgId)
        self.sortByPt = lambda p : self.gens[p].pdgId
        self.sortByP3 = lambda p : self.gens[p].p4().P()
        self.sortByE = lambda p : self.gens[p].p4().E()
        self.sortByNDau = lambda k : len(self.tree[k])
        self.noSort = None
        
        
        ##########################
        ### Top Classification ###
        ##########################
        self.t_head = {} #0-indexed dictionary that stores the index of the first copy of each top quark
        self.t_first = {}
        self.t_last = {}
        self.t_rad = {} #Any extra radiated particles
        self.t_first_desc = {} #all descendants, superset of tb_desc, tW_dau1_desc, tW_dau2_desc; includes pre-decay radiation
        self.t_last_desc = {} #As t_first_desc, but only those after the top decays
        self.tb_first = {} #first b (or down-type quark) daughter of the top
        self.tb_last = {}
        self.tb_desc = {} #all descendants, including the lepton
        self.tb_hadleps = {} #store list of stable massive leptons associated with the b quark (electron or muon)
        self.tW_first = {}
        self.tW_last = {}
        self.tW_dau1_first = {} #Preferentially massive lepton or down-type quark (odd, lower abs pdg id)
        self.tW_dau1_last = {}
        self.tW_dau1_desc = {}
        self.tW_dau2_first = {} #Neutrinos and up-type quarks (even, higher abs pddg id)
        self.tW_dau2_last = {}
        self.tW_dau2_desc = {}
        self.tW_hadleps = {} #For storing stable massive leptons arising during a hadronic W decay (electron, muon)
        self.tWTau_dauArr_first = {} #For Tau decays
        self.tWTau_dauArr_last = {}
        self.tWTau_dauArr_desc = {}
        self.tWTau_mLep_first = {}
        self.tWTau_mLep_last = {}
        self.tWTau_mLep_desc = {}
        self.tHasWDauElectron = {}
        self.tHasWDauMuon = {}
        self.tHasWDauTau = {}
        self.tHasAnyHadronicTau = {}
        self.tHasHadronicWDauTau = {}
        self.tHasHadronicW = {}
        self.tIsLeptonic = {}
        
        ##############################
        ### W Boson Classification ###
        ##############################
        self.W_head = {} #0-indexed dictionary that stores the index of the first copy of each W Boson not descended from top
        
        ##############################
        ### Z Boson Classification ###
        ##############################
        self.Z_head = {} #0-indexed dictionary that stores the index of the first copy of each Z Boson
        
        ##################################
        ### Higgs Boson Classification ###
        ##################################
        self.H_head = {} #0-indexed dictionary that stores the index of the first copy of each Higgs Boson
        
        #dumpGenCollection(self.gens)
        #self.initializeTrees()
        #self.buildGenTree()

        #_ = self.buildPFTrees()
        #self.printGenNode(nodeKey=-1)
        #self.pprintGenNode(nodeKey=-1)
        #self.buildTopSubtree()
        
        
    def initializeTrees(self):
        """To initialize the tree safely, in case of a Gen Particle structure that references parents with larger Idx."""
        #Initialize tree value for parentless particles (initial partons should always be linked here)
        if self.verbose:
            print("MCTree is initializing the tree with empty arrays")
        self.tree[-1] = []
        for Idx in xrange(len(self.gens)):
            self.tree[Idx] = []
            self.treeElectron[Idx] = []
            self.treeMuon[Idx] = []
            self.treeTau[Idx] = []
            self.treeJet[Idx] = []
            self.treeGenJet[Idx] = []
            self.treeFatJet[Idx] = []
            self.treeGenJetAK8[Idx] = []
            #self.treeSubJet[Idx] = []
            #self.treeSubGenJetAK8[Idx] = []
            self.treeJetTuple[Idx] = []
            self.treeGenJetTuple[Idx] = []
            self.treeFatJetTuple[Idx] = []
            self.treeGenJetAK8Tuple[Idx] = []
            #self.treeSubJetTuple[Idx] = []
            #self.treeSubGenJetAK8Tuple[Idx] = []

            
    def buildGenTree(self):
        """Build the Gen Tree by storing descendants' indices in lists associated with the parent index, forming key-value pairs.
        
        For example, a particle with Idx=5 with descendants 9, 14, 15, 87 would be stored as { 5:[9, 14, 15, 87] }.
        This only contains the direct descendants, forming a tree structure.
        PF Candidates are stored with non-integer format.
        """
        if self.verbose:
            print("MCTree is building the Gen Particle tree")
        for Idx, gen in enumerate(self.gens):
            self.tree[gen.genPartIdxMother].append(Idx)
            if abs(gen.pdgId) == 6 and abs(self.gens[gen.genPartIdxMother].pdgId) != 6:
                self.t_head[len(self.t_head)] = Idx
            if abs(gen.pdgId) == 23 and abs(self.gens[gen.genPartIdxMother].pdgId) != 23:
                self.Z_head[len(self.Z_head)] = Idx
            if abs(gen.pdgId) == 24 and abs(self.gens[gen.genPartIdxMother].pdgId) not in set([6, 24]):
                self.W_head[len(self.W_head)] = Idx
            if abs(gen.pdgId) == 25 and abs(self.gens[gen.genPartIdxMother].pdgId) != 25:
                self.H_head[len(self.H_head)] = Idx
        #Sort the tree by abs(PDG ID), except the initial pp interaction
        for nodekey, node in self.tree.iteritems():
            if len(node) > 1:
                if nodekey > -1:
                    #sort all nodes descended from initial pp interaction by absolute value of pdgId, smallest first
                    node.sort(key=self.sortByAbsId, reverse=False)
                else:
                    #Sort the -1 node by key-value, so that the 0 node prints first
                    node.sort(key=lambda n : n, reverse=False)

    def LW_buildGenTree(self):
        """(LightWeight - more optimized version) Build the Gen Tree by storing descendants' indices in lists associated with the parent index, forming key-value pairs.
        
        For example, a particle with Idx=5 with descendants 9, 14, 15, 87 would be stored as { 5:[9, 14, 15, 87] }.
        This only contains the direct descendants, forming a tree structure.
        PF Candidates are stored with non-integer format.
        """
        if self.verbose:
            print("MCTree is building the Gen Particle tree")
        for Idx in xrange(self.event.nGenPart):
            pdgid = abs(self.event.GenPart_pdgId[Idx])
            moidx = self.event.GenPart_genPartIdxMother[Idx]
            if moidx > -1:
                mpdgid = abs(self.event.GenPart_pdgId[moidx])
            else:
                mpdgid = -999
            self.tree[moidx].append(Idx)
            if pdgid == 6 and mpdgid != 6:
                self.t_head[len(self.t_head)] = Idx
            if pdgid == 23 and mpdgid != 23:
                self.Z_head[len(self.Z_head)] = Idx
            if pdgid == 24 and mpdgid not in set([6, 24]):
                self.W_head[len(self.W_head)] = Idx
            if pdgid == 25 and mpdgid != 25:
                self.H_head[len(self.H_head)] = Idx
        #Sort the tree by abs(PDG ID), except the initial pp interaction
        for nodekey, node in self.tree.iteritems():
            if len(node) > 1:
                if nodekey > -1:
                    #sort all nodes descended from initial pp interaction by absolute value of pdgId, smallest first
                    node.sort(key=self.sortByAbsId, reverse=False)
                else:
                    #Sort the -1 node by key-value, so that the 0 node prints first
                    node.sort(key=lambda n : n, reverse=False)

                    
    def getMCTree(self, returnCopy=True):
        """Return the MC Tree dictionary.

        Default option of returnCopy=True returns a copy.copy() of the tree, so that it can be modified without affecting the class's internal tree."""
        if returnCopy:
            return copy.copy(self.tree)
        else:
            return self.tree
        
    def buildPFTrees(self, dRforAK4=0.4, dRforAK8=0.8, onlyBuildDaughterless=True, onlyUseClosest=False):
        """Build trees for Particle Flow objects, including leptons and jets.

        Loops through the gen particles and stores the index of leptons and jets.
        dRforAK4 is the maximum DeltaR for AK4 Jets
        dRforAK8 is the maximum DeltaR for AK8 Jets
        onlyBuildDaughterless specifies whether a gen particle that decays to other gen particles should be matched against any jets (does not affect lepton matching)
        onlyUseClosest specifies whether a gen particle can match to multiple jets within small enough DeltaR (overlap), or should only store the index of the closest for each jet type
        """
        #Direct link electrons, muons, taus
        if self.electrons:
            for eidx, ele in enumerate(self.electrons):
                genIdx = ele.genPartIdx
                if -1 < genIdx < len(self.gens):
                    self.treeElectron[genIdx].append(eidx)
        if self.muons:
            for midx, muon in enumerate(self.muons):
                genIdx = muon.genPartIdx
                if -1 < genIdx < len(self.gens):
                    self.treeMuon[genIdx].append(midx)
        if self.taus:
            for tauidx, tau in enumerate(self.taus):
                genIdx = tau.genPartIdx
                if -1 < genIdx < len(self.gens):
                    self.treeTau[genIdx].append(tauidx)
                
        for Idx, gen in enumerate(self.gens):
            #Skip neutrinos
            if abs(gen.pdgId) in set([12,14,16]): 
                continue
            if onlyBuildDaughterless and len(self.tree[Idx]) > 0: continue
            if onlyUseClosest:
                if self.jets:
                    dRmin = 999
                    closestJidx = -1
                    for jidx, jet in enumerate(self.jets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRmin and dRtest < dRforAK4:
                            dRmin = copy.copy(dRtest)
                            closestJidx = jidx
                    if closestJidx > -1: 
                        self.treeJet[Idx].append(closestJidx)
                        self.treeJetTuple[Idx].append( (closestJidx, dRmin) )
                if self.genjets:
                    dRmin = 999
                    closestJidx = -1
                    for jidx, jet in enumerate(self.genjets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRmin and dRtest < dRforAK4:
                            dRmin = copy.copy(dRtest)
                            closestJidx = jidx
                    if closestJidx > -1: 
                        self.treeGenJet[Idx].append(closestJidx)
                        self.treeGenJetTuple[Idx].append( (closestJidx, dRmin) )
                if self.fatjets:
                    dRmin = 999
                    closestJidx = -1
                    for jidx, jet in enumerate(self.fatjets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRmin and dRtest < dRforAK8:
                            dRmin = copy.copy(dRtest)
                            closestJidx = jidx
                    if closestJidx > -1: 
                        self.treeFatJet[Idx].append(closestJidx)
                        self.treeFatJetTuple[Idx].append( (closestJidx, dRmin) )
                if self.genfatjets:
                    dRmin = 999
                    closestJidx = -1
                    for jidx, jet in enumerate(self.genfatjets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRmin and dRtest < dRforAK8:
                            dRmin = copy.copy(dRtest)
                            closestJidx = jidx
                    if closestJidx > -1: 
                        self.treeGenJetAK8[Idx].append(closestJidx)
                        self.treeGenJetAK8Tuple[Idx].append( (closestJidx, dRmin) )
            else:
                if self.jets:
                    for jidx, jet in enumerate(self.jets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRforAK4:
                            self.treeJet[Idx].append(jidx)
                            self.treeJetTuple[Idx].append( (jidx, dRtest) )
                if self.genjets:
                    for jidx, jet in enumerate(self.genjets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRforAK4:
                            self.treeGenJet[Idx].append(jidx)
                            self.treeGenJetTuple[Idx].append( (jidx, dRtest) )
                if self.fatjets:
                    for jidx, jet in enumerate(self.fatjets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRforAK8:
                            self.treeFatJet[Idx].append(jidx)
                            self.treeFatJetTuple[Idx].append( (jidx, dRtest) )
                if self.genfatjets:
                    for jidx, jet in enumerate(self.genfatjets):
                        dRtest = deltaR(gen, jet)
                        if dRtest < dRforAK8:
                            self.treeGenJetAK8[Idx].append(jidx)
                            self.treeGenJetAK8Tuple[Idx].append( (jidx, dRtest) )

    def getPFTrees(self, returnCopy=True):
        """Return the PF Tree dictionaries inside a dictionary.

        Default option of returnCopy=True returns a copy.copy() of the trees, so that they can be modified without affecting the class's internal trees."""

        if returnCopy:
            return { 'treeJet': copy.copy(self.treeJet),
                     'treeGenJet': copy.copy(self.treeGenJet),
                     'treeFatJet': copy.copy(self.treeFatJet),
                     'treeGenJetAK8': copy.copy(self.treeGenJetAK8),
                     'treeJetTuple': copy.copy(self.treeJetTuple),
                     'treeGenJetTuple': copy.copy(self.treeGenJetTuple),
                     'treeFatJetTuple': copy.copy(self.treeFatJetTuple),
                     'treeGenJetAK8Tuple': copy.copy(self.treeGenJetAK8Tuple)}
        else:
            return { 'treeJet': self.treeJet,
                     'treeGenJet': self.treeGenJet,
                     'treeFatJet': self.treeFatJet,
                     'treeGenJetAK8': self.treeGenJetAK8,
                     'treeJetTuple': self.treeJetTuple,
                     'treeGenJetTuple': self.treeGenJetTuple,
                     'treeFatJetTuple': self.treeFatJetTuple,
                     'treeGenJetAK8Tuple': self.treeGenJetAK8Tuple}
              
    def unbrokenDescent(self, Idx, chain=None, sortkey=None, sortreverse=True, chooseLongestChain=True):
        if not sortkey:
            sortkey = self.noSort
        if not chain:
            chain = []
            chain.append(Idx)
        if -1 < Idx < len(self.gens):
            Id = self.gens[Idx].pdgId
            candidates = copy.copy(self.tree[Idx])
            candidates = [c for c in candidates if self.gens[c].pdgId == Id]
            if len(candidates) == 1:
                chain.append(candidates[0])
                return self.unbrokenDescent( candidates[0], chain=chain, sortkey=sortkey, 
                                            sortreverse=sortreverse, chooseLongestChain=chooseLongestChain)
            elif len(candidates) > 1:
                #candidates.sort(key=lambda d : getattr(self.gens[d], sortkey), reverse=sortreverse)
                if sortkey:
                    #Sort now, to propogate sortkey preferences as secondary on top of chooseLongestChain if enabled
                    candidates.sort(key=sortkey, reverse=sortreverse)
                    if self.debug: 
                        print("Sorting engaged, Captain! The key is: " + str(sortkey))
                        print(candidates)
                if chooseLongestChain:
                    potentiates = []
                    for cand in candidates:
                        #Create new chains for each candidate, since using append everywhere 
                        subChain = copy.copy(chain)
                        #Add this candidate to the list itself
                        subChain.append(cand)
                        poten = self.unbrokenDescent( cand, chain=subChain, sortkey=sortkey, 
                                            sortreverse=sortreverse, chooseLongestChain=chooseLongestChain)
                        if poten[0]:
                            potentiates.append(poten[1])
                    potentiates.sort(key=lambda p : len(p), reverse=True)
                    if self.debug:
                        print("The potentiates are: " + str(potentiates))
                    return (len(potentiates[0]) > 0, potentiates[0])
                else:
                    #Choose first candidate from sorted list above
                    chain.append(candidates[0])
                    return self.unbrokenDescent(candidates[0], chain=chain, sortkey=sortkey,
                                                sortreverse=sortreverse, chooseLongestChain=chooseLongestChain)
            else:
                #Set return bool to len(chain) > 0, to see if something was found (including itself, corresponding to len()==1)
                return (len(chain) > 0, chain)
                
        else:
            return (False, chain)
        
    def anyDescent(self, Idx, descTree=None, sortkey=None, sortreverse=False, onlyDaughterless=False, includeSelf=True):
        """Method for finding the descendants of a gen particle given its index inside the collection.
        
        sortkey can be a function by which they particles are sorted at the end, before returning them as a list.
        sortreverse is the boolean passed to the reverse option in list.sort().
        onlyDaughterless option only appends indices of descendants that have no gen daughters themselves.
        includeSelf is an option that is defaulted to True, and thus the list will return the index of the called particle
        if it has no daughters. This is set to False for recursion to prevent overcounting without resorting to sets.
        """
        #Default sort method
        if not sortkey:
            sortkey = self.noSort
        if descTree is None:
            descTree = []
        if -1 < Idx < len(self.gens):
            candidates = copy.copy(self.tree[Idx])
            if includeSelf:
                if onlyDaughterless:
                    if len(candidates) == 0:
                        descTree.append(Idx)
                else:
                    descTree.append(Idx)
            #print("candidates = " + str(candidates))
            for cand in candidates:
                if onlyDaughterless:
                    if len(self.tree[cand]) == 0:
                        descTree.append(cand)
                else:
                    descTree.append(cand)
                #Call recursively on all daughters in the list, turning off includeSelf to avoid double counting
                _ = self.anyDescent(cand, descTree=descTree, sortkey=sortkey, 
                               sortreverse=sortreverse, onlyDaughterless=onlyDaughterless, includeSelf=False)
            descTree.sort(key=sortkey, reverse=sortreverse)
            return descTree
        else:
            return []
        
    def buildTopSubtree(self):
        """Method to recontstruct nodes of the top decays.

        Calls several submethods:
        linkTops()
        linkTopDaughters()
        linkWDaughters()
        linkTauDaughters()
        linkBDescendants()
        linkWDescendants()
        linkTauDescendants()
        evaluateLeptonicity()
        evaluateHadronicityWithVoting()
        """
        if self.verbose:
            print("MCTree is building the Top Subtree")
            print(self.t_head)
        __ = self.linkTops()
        ___ = self.linkTopDaughters()
        ____ = self.linkWDaughters()
        _____ = self.linkTauDaughters()
        ______ = self.linkBDescendants()
        _______ = self.linkWDescendants()
        ________ = self.linkTauDescendants()
        LepTopDict = self.evaluateLeptonicity()
        TopJetDict = self.evaluateHadronicityWithVoting()
        
            
    def linkTops(self, returnSuccess=True, returnCopy=True):
        if self.verbose:
            print("MCTree is linking the Tops")
        #Link last tops
        in_tp = {}
        for tidx in self.t_head.values():
            self.t_first[tidx] = tidx
            tp = self.unbrokenDescent(tidx, chooseLongestChain=True)
            in_tp[tidx] = tp
            if tp[0]:
                self.t_last[tidx] = tp[1][-1]
        if returnSuccess:
            return True
        elif returnCopy:
            return {'t_first': copy.copy(self.t_first), 't_last': copy.copy(self.t_last), 'in_tp': copy.copy(in_tp)}
        else:
            return {'t_first': self.t_first, 't_last': self.t_last, 'in_tp': in_tp}
                
    def linkTopDaughters(self, returnSuccess=True, returnCopy=True):
        if self.verbose:
            print("MCTree is linking the Top daughters")
        #All internals for debugging and returning
        daughters = {}
        downtypes = {}
        Wtypes = {}
        dtp = {}
        wp = {}
        
        #Link top's b and W daughters
        for tidx, dnode in self.t_last.iteritems():
            daughters[tidx] = copy.copy(self.tree[dnode])
            downtypes[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([1,3,5])]
            Wtypes[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) == 24]
            if len(downtypes[tidx]) == 1:
                self.tb_first[tidx] = downtypes[tidx][0]
            elif len(downtypes[tidx]) > 1:
                downtypes[tidx].sort(key =self.sortByAbsId, reverse=True)
                print("Downtypes Highest first check: " + str([(down, self.gens[down].pdgId) for down in downtypes[tidx]]))
                self.tb_first[tidx] = downtypes[tidx][0]
            else:
                raise NotImplementedError("buildTopSubtree has encountered last top without a down-type quark daughter")
            if len(Wtypes) == 1:
                self.tW_first[tidx] = Wtypes[tidx][0]
            elif len(Wtypes) > 1:
                Wtypes[tidx].sort(key=self.sortByNDau, reverse=True)
                self.tW_first[tidx] = Wtypes[tidx][0]
            else:
                raise NotImplementedError("buildTopSubtree has encountered last top without a W daughter")
            
        #Link last down-type quark
        for tidx, dtidx in self.tb_first.iteritems():
            dtp[tidx] = self.unbrokenDescent(dtidx, chooseLongestChain=True)
            if dtp[tidx][0]:
                self.tb_last[tidx] = dtp[tidx][1][-1]
                
        #Link last W boson
        for tidx, widx in self.tW_first.iteritems():
            wp[tidx] = self.unbrokenDescent(widx, chooseLongestChain=True)
            if wp[tidx][0]:
                self.tW_last[tidx] = wp[tidx][1][-1]
            
        if returnSuccess:
            return True
        elif returnCopy:
            return {'tb_first': copy.copy(self.tb_first), 'tb_last': copy.copy(self.tb_last),
                    'tW_first': copy.copy(self.tW_first), 'tW_last': copy.copy(self.tW_last),
                    'daughters': copy.copy(daughters), 'downtypes': copy.copy(downtypes),
                    'Wtypes': copy.copy(Wtypes), 'dtp': copy.copy(dtp), 'wp': copy.copy(wp)}
        else:
            return {'tb_first': self.tb_first, 'tb_last': self.tb_last,
                    'tW_first': self.tW_first, 'tW_last': self.tW_last,
                    'daughters': daughters, 'downtypes': downtypes,
                    'Wtypes': Wtypes, 'dtp': dtp, 'wp': wp}
        
    def linkWDaughters(self, returnSuccess=True, returnCopy=True):
        if self.verbose:
            print("MCTree is linking the Top W daughters")
        #internal variables for return
        daughters = {}
        massiveleps = {}
        neutrinos = {}
        downtypes = {}
        uptypes = {}
        nLep = {}
        nQuark = {}
        dau1p = {}
        dau2p = {}
        
        #Link W's daughters
        for tidx, dnode in self.tW_last.iteritems():
            daughters[tidx] = copy.copy(self.tree[dnode])
            massiveleps[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([11,13,15])]
            neutrinos[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([12, 14, 16])]
            downtypes[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([1,3,5])]
            uptypes[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([2,4,6])]
            nLep[tidx] = len(massiveleps[tidx]) + len(neutrinos[tidx])
            nQuark[tidx] = len(downtypes[tidx]) + len(uptypes[tidx])
            
            if self.debug:
                print("tW_last: " + str(self.tW_last))
                print("Last W Daughters: " + str(daughters[tidx]))
                print("Massive Leptons: " + str(massiveleps[tidx]))
                print("Neutrinos: " + str(neutrinos[tidx]))
                print("Downtype quarks: " + str(downtypes[tidx]))
                print("Uptype quarks: " + str(uptypes[tidx]))
                print("nLep: " + str(nLep[tidx]))
                print("nQuark: " + str(nQuark[tidx]))
                
            if nLep[tidx] + nQuark[tidx] != len(daughters[tidx]):
                raise NotImplementedError("buildTopSubtree() has no method for handling W decay into non quark/lepton states")
            elif nLep[tidx] == 2:
                if nQuark[tidx] > 0: 
                    raise NotImplementedError("buildTopSubtree() has no method for handling mixed lep/had W decay")
                self.tHasHadronicW[tidx] = False
                self.tW_dau1_first[tidx] = massiveleps[tidx][0]
                self.tW_dau2_first[tidx] = neutrinos[tidx][0]
                if abs(self.gens[massiveleps[tidx][0]].pdgId) == 11:
                    self.tHasWDauElectron[tidx] = True
                    self.tHasWDauMuon[tidx] = False
                    self.tHasWDauTau[tidx] = False
                    self.tHasAnyHadronicTau[tidx] = False
                    self.tHasHadronicWDauTau[tidx] = False
                elif abs(self.gens[massiveleps[tidx][0]].pdgId) == 13:
                    self.tHasWDauElectron[tidx] = False
                    self.tHasWDauMuon[tidx] = True
                    self.tHasWDauTau[tidx] = False
                    self.tHasAnyHadronicTau[tidx] = False
                    self.tHasHadronicWDauTau[tidx] = False
                elif abs(self.gens[massiveleps[tidx][0]].pdgId) == 15:
                    self.tHasWDauElectron[tidx] = False
                    self.tHasWDauMuon[tidx] = False
                    self.tHasWDauTau[tidx] = True
                    self.tHasAnyHadronicTau[tidx] = "EvaluationIncomplete"
                    self.tHasHadronicWDauTau[tidx] = "EvaluationIncomplete"
                else:
                    raise RuntimeError("buildTopSubtree() has failed a logic check! (LEP)")
            elif nQuark[tidx] == 2:
                if nLep[tidx] > 0: 
                    raise NotImplementedError("buildTopSubtree() has no method for handling mixed had/lep W decay")
                self.tHasHadronicW[tidx] = True
                self.tHasHadronicWDauTau[tidx] = False
                self.tHasAnyHadronicTau[tidx] = "EvaluationIncomplete"
                self.tHasWDauElectron[tidx] = False
                self.tHasWDauMuon[tidx] = False
                self.tHasWDauTau[tidx] = False
                self.tW_dau1_first[tidx] = downtypes[tidx][0]
                self.tW_dau2_first[tidx] = uptypes[tidx][0]
                
        #Link last W daughters
        for tidx, didx in self.tW_dau1_first.iteritems():
            #Get the result of unbrokenDescent, where element 0 is boolean and element 1 is the list of indices
            dau1p[tidx] = self.unbrokenDescent(didx, sortkey=self.sortByNDau, sortreverse=True, chooseLongestChain=True)
            if dau1p[tidx][0]:
                #Get the last index in the list, corresponding to last descendent of same pdgId
                #print("last W 1 Dau: " + str(dau1p[tidx][1][-1]))
                self.tW_dau1_last[tidx] = dau1p[tidx][1][-1]
        for tidx, didx in self.tW_dau2_first.iteritems():
            dau2p[tidx] = self.unbrokenDescent(didx, sortkey=self.sortByNDau, sortreverse=True, chooseLongestChain=True)
            if dau2p[tidx][0]:
                self.tW_dau2_last[tidx] = dau2p[tidx][1][-1]
            
        if returnSuccess:
            return True
        elif returnCopy:
            return {'tW_dau1_first': copy.copy(self.tW_dau1_first), 'tW_dau1_last': copy.copy(self.tW_dau1_last),
                    'tW_dau2_first': copy.copy(self.tW_dau2_first), 'tW_dau2_last': copy.copy(self.tW_dau2_last),
                    'daughters': copy.copy(daughters), 'massiveleps': copy.copy(massiveleps),
                    'neutrinos': copy.copy(neutrinos), 'downtypes': copy.copy(downtypes),
                    'uptypes': copy.copy(uptypes), 'nLep': copy.copy(nLep), 'nQuark': copy.copy(nQuark),
                    'dau1': copy.copy(dau1p), 'dau2': copy.copy(dau2p)}
        else:
            return {'tW_dau1_first': self.tW_dau1_first, 'tW_dau1_last': self.tW_dau1_last,
                    'tW_dau2_first': self.tW_dau2_first, 'tW_dau2_last': self.tW_dau2_last,
                    'daughters': daughters, 'massiveleps': massiveleps,
                    'neutrinos': neutrinos, 'downtypes': downtypes,
                    'uptypes': uptypes, 'nLep': nLep, 'nQuark': nQuark, 'dau1': dau1p, 'dau2': dau2p}
         
    def linkTauDaughters(self, returnSuccess=True, returnCopy=True):
        if self.verbose:
            print("MCTree is linking the Top W-Tau daughters")
        #internal variables
        daughters = {}
        daughterIds = {}
        massiveleps = {}
        neutrinos = {}
        photons = {}
        downtypes = {}
        uptypes = {}
        Bhadrons = {}
        Chadrons = {}
        Lighthadrons = {}
        nLep = {}
        nHad = {}
        nDau = {}
        nPho = {}
        
        #Link Tau daughters if present
        for tidx, dnode in self.tW_dau1_last.iteritems():
            if self.tHasWDauTau[tidx]:
                daughters[tidx] = copy.copy(self.tree[dnode])
                daughterIds[tidx] = [self.gens[dau].pdgId for dau in daughters[tidx]]
                massiveleps[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([11,13,15])]
                neutrinos[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([12, 14, 16])]
                photons[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) == 22]
                downtypes[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([1,3,5])]
                uptypes[tidx] = [dau for dau in daughters[tidx] if abs(self.gens[dau].pdgId) in set([2,4,6])]
                Bhadrons[tidx] = [dau for dau in daughters[tidx] if getHadFlav(self.gens[dau].pdgId) == 5]
                Chadrons[tidx] = [dau for dau in daughters[tidx] if getHadFlav(self.gens[dau].pdgId) == 4]
                Lighthadrons[tidx] = [dau for dau in daughters[tidx] if getHadFlav(self.gens[dau].pdgId) in set([3, 2, 1])]
                
                nLep[tidx] = len(massiveleps[tidx]) + len(neutrinos[tidx])
                nHad[tidx] = len(downtypes[tidx]) + len(uptypes[tidx]) + len(Bhadrons[tidx])\
                                + len(Chadrons[tidx]) + len(Lighthadrons[tidx])
                nPho[tidx] = len(photons[tidx])
                nDau[tidx] = len(daughters[tidx])
                
                #Store list of all daughters, first and last, and an empty list for each one 
                #FIXME: Replace empty list with all daughter-less descendents of each daughter from the tau
                self.tWTau_dauArr_first[tidx] = daughters[tidx]
                self.tWTau_dauArr_last[tidx] = [self.unbrokenDescent(didx, sortkey=self.sortByNDau, 
                                                                     sortreverse=True, chooseLongestChain=True
                                                                    )[1] for didx in self.tWTau_dauArr_first[tidx]]
                self.tWTau_dauArr_desc[tidx] = [ [] for dau in self.tWTau_dauArr_first[tidx] ]
                
                #Tau leptonic decays are marked by 3 leptons, one massive and two neutrinos. 
                if nLep[tidx] >= 3 and len(massiveleps[tidx]) > 0:
                    self.tHasHadronicWDauTau[tidx] = False
                    self.tWTau_mLep_first[tidx] = massiveleps[tidx][0]
                    self.tWTau_mLep_last[tidx] = self.unbrokenDescent(massiveleps[tidx][0],
                                                                      sortkey=self.sortByE, sortreverse=True,
                                                                      chooseLongestChain=True)[1][0]
                    self.tWTau_mLep_desc[tidx] = []
                #This will be a hadronic Tau
                else:
                    self.tHasHadronicWDauTau[tidx] = True
                    self.tWTau_mLep_first[tidx] = -1
                    self.tWTau_mLep_last[tidx] = -1
                    self.tWTau_mLep_desc[tidx] = []  
                
            else:
                #Null the Tau daughter information if no Tau directly from last W
                self.tWTau_dauArr_first[tidx] = [] #list of lists
                self.tWTau_dauArr_last[tidx] = []
                self.tWTau_dauArr_desc[tidx] = []
                self.tWTau_mLep_first[tidx] = -1
                self.tWTau_mLep_last[tidx] = -1
                self.tWTau_mLep_desc[tidx] = []
        if returnSuccess:
            return True
        elif returnCopy:
            return {'daughters': copy.copy(daughters), 'massiveleps': copy.copy(massiveleps),
                    'neutrinos': copy.copy(neutrinos), 'downtypes': copy.copy(downtypes),
                    'uptypes': copy.copy(uptypes), 'Bhadrons': copy.copy(Bhadrons),
                    'Chadrons': copy.copy(Chadrons), 'Lighthadrons': copy.copy(Lighthadrons),
                    'daughterIds': copy.copy(daughterIds), 'nLep': copy.copy(nLep),
                    'nHad': copy.copy(nHad), 'nDau': copy.copy(nDau), 'nPho': copy.copy(nPho)}
        else:
            return {'daughters': daughters, 'massiveleps': massiveleps,
                    'neutrinos': neutrinos, 'downtypes': downtypes,
                    'uptypes': uptypes, 'Bhadrons': Bhadrons,
                    'Chadrons': Chadrons, 'Lighthadrons': Lighthadrons,
                    'daughterIds': daughterIds, 'nLep': nLep,
                    'nHad': nHad, 'nDau': in_nDau, 'nPho': nPho}
        
    def linkBDescendants(self, returnSuccess=True, returnCopy=True):
        for tidx, dnode in self.tb_first.iteritems():
            self.tb_hadleps[tidx] = []
            self.tb_desc[tidx] = self.anyDescent(dnode, sortkey=self.sortByE, sortreverse=True, onlyDaughterless=True)
            for desc in self.tb_desc[tidx]:
                if abs(self.gens[desc].pdgId) in set([11, 13]):
                    self.tb_hadleps[tidx].append(desc)
        if returnSuccess:
            return True
        elif returnCopy:
            return {'tb_desc': copy.copy(self.tb_desc), 'tb_hadleps': copy.copy(self.tb_hadleps)}
        else:
            return {'tb_desc': self.tb_desc, 'tb_hadleps': self.tb_hadleps}
                    
    def linkWDescendants(self, returnSuccess=True, returnCopy=True):
        for tidx, d1node in self.tW_dau1_last.iteritems():
            self.tW_hadleps[tidx] = [] #Empty list for hadronic leptons from the W
            self.tW_dau1_desc[tidx] = self.anyDescent(d1node, sortkey=self.sortByE, sortreverse=True, onlyDaughterless=True)
            #If tHasHadronicW is not true, there will not be an empty list to append to from link Daughters methods
            if self.tHasHadronicW[tidx]:   
                for desc in self.tW_dau1_desc[tidx]:
                    if abs(self.gens[desc].pdgId) in set([11, 13]):
                        self.tW_hadleps[tidx].append(desc)
        for tidx, d2node in self.tW_dau2_last.iteritems():
            self.tW_dau2_desc[tidx] = self.anyDescent(d2node, sortkey=self.sortByE, sortreverse=True, onlyDaughterless=True)
            if self.tHasHadronicW[tidx]:   
                for desc in self.tW_dau2_desc[tidx]:
                    if abs(self.gens[desc].pdgId) in set([11, 13]):
                        self.tW_hadleps[tidx].append(desc)
        if returnSuccess:
            return True
        elif returnCopy:
            return {'tW_dau1_desc': copy.copy(self.tW_dau1_desc), 'tW_dau2_desc': copy.copy(self.tW_dau2_desc),
                    'tW_hadleps': copy.copy(self.tW_hadleps)}
        else:
            return {'tW_dau1_desc': self.tW_dau1_desc, 'tW_dau2_desc': self.tW_dau2_desc,
                    'tW_hadleps': self.tW_hadleps}
      
    def linkAllTopDescendants(self, returnSuccess=True, returnCopy=True):
        for tidx, dnode in self.t_first.iteritems():
            self.t_first_desc[tidx] = self.anyDescent(dnode, sortkey=self.sortByE, sortreverse=True, onlyDaughterless=True)
        for tidx, dnode in self.t_last.iteritems():
            self.t_last_desc[tidx] = self.anyDescent(dnode, sortkey=self.sortByE, sortreverse=True, onlyDaughterless=True)
        if returnSuccess:
            return True
        elif returnCopy:
            return {'t_first_desc': copy.copy(self.t_first_desc), 't_last_desc': copy.copy(self.t_last_desc)}
        else:
            return {'t_first_desc': self.t_first_desc, 't_last_desc': self.t_last_desc}
        
    def linkTauDescendants(self, returnSuccess=True, returnCopy=True):
        for tidx, dnode in self.tW_dau1_last.iteritems():
            if self.tHasWDauTau[tidx]:
                for dNum, dau in enumerate(self.tWTau_dauArr_first[tidx]):
                    self.tWTau_dauArr_desc[tidx][dNum] = self.anyDescent(dau, sortkey=self.sortByE, 
                                                                         sortreverse=True, onlyDaughterless=True)
                self.tWTau_mLep_desc[tidx] = self.anyDescent(self.tWTau_mLep_last[tidx], sortkey=self.sortByE, 
                                                                         sortreverse=True, onlyDaughterless=True)
       
        if returnSuccess:
            return True
        elif returnCopy:
            return {'tWTau_dauArr_desc': copy.copy(self.tWTau_dauArr_desc), 'tWTau_mLep_desc': copy.copy(self.tWTau_mLep_desc)}
        else:
            return {'tWTau_dauArr_desc': self.tWTau_dauArr_desc, 'tWTau_mLep_desc': self.tWTau_mLep_desc}
        
    def evaluateLeptonicity(self, returnCopy=True):
        nEle = 0
        nMuon = 0
        nLepTau = 0
        nHadTau = 0
        nHad = 0
        nLep = 0
        for tidx, dnode in self.t_last.iteritems():
            if self.tHasWDauElectron[tidx]:
                nEle += 1
                nLep += 1
                self.tIsLeptonic[tidx] = True
            if self.tHasWDauMuon[tidx]:
                nMuon += 1
                nLep += 1
                self.tIsLeptonic[tidx] = True
            if self.tHasWDauTau[tidx]:
                if not self.tHasHadronicWDauTau[tidx]:
                    nLepTau += 1
                    nLep += 1
                    self.tIsLeptonic[tidx] = True
                else:
                    nHadTau += 1
                    self.tIsLeptonic[tidx] = False
            if self.tHasHadronicWDauTau[tidx] or self.tHasHadronicW[tidx]:
                nHad += 1
                self.tIsLeptonic[tidx] = False
        if returnCopy:
            return {'nEle': copy.copy(nEle), 'nMuon': copy.copy(nMuon), 'nLepTau': copy.copy(nLepTau),
                    'nHadTau': copy.copy(nHadTau), 'nHad': copy.copy(nHad), 'nLep': copy.copy(nLep),
                    'tIsLeptonic':copy.copy(self.tIsLeptonic)}
        else:
            return {'nEle': nEle, 'nMuon': nMuon, 'nLepTau': nLepTau,
                    'nHadTau': nHadTau, 'nHad': nHad, 'nLep': nLep, 'tIsLeptonic': self.tIsLeptonic}
        
    def evaluateHadronicity(self, returnCopy=True):
        tJets = {}
        tGenJets = {}
        tFatJets = {}
        tGenJetAK8s = {}
        bJets = {}
        bGenJets = {}
        bFatJets = {}
        bGenJetAK8s = {}
        WDau1Jets = {}
        WDau1GenJets = {}
        WDau1FatJets = {}
        WDau1GenJetAK8s = {}
        WDau2Jets = {}
        WDau2GenJets = {}
        WDau2FatJets = {}
        WDau2GenJetAK8s = {}
        for tidx in self.t_head.values():
            tJets[tidx] = set()
            tGenJets[tidx] = set()
            tFatJets[tidx] = set()
            tGenJetAK8s[tidx] = set()
            bJets[tidx] = set()
            bGenJets[tidx] = set()
            bFatJets[tidx] = set()
            bGenJetAK8s[tidx] = set()
            WDau1Jets[tidx] = set()
            WDau1GenJets[tidx] = set()
            WDau1FatJets[tidx] = set()
            WDau1GenJetAK8s[tidx] = set()
            WDau2Jets[tidx] = set()
            WDau2GenJets[tidx] = set()
            WDau2FatJets[tidx] = set()
            WDau2GenJetAK8s[tidx] = set()
            
            #print("b Desc: " + str(self.tb_desc[tidx]))
            for dnode in self.tb_desc[tidx]:
                if self.jets:
                    #print(self.treeJet[dnode])
                    for i in self.treeJet[dnode]:
                        bJets[tidx].add(i)
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        bGenJets[tidx].add(i)
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        bFatJets[tidx].add(i)
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        bGenJetAK8s[tidx].add(i)
            #print("W Dau 1 Desc: " + str(self.tW_dau1_desc[tidx]))
            for dnode in self.tW_dau1_desc[tidx]:
                if self.jets:
                    for i in self.treeJet[dnode]:
                        WDau1Jets[tidx].add(i)
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        WDau1GenJets[tidx].add(i)
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        WDau1FatJets[tidx].add(i)
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        WDau1GenJetAK8s[tidx].add(i)
            #print("W Dau 2 Desc: " + str(self.tW_dau2_desc[tidx]))
            for dnode in self.tW_dau2_desc[tidx]:
                if self.jets:
                    for i in self.treeJet[dnode]:
                        WDau2Jets[tidx].add(i)
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        WDau2GenJets[tidx].add(i)
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        WDau2FatJets[tidx].add(i)
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        WDau2GenJetAK8s[tidx].add(i)
            #print("t Desc: " + str(self.t_first_desc[tidx]))
            for dnode in self.t_first_desc[tidx]:
                if self.jets:
                    for i in self.treeJet[dnode]:
                        tJets[tidx].add(i)
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        tGenJets[tidx].add(i)
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        tFatJets[tidx].add(i)
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        tGenJetAK8s[tidx].add(i)
        #Analyze jet lists via unions, intersections, etc.
        
        #convert to list
        #for tidx in self.t_head.values():
            tJets[tidx] = list(tJets[tidx])
            tGenJets[tidx] = list(tGenJets[tidx])
            tFatJets[tidx] = list(tFatJets[tidx])
            tGenJetAK8s[tidx] = list(tGenJetAK8s[tidx])
            bJets[tidx] = list(bJets[tidx])
            bGenJets[tidx] = list(bGenJets[tidx])
            bFatJets[tidx] = list(bFatJets[tidx])
            bGenJetAK8s[tidx] = list(bGenJetAK8s[tidx])
            WDau1Jets[tidx] = list(WDau1Jets[tidx])
            WDau1GenJets[tidx] = list(WDau1GenJets[tidx])
            WDau1FatJets[tidx] = list(WDau1FatJets[tidx])
            WDau1GenJetAK8s[tidx] = list(WDau1GenJetAK8s[tidx])
            WDau2Jets[tidx] = list(WDau2Jets[tidx])
            WDau2GenJets[tidx] = list(WDau2GenJets[tidx])
            WDau2FatJets[tidx] = list(WDau2FatJets[tidx])
            WDau2GenJetAK8s[tidx] = list(WDau2GenJetAK8s[tidx])
            
        if returnCopy:
            return {'tJets': copy.copy(tJets), 'tGenJets': copy.copy(tGenJets), 'tFatJets': copy.copy(tFatJets),
                    'tGenJetAK8s': copy.copy(tGenJetAK8s), 'bJets': copy.copy(bJets), 'bGenJets': copy.copy(bGenJets),
                    'bFatJets': copy.copy(bFatJets), 'bGenJetAK8s': copy.copy(bGenJetAK8s), 'WDau1Jets': copy.copy(WDau1Jets),
                    'WDau1GenJets': copy.copy(WDau1GenJets), 'WDau1FatJets': copy.copy(WDau1FatJets),
                    'WDau1GenJetAK8s': copy.copy(WDau1GenJetAK8s), 'WDau2Jets': copy.copy(WDau2Jets),
                    'WDau2GenJets': copy.copy(WDau2GenJets), 'WDau2FatJets': copy.copy(WDau2FatJets),
                    'WDau2GenJetAK8s': copy.copy(WDau2GenJetAK8s)
                   }
        else:
            return {'tJets': tJets, 'tGenJets': tGenJets, 'tFatJets': tFatJets, 'tGenJetAK8s': tGenJetAK8s,
                    'bJets': bJets, 'bGenJets': bGenJets, 'bFatJets': bFatJets, 'bGenJetAK8s': bGenJetAK8s,
                    'WDau1Jets': WDau1Jets, 'WDau1GenJets': WDau1GenJets, 'WDau1FatJets': WDau1FatJets,
                    'WDau1GenJetAK8s': WDau1GenJetAK8s, 'WDau2Jets': WDau2Jets, 'WDau2GenJets': WDau2GenJets,
                    'WDau2FatJets': WDau2FatJets, 'WDau2GenJetAK8s': WDau2GenJetAK8s
                   }

    def evaluateHadronicityWithVoting(self, returnCopy=True, votingMethod=None, votingFilter=None):
        """Matches jets to b quarks and W daughters

        Take note of interplay with BuildPFTrees (notably the onlyUseClosest option storing one jet per gen), as gens can be DeltaR matched against multiple jets 
        due to overlap and the jet clustering algorithms. 
        votingMethod=None will cause the method to throw an exception with the usage information
        votingMethod=0:
        Unnweighted voting.
        Each gen can contribute 1 vote per jet and per jet type it was DeltaR matched to.
        votingMethod=1:
        Pt weighted voting.
        Each gen contributes a vote weighted by the fraction of parent particle Pt it carried, per jet and per jet type
        votingMethod=2:
        3-Momentum weighted voting.
        Each gen contributes a vote weighted by the fraction of parent particle Momentum it carried, per jet and per jet type
        """

        if votingMethod==None:
            help(MCTree.evaluateHadronicityWithVoting)
            raise ValueError("evaluateHadronicityWithVoting() in MCTree class requires a chosen voting method.")
        elif votingMethod==0:
            self.vote = lambda g, p : 1
        elif votingMethod==1:
            self.vote = lambda g, p : self.gens[g].p4().P() / self.gens[p].p4().P()
        elif votingMethod==2: #Not a good method, due to changes in angular direction for daughters versus parent particles
            self.vote = lambda g, p : self.gens[g].pt / self.gens[p].pt

            
        tJets = {}
        tGenJets = {}
        tFatJets = {}
        tGenJetAK8s = {}
        bJets = {}
        bGenJets = {}
        bFatJets = {}
        bGenJetAK8s = {}
        WDau1Jets = {}
        WDau1GenJets = {}
        WDau1FatJets = {}
        WDau1GenJetAK8s = {}
        WDau2Jets = {}
        WDau2GenJets = {}
        WDau2FatJets = {}
        WDau2GenJetAK8s = {}

        tJetsWeight = {}
        tGenJetsWeight = {}
        tFatJetsWeight = {}
        tGenJetAK8sWeight = {}
        bJetsWeight = {}
        bGenJetsWeight = {}
        bFatJetsWeight = {}
        bGenJetAK8sWeight = {}
        WDau1JetsWeight = {}
        WDau1GenJetsWeight = {}
        WDau1FatJetsWeight = {}
        WDau1GenJetAK8sWeight = {}
        WDau2JetsWeight = {}
        WDau2GenJetsWeight = {}
        WDau2FatJetsWeight = {}
        WDau2GenJetAK8sWeight = {}

        tJetsWithVoting = {}
        tGenJetsWithVoting = {}
        tFatJetsWithVoting = {}
        tGenJetAK8sWithVoting = {}
        bJetsWithVoting = {}
        bGenJetsWithVoting = {}
        bFatJetsWithVoting = {}
        bGenJetAK8sWithVoting = {}
        WDau1JetsWithVoting = {}
        WDau1GenJetsWithVoting = {}
        WDau1FatJetsWithVoting = {}
        WDau1GenJetAK8sWithVoting = {}
        WDau2JetsWithVoting = {}
        WDau2GenJetsWithVoting = {}
        WDau2FatJetsWithVoting = {}
        WDau2GenJetAK8sWithVoting = {}
        for tidx in self.t_head.values():
            tJets[tidx] = []
            tGenJets[tidx] = []
            tFatJets[tidx] = []
            tGenJetAK8s[tidx] = []
            bJets[tidx] = []
            bGenJets[tidx] = []
            bFatJets[tidx] = []
            bGenJetAK8s[tidx] = []
            WDau1Jets[tidx] = []
            WDau1GenJets[tidx] = []
            WDau1FatJets[tidx] = []
            WDau1GenJetAK8s[tidx] = []
            WDau2Jets[tidx] = []
            WDau2GenJets[tidx] = []
            WDau2FatJets[tidx] = []
            WDau2GenJetAK8s[tidx] = []

            tJetsWeight[tidx] = []
            tGenJetsWeight[tidx] = []
            tFatJetsWeight[tidx] = []
            tGenJetAK8sWeight[tidx] = []
            bJetsWeight[tidx] = []
            bGenJetsWeight[tidx] = []
            bFatJetsWeight[tidx] = []
            bGenJetAK8sWeight[tidx] = []
            WDau1JetsWeight[tidx] = []
            WDau1GenJetsWeight[tidx] = []
            WDau1FatJetsWeight[tidx] = []
            WDau1GenJetAK8sWeight[tidx] = []
            WDau2JetsWeight[tidx] = []
            WDau2GenJetsWeight[tidx] = []
            WDau2FatJetsWeight[tidx] = []
            WDau2GenJetAK8sWeight[tidx] = []

            tJetsWithVoting[tidx] = {}
            tGenJetsWithVoting[tidx] = {}
            tFatJetsWithVoting[tidx] = {}
            tGenJetAK8sWithVoting[tidx] = {}
            bJetsWithVoting[tidx] = {}
            bGenJetsWithVoting[tidx] = {}
            bFatJetsWithVoting[tidx] = {}
            bGenJetAK8sWithVoting[tidx] = {}
            WDau1JetsWithVoting[tidx] = {}
            WDau1GenJetsWithVoting[tidx] = {}
            WDau1FatJetsWithVoting[tidx] = {}
            WDau1GenJetAK8sWithVoting[tidx] = {}
            WDau2JetsWithVoting[tidx] = {}
            WDau2GenJetsWithVoting[tidx] = {}
            WDau2FatJetsWithVoting[tidx] = {}
            WDau2GenJetAK8sWithVoting[tidx] = {}

            #Fill dictionaries with jet indices and value initialized to 0 (will be accumulated votes for the jet)
            #Append jet list of tuples with the jet index and the weight of the vote
            #print("b Desc: " + str(self.tb_desc[tidx]))
            for dnode in self.tb_desc[tidx]:
                thevote = self.vote(dnode, self.tb_first[tidx])
                if self.jets:
                    #print(self.treeJet[dnode])
                    for i in self.treeJet[dnode]:
                        bJetsWithVoting[tidx][i] = 0
                        bJetsWeight[tidx].append((i, thevote))
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        bGenJetsWithVoting[tidx][i] = 0
                        bGenJetsWeight[tidx].append((i, thevote))
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        bFatJetsWithVoting[tidx][i] = 0
                        bFatJetsWeight[tidx].append((i, thevote))
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        bGenJetAK8sWithVoting[tidx][i] = 0
                        bGenJetAK8sWeight[tidx].append((i, thevote))
            #print("W Dau 1 Desc: " + str(self.tW_dau1_desc[tidx]))
            for dnode in self.tW_dau1_desc[tidx]:
                thevote = self.vote(dnode, self.tW_dau1_last[tidx])
                if self.jets:
                    for i in self.treeJet[dnode]:
                        WDau1JetsWithVoting[tidx][i] = 0
                        WDau1JetsWeight[tidx].append((i, thevote))
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        WDau1GenJetsWithVoting[tidx][i] = 0
                        WDau1GenJetsWeight[tidx].append((i, thevote))
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        WDau1FatJetsWithVoting[tidx][i] = 0
                        WDau1FatJetsWeight[tidx].append((i, thevote))
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        WDau1GenJetAK8sWithVoting[tidx][i] = 0
                        WDau1GenJetAK8sWeight[tidx].append((i, thevote))
            #print("W Dau 2 Desc: " + str(self.tW_dau2_desc[tidx]))
            for dnode in self.tW_dau2_desc[tidx]:
                thevote = self.vote(dnode, self.tW_dau2_last[tidx])
                if self.jets:
                    for i in self.treeJet[dnode]:
                        WDau2JetsWithVoting[tidx][i] = 0
                        WDau2JetsWeight[tidx].append((i, thevote))
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        WDau2GenJetsWithVoting[tidx][i] = 0
                        WDau2GenJetsWeight[tidx].append((i, thevote))
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        WDau2FatJetsWithVoting[tidx][i] = 0
                        WDau2FatJetsWeight[tidx].append((i, thevote))
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        WDau2GenJetAK8sWithVoting[tidx][i] = 0
                        WDau2GenJetAK8sWeight[tidx].append((i, thevote))
            #print("t Desc: " + str(self.t_first_desc[tidx]))
            
            #t_remainder = set(self.t_first_desc[tidx]) - (set(self.tb_first_desc[tidx]) + set(self.tW_dau1_desc[tidx]) + set(self.tW_dau2_desc[tidx]))
            #for dnode in t_remainder:
            for dnode in self.t_first_desc[tidx]:
                thevote = self.vote(dnode, self.t_first[tidx])
                if self.jets:
                    for i in self.treeJet[dnode]:
                        tJetsWithVoting[tidx][i] = 0
                        tJetsWeight[tidx].append((i, thevote))
                if self.genjets:
                    for i in self.treeGenJet[dnode]:
                        tGenJetsWithVoting[tidx][i] = 0
                        tGenJetsWeight[tidx].append((i, thevote))
                if self.fatjets:
                    for i in self.treeFatJet[dnode]:
                        tFatJetsWithVoting[tidx][i] = 0
                        tFatJetsWeight[tidx].append((i, thevote))
                if self.genfatjets:
                    for i in self.treeGenJetAK8[dnode]:
                        tGenJetAK8sWithVoting[tidx][i] = 0
                        tGenJetAK8sWeight[tidx].append((i, thevote))

            #Accumulate votes by using the key in the 1st slot of the tuple, and the vote weight in the second slot
            for v in tJetsWeight[tidx]:
                tJetsWithVoting[tidx][v[0]] += v[1]
            for v in tGenJetsWeight[tidx]:
                tGenJetsWithVoting[tidx][v[0]] += v[1]
            for v in tFatJetsWeight[tidx]:
                tFatJetsWithVoting[tidx][v[0]] += v[1]
            for v in tGenJetAK8sWeight[tidx]:
                tGenJetAK8sWithVoting[tidx][v[0]] += v[1]
            for v in bJetsWeight[tidx]:
                bJetsWithVoting[tidx][v[0]] += v[1]
            for v in bGenJetsWeight[tidx]:
                bGenJetsWithVoting[tidx][v[0]] += v[1]
            for v in bFatJetsWeight[tidx]:
                bFatJetsWithVoting[tidx][v[0]] += v[1]
            for v in bGenJetAK8sWeight[tidx]:
                bGenJetAK8sWithVoting[tidx][v[0]] += v[1]
            for v in WDau1JetsWeight[tidx]:
                WDau1JetsWithVoting[tidx][v[0]] += v[1]
            for v in WDau1GenJetsWeight[tidx]:
                WDau1GenJetsWithVoting[tidx][v[0]] += v[1]
            for v in WDau1FatJetsWeight[tidx]:
                WDau1FatJetsWithVoting[tidx][v[0]] += v[1]
            for v in WDau1GenJetAK8sWeight[tidx]:
                WDau1GenJetAK8sWithVoting[tidx][v[0]] += v[1]
            for v in WDau2JetsWeight[tidx]:
                WDau2JetsWithVoting[tidx][v[0]] += v[1]
            for v in WDau2GenJetsWeight[tidx]:
                WDau2GenJetsWithVoting[tidx][v[0]] += v[1]
            for v in WDau2FatJetsWeight[tidx]:
                WDau2FatJetsWithVoting[tidx][v[0]] += v[1]
            for v in WDau2GenJetAK8sWeight[tidx]:
                WDau2GenJetAK8sWithVoting[tidx][v[0]] += v[1]

            #Convert to lists of tuples and sort
            tJets[tidx] = tJetsWithVoting[tidx].items()
            tJets[tidx].sort(key=lambda k : k[1], reverse=True)
            tGenJets[tidx] = tGenJetsWithVoting[tidx].items()
            tGenJets[tidx].sort(key=lambda k : k[1], reverse=True)
            tFatJets[tidx] = tFatJetsWithVoting[tidx].items()
            tFatJets[tidx].sort(key=lambda k : k[1], reverse=True)
            tGenJetAK8s[tidx] = tGenJetAK8sWithVoting[tidx].items()
            tGenJetAK8s[tidx].sort(key=lambda k : k[1], reverse=True)
            bJets[tidx] = bJetsWithVoting[tidx].items()
            bJets[tidx].sort(key=lambda k : k[1], reverse=True)
            bGenJets[tidx] = bGenJetsWithVoting[tidx].items()
            bGenJets[tidx].sort(key=lambda k : k[1], reverse=True)
            bFatJets[tidx] = bFatJetsWithVoting[tidx].items()
            bFatJets[tidx].sort(key=lambda k : k[1], reverse=True)
            bGenJetAK8s[tidx] = bGenJetAK8sWithVoting[tidx].items()
            bGenJetAK8s[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau1Jets[tidx] = WDau1JetsWithVoting[tidx].items()
            WDau1Jets[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau1GenJets[tidx] = WDau1GenJetsWithVoting[tidx].items()
            WDau1GenJets[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau1FatJets[tidx] = WDau1FatJetsWithVoting[tidx].items()
            WDau1FatJets[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau1GenJetAK8s[tidx] = WDau1GenJetAK8sWithVoting[tidx].items()
            WDau1GenJetAK8s[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau2Jets[tidx] = WDau2JetsWithVoting[tidx].items()
            WDau2Jets[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau2GenJets[tidx] = WDau2GenJetsWithVoting[tidx].items()
            WDau2GenJets[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau2FatJets[tidx] = WDau2FatJetsWithVoting[tidx].items()
            WDau2FatJets[tidx].sort(key=lambda k : k[1], reverse=True)
            WDau2GenJetAK8s[tidx] = WDau2GenJetAK8sWithVoting[tidx].items()
            WDau2GenJetAK8s[tidx].sort(key=lambda k : k[1], reverse=True)
            
        if returnCopy:
            return {'tJets': copy.copy(tJets), 'tGenJets': copy.copy(tGenJets), 'tFatJets': copy.copy(tFatJets),
                    'tGenJetAK8s': copy.copy(tGenJetAK8s), 'bJets': copy.copy(bJets), 'bGenJets': copy.copy(bGenJets),
                    'bFatJets': copy.copy(bFatJets), 'bGenJetAK8s': copy.copy(bGenJetAK8s), 'WDau1Jets': copy.copy(WDau1Jets),
                    'WDau1GenJets': copy.copy(WDau1GenJets), 'WDau1FatJets': copy.copy(WDau1FatJets),
                    'WDau1GenJetAK8s': copy.copy(WDau1GenJetAK8s), 'WDau2Jets': copy.copy(WDau2Jets),
                    'WDau2GenJets': copy.copy(WDau2GenJets), 'WDau2FatJets': copy.copy(WDau2FatJets),
                    'WDau2GenJetAK8s': copy.copy(WDau2GenJetAK8s)
                   }
        else:
            return {'tJets': tJets, 'tGenJets': tGenJets, 'tFatJets': tFatJets, 'tGenJetAK8s': tGenJetAK8s,
                    'bJets': bJets, 'bGenJets': bGenJets, 'bFatJets': bFatJets, 'bGenJetAK8s': bGenJetAK8s,
                    'WDau1Jets': WDau1Jets, 'WDau1GenJets': WDau1GenJets, 'WDau1FatJets': WDau1FatJets,
                    'WDau1GenJetAK8s': WDau1GenJetAK8s, 'WDau2Jets': WDau2Jets, 'WDau2GenJets': WDau2GenJets,
                    'WDau2FatJets': WDau2FatJets, 'WDau2GenJetAK8s': WDau2GenJetAK8s
                   }
        
    def debugTopSubtree(self):
        print("MCTree is printing some linked nodes for debugging purposes")
        print("t_head: " + str(self.t_head))
        print("t_first: " + str(self.t_first))
        print("t_last: " + str(self.t_last))
        print("tb_first: " + str(self.tb_first))
        print("tb_last: " + str(self.tb_last))
        print("tW_first: " + str(self.tW_first))
        print("tW_last: " + str(self.tW_last))
        print("tW_dau1_first: " + str(self.tW_dau1_first))
        print("tW_dau1_last: " + str(self.tW_dau1_last))
        print("tW_dau2_first: " + str(self.tW_dau2_first))
        print("tW_dau2_last: " + str(self.tW_dau2_last))

    def printGenTree(self):
        if self.verbose:
            print("MCTree is printing the current tree dictionary")
        print(self.tree)
        
    def printGenNode(self, nodeKey=-1, depth=0, lNode=False):
        tmp = ""
        if nodeKey > -1:
            gen = self.gens[nodeKey]
            tmp += " ||   "*(depth-1) 
            if lNode: tmp += "  \\\== "
            else: tmp += " ||=== "
            tmp += "{0:d}  ({1:d}:{2:6.2f},{3:4.2f},{4:4.2f})".format(gen.pdgId, nodeKey, 
                                                                           gen.pt, gen.eta, gen.phi)
        #elif nodeKey == 0:
        #    gen = self.gens[nodeKey]
        #    tmp += "{0:d}  ({1:d}:{2:6.2f},{3:4.2f},{4:4.2f})".format(gen.pdgId, nodeKey, 
        #                                                                   gen.pt, gen.eta, gen.phi)
        else:
            tmp += "Initial Proton-Proton Interaction"
        print(tmp)
        ndmax = len(self.tree[nodeKey])
        for nd, dau in enumerate(self.tree[nodeKey]):
            if type(dau) is int:
                if -1 <= dau <= len(self.gens):
                    #pass
                    #if(depth < 3): 
                    if nd < ndmax - 1:
                        self.printGenNode(nodeKey=dau, depth=depth+1, lNode=False)
                    else:
                        self.printGenNode(nodeKey=dau, depth=depth+1, lNode=True)
                else:
                    raise ValueError("printGenNode() received a nodeKey outside of the Gen Particle Collection range")
            else:
                pass
            
    def pprintGenNode(self, nodeKey=-1, depthMask=[], lNode=False):
        tmp = ""
        if nodeKey > -1:
            gen = self.gens[nodeKey]
            for m, mask in enumerate(depthMask):
                if mask:
                    tmp += "      "
                elif m > 0:
                    tmp += " ||   "
            if lNode: tmp += "  \\\== "
            else: tmp += " ||=== "
            tmp += "{0:d}  ({1:d}:{2:6.2f},{3:4.2f},{4:4.2f},{5:6.2f})".format(gen.pdgId, nodeKey, 
                                                                           gen.pt, gen.eta, gen.phi, gen.p4().E())
        else:
            tmp += "Initial Proton-Proton Interaction"
        print(tmp)
        ndmax = len(self.tree[nodeKey])
        for nd, dau in enumerate(self.tree[nodeKey]):
            if type(dau) is int:
                if -1 <= dau <= len(self.gens):
                    #pass
                    #if(depth < 3): 
                    subDepthMask = copy.copy(depthMask)
                    subDepthMask.append(lNode)
                    if nd < ndmax - 1:
                        self.pprintGenNode(nodeKey=dau, depthMask=subDepthMask, lNode=False)
                    else:
                        self.pprintGenNode(nodeKey=dau, depthMask=subDepthMask, lNode=True)
                else:
                    raise ValueError("printGenNode() received a nodeKey outside of the Gen Particle Collection range")
            else:
                pass
       
    def getInternalState(self, state_key=None, returnCopy=True):
        #FIXME: Update list
        all_state_keys = ["t_head",
                          "t_first",
                          "t_last",
                          "t_rad",
                          "tb_first",
                          "tb_last",
                          "tb_desc",
                          "tb_hadleps",
                          "tW_first",
                          "tW_last",
                          "tW_dau1_first",
                          "tW_dau1_last",
                          "tW_dau1_desc",
                          "tW_dau2_first",
                          "tW_dau2_last",
                          "tW_dau2_desc",
                          "tWTau_dauArr_first",
                          "tWTau_dauArr_last",
                          "tWTau_dauArr_desc",
                          "tWTau_mLep_first",
                          "tWTau_mLep_last",
                          "tWTau_mLep_desc",
                          "tW_hadleps",
                          "tHasWDauElectron",
                          "tHasWDauMuon",
                          "tHasWDauTau",
                          "tHasAnyHadronicTau",
                          "tHasHadronicWDauTau",
                          "tHasHadronicW",
                          "W_head",
                          "Z_head",
                          "H_head",
                          "tree", 
                          "treeElectron",
                          "treeMuon",
                          "treeTau",
                          "treeJet",
                          "treeGenJet",
                          "treeFatJet",
                          "treeGenJetAK8",
                         ]
        if not state_key or type(state_key) is list:
            if type(state_key) is list:
                list_state_keys = state_key
            else:
                list_state_keys = all_state_keys
            if returnCopy:
                return {skey:copy.copy(getattr(self, skey)) for skey in list_state_keys}
            else:
                return {skey:getattr(self, skey) for skey in list_state_keys}
        elif hasattr(self, state_key):
            if returnCopy:
                return copy.copy(getattr(self, state_key))
            else:
                return getattr(self, state_key)
        else:
            raise ValueError("Unrecognized state key {0:s} passed to MCSlimTop.getInternalState(state_key)"\
                             .format(str(state_key)))
