from PhysicsTools.NanoAODTools.postprocessing.tools import *
import copy
from glob import glob #For getFiles
import os #For getFiles
import tempfile #For getFiles


def dumpGenCollection(genPartCollection):
    print("=====Gen Particles=====\n{0:>5s} {1:>10s} {2:>10s} {3:>10s} {4:>10s} {5:10s} {6:>10s} {7:>20s}"
              .format("IdX", "pt", "eta", "phi","Moth ID", "PDG ID", "Status", "Stat. Flgs"))
    for np, gen in enumerate(genPartCollection):
        print("Idx: {0:<5d}".format(np) + " " + strGenPart(gen))
        
def dumpMuonCollection(muons):
    print("=====Muons=====\n")
    for nm, muon in enumerate(muons):
        print("Idx: {0:<5d}".format(nm) + " " + strElectron(muon).replace("Electron ", ""))
        
def dumpElectronCollection(electrons):
    print("=====Electrons=====\n")
    for ne, electron in enumerate(electrons):
        print("Idx: {0:<5d}".format(ne) + " " + strElectron(electron).replace("Electron ", ""))
        
def dumpJetCollection(jets):
    print("=====Jets=====\n")
    for nj, jet in enumerate(jets):
        print("Idx: {0:<5d}".format(nj) + " " + strJet(jet).replace("Jet ", "", 1))

def dumpGenJetCollection(jets):
    print("=====Gen Jets=====\n")
    for nj, jet in enumerate(jets):
        print("Idx: {0:<5d}".format(nj) + " " + strGenJet(jet).replace("Gen Jet ", "", 1))

def strMuon(muon):
    if not muon:
        return ""
    tmp="Muon Pt: {0:>7.1f} Eta: {1:>6.2f} Phi: {2:>6.2f} C: {3:>2d} JetIdx: {4:>3d}"\
        " GenPartIdx: {5:>4d} PFIso: {6:>4.2f}".format(muon.pt, muon.eta, muon.phi, muon.charge, muon.jetIdx, 
                                                       muon.genPartIdx, muon.pfRelIso04_all)
    if hasattr(muon, "PES"):
        tmp += " PES: {0:<10d}".format(muon.PES)
    return tmp

def strElectron(electron):
    if not electron:
        return ""
    tmp="Electron Pt: {0:>7.1f} Eta: {1:>6.2f} Phi: {2:>6.2f} C: {3:>2d} JetIdx: {4:>3d}"\
        " GenPartIdx: {5:>4d} PFIso: {6:>4.2f}".format(electron.pt, electron.eta, electron.phi, electron.charge,
                                      electron.jetIdx, electron.genPartIdx, electron.pfRelIso03_all)
    if hasattr(electron, "PES"):
        tmp += " PES: {0:<10d}".format(electron.PES)
    return tmp

def strJet(jet):
    if not jet:
        return ""
    tmp="Jet Pt: {0:<7.1f} Eta: {1:<6.2f} Phi: {2:<6.2f} M: {3:<6.2f} DeepJetB: {4:<10.4f}"\
        " GenJetIdx: {5:<10d}".format(jet.pt, jet.eta, jet.phi, jet.mass, jet.btagDeepFlavB, jet.genJetIdx)
    if hasattr(jet, "PES"):
        tmp += " PES: {0:<10d}".format(jet.PES)
    return tmp

def strGenJet(genjet):
    if not genjet:
        return ""
    tmp="GenJet Pt: {0:<7.1f} Eta: {1:<6.2f} Phi: {2:<6.2f} M: {3:<6.2f} Hadr Flav: {4:<10d}"\
        " Part Flav: {5:<10d}".format(genjet.pt, genjet.eta, genjet.phi, genjet.mass, genjet.hadronFlavour,
                                      genjet.partonFlavour)
    return tmp

def strFatJet(jet):
    if not jet:
        return ""
    tmp="Fatjet Pt: {0:<7.1f} Eta: {1:<6.2f} Phi: {2:<6.2f} M: {3:<6.2f} JetID: {4:<5d} TvsQCD: {5:<10.4f}"\
          " WvsQCD: {6:<10.4f}".format(jet.pt, jet.eta, jet.phi, jet.mass, jet.jetId, jet.deepTag_TvsQCD, jet.deepTag_WvsQCD)
    return tmp

def strGenJetAK8(genjet):
    if not genjet:
        return ""
    tmp="GenJet Pt: {0:<7.1f} Eta: {1:<6.2f} Phi: {2:<6.2f} M: {3:<6.2f} Had Flav: {4:<10d}"\
          " Part Flav: {5:<10d}".format(genjet.pt, genjet.eta, genjet.phi, genjet.mass, genjet.hadronFlavour, genjet.partonFlavour)
    return tmp

def strGenPart(gen):
    if not gen:
        return ""
    tmp="Gen Pt: {0:<7.1f} Eta: {1:<6.2f} Phi: {2:<6.2f} M: {3:<6.2f}"\
        " Moth: {4:<3d} PDG ID: {5:<5d} Stat: {6:<4d} Flgs: "\
        "{7:015b}".format(gen.pt, gen.eta, gen.phi, gen.mass, gen.genPartIdxMother, 
                          gen.pdgId, gen.status, gen.statusFlags)
    return tmp

def strGenerator(generator):
    if not generator:
        return ""
    tmp="\n==========Generator=========="\
          "\nBinVar: {0:<10f} ID 1: {1:<5d} ID 2: {2:<5d} Q2 Scale: {3:<10.4f} Weight: {4:<10.4f} \n\tX1: {5:<7.3f} X2: {6:<7.3f} X*PDF1:"\
          " {7:<10.9f} X*PDF2: {8:<10.9f}".format(generator.binvar, generator.id1, generator.id2, generator.scalePDF, 
                                                  generator.weight, generator.x1,generator.x2, generator.xpdf1, generator.xpdf2)
    return tmp

def strBtagWeight(btagweight):
    tmp="\n==========btag Weight==========\n"\
        "CSVv2: " + str(btagweight.CSVV2) + " DeepCSV: " + str(btagweight.DeepCSVB)
    return tmp

#def strLink(linkChain, sub=False):
#    if not sub:
#        tmp="\n==========A Link Chain==========\n"
#    else:
#        tmp=""
#    if type(linkChain) is list and linkChain:
#        if type(linkChain[0]) is list:
#            for subchain in linkChain:
#                tmp += strLink(subchain, sub=True)
#        else:
#            for l in linkChain:
#                if l[0] == "GenPart":
#                    tmp += ("{0:<10s} Idx: {1:<4d} Moth: {2:<10d}          pdgId: {3:<5d} dR: {4:<5.4f} Flg: {5:015b} Pt: {6:<10.4f}"\
#                            "\n".format(l[0], l[1], l[2], l[3], l[4], l[5], getattr(l[6], "pt")))
#                elif l[0] == "Jet":
#                    tmp += ("{0:<10s} Idx: {1:<4d} GenJet: {2:<10d} hadron Flavour: {3:<5d} dR: {4:<5.4f} Oth: {5:<10d}"\
#                            "Pt: {6:<10.4f}\n".format(l[0], l[1], l[2], l[3], l[4], l[5], getattr(l[6], "pt")))
#                elif l[0] == "Electron":
#                    tmp += "FIXME: ELECTRON\n"
#                elif l[0] == "Muon":
#                    tmp += "FIXME: MUON\n"
#                elif l[0] == "GenJet":
#                    tmp += ("{0:<10s} Idx: {1:<4d} GenParts: {2:<10s} hadron Flavour: {3:<5d} dR: {4:<5.4f} Oth: {5:<10d}"\
#                            "Pt: {6:<10.4f}\n".format(l[0], l[1], l[2], l[3], l[4], l[5], getattr(l[6], "pt")))
#                elif l[0] == "FatJet":
#                    tmp += "FIXME: FATJET\n"
#                elif l[0] == "GenJetAK8":
#                    tmp += "FIXME: GenJetAK8\n"
#                else:
#                    tmp += "UNKNOWN TYPE: {0:<20s}\n".format(l[0])
#        return tmp
#    elif type(linkChain) is list:
#        #if the list is empty
#        return "linkChain is Empty!"
#    else:
#        raise TypeError("Function strLink() was passed a non-list (and non-list-of-lists) type: " + str(type(linkChain)))
        
def strSupLink(linkChain, sub=False):
    if not sub:
        tmp="\n==========A Link Chain==========\n"
    else:
        tmp=""
    if type(linkChain) is list:
        if linkChain:
            if type(linkChain[0]) is list:
                if linkChain[0]:
                    for subchain in linkChain:
                        tmp += "\n" + strSupLink(subchain, sub=True)
                else:
                    tmp += "\n\tEmpty subchain!\n"
            else:
                for l in linkChain:
                    if l[0] == "GenPart":
                        tmp += ("{0:>10s} Idx: {1:>3d} Moth: {2:>4d}        pdgId: {3:>5d} dR: {4:>7.4f} Flg: {5:015b} Pt: {6:<10.4f}"\
                                "\n".format(l[0], l[1], l[2], l[3], (l[4] if l[4] < 100.0 else float('inf')), l[5], getattr(l[6], "pt")))
                    elif l[0] == "Jet":
                        tmp += ("{0:>10s} Idx: {1:>3d} GenJet: {2:>4d}   had Flav: {3:>5d} dR: {4:>7.4f} Oth: {5:>10d}"\
                                "Pt: {6:<10.4f}\n".format(l[0], l[1], l[2], l[3], l[4], getattr(l[6], "jetId"), getattr(l[6], "pt")))
                    elif l[0] == "Electron":
                        tmp += ("{0:>10s} Idx: {1:>3d} GenParts: {2:>4d}    pdgId: {3:>5d} dR: {4:>7.4f} Part Flav: {5:>4d}"\
                                "Pt: {6:<10.4f}\n".format(l[0], l[1], l[2], l[3], l[4], l[5], getattr(l[6], "pt")))
                    elif l[0] == "Muon":
                        tmp += ("{0:>10s} Idx: {1:>3d} GenParts: {2:>4d}    pdgId: {3:>5d} dR: {4:>7.4f} Part Flav: {5:>4d}"\
                                " Pt: {6:<10.4f}\n".format(l[0], l[1], l[2], l[3], l[4], l[5], getattr(l[6], "pt")))
                    elif l[0] == "GenJet":
                        tmp += ("{0:<10s} Idx: {1:>3d} GenParts: {2:>4d} had Flav: {3:>5d} dR: {4:>7.4f} Oth: {5:>10d}"\
                                " Pt: {6:<10.4f}\n".format(l[0], l[1], l[2], l[3], l[4], l[5], getattr(l[6], "pt")))
                    elif l[0] == "FatJet":
                        tmp += "FIXME: FATJET\n"
                    elif l[0] == "GenJetAK8":
                        tmp += "FIXME: GenJetAK8\n"
                    else:
                        tmp += "UNKNOWN TYPE: {0:<20s}\n".format(l[0])
            return tmp
    elif type(linkChain) is list:
        #if the list is empty
        return "linkChain is Empty!"
    else:
        raise TypeError("Function strSupLink() was passed a non-list (and non-list-of-lists) type: " + str(type(linkChain)))
        
def linkFatJet(inJet=None, genPartCollection=None, genJetCollection=None, isGenJet=False, linkChain=None):
    """process input FatJet, find lineage within gen particles

    if isGenJet=True, skip linking step from FatJet to GenJetAK8"""
    if not (genPartCollection and genJetCollection):
        raise RuntimeException("Neither Gen Particle nor Gen Jet collections passed to linFatJet()")
    inter = []
    inter.append(inJet)
    intermediateResult = matchObjectCollectionMultiple(inter, genJetCollection, dRmax=0.8)
    #intermediateResult = matchObjectCollection(inter, genJetCollection, dRmax=0.4)
    theKeys = intermediateResult.keys()
    for i, k in enumerate(theKeys):
        matches = intermediateResult[k]
        print(" FatJet Idx: {0:<2d}".format(i) + " " + strFatJet(inJet))
        for m, match in enumerate(matches):
            print(" GenJetAK8 Match: {0:<2d}".format(m) + " " + strGenJetAK8(match))
            print(" deltaR: " + str(deltaR(k, match)))
        #print("")
        #print(intermediateResult[str(k)])
    #print("inJet length and type: " +str(len(inJet)) + " " + str(type(inJet)))
    #if hasattr(inJet, "genJetIdx"):
    #    print(getattr(inJet, "genJetIdx"))
    #    outJet = genJetCollection[inJet.genJetIdx]
    #else:
    #    print("FUCKOFF")
    #    print(inJet.pt)
    #    return [(-10,-10,-10)]
    #Can add DeltaR fallback...
    #linJetPresel=lambda x, y: x.partonFlavour == y.pdgId
    #matchResult = matchObjectCollectionMultiple(outJet,genPartCollection,dRmax=0.4,presel=linJetPresel)
    #matchResult = matchObjectCollection(outJet,genPartCollection,dRmax=0.4)
    #print(type(matchResult))
    
def linkMuon(inLep, inLepIdx, lepCollection, genPartCollection):
    """process input Muon, find lineage within gen particles

    pass "find" as inLepIdx of particle to trigger finding within the method"""
    linkChain = []
    lepIdx = -1
    if inLepIdx == "find":
        for Idx, lep in enumerate(lepCollection):
            if inLep == lep:
                lepIdx = Idx
                break
    elif -1 < inLepIdx < len(lepCollection):
        lepIdx = inLepIdx
    else:
        lepIdx = -999
    tmpMoth = inLep.genPartIdx
    #temporary deltaR with a default (only stored under logic error) and a calculation against the 'head' of the chain
    tmpDeltaR = -9999.786
    if len(linkChain) > 0:
        tmpDeltaR = deltaR(inPart, linkChain[0][6])
    elif len(linkChain) == 0:
        tmpDeltaR = 0.0
    linkChain.append( ("Muon", lepIdx, tmpMoth, inLep.pdgId, tmpDeltaR, inLep.genPartFlav, inLep) )
    if -1 < tmpMoth < len(genPartCollection):
        __ = linkGenPart(genPartCollection[tmpMoth], tmpMoth, genPartCollection, linkChain=linkChain)
    return linkChain

def linkElectron(inLep, inLepIdx, lepCollection, genPartCollection):
    """process input Electron, find lineage within gen particles

    pass "find" as inLepIdx of particle to trigger finding within the method"""
    linkChain = []
    lepIdx = -1
    if inLepIdx == "find":
        for Idx, lep in enumerate(lepCollection):
            if inLep == lep:
                lepIdx = Idx
                break
    elif -1 < inLepIdx < len(lepCollection):
        lepIdx = inLepIdx
    else:
        lepIdx = -999
    tmpMoth = inLep.genPartIdx
    #temporary deltaR with a default (only stored under logic error) and a calculation against the 'head' of the chain
    tmpDeltaR = -9999.786
    if len(linkChain) > 0:
        tmpDeltaR = deltaR(inPart, linkChain[0][6])
    elif len(linkChain) == 0:
        tmpDeltaR = 0.0
    linkChain.append( ("Electron", lepIdx, tmpMoth, inLep.pdgId, tmpDeltaR, inLep.genPartFlav, inLep) )
    if -1 < tmpMoth < len(genPartCollection):
        __ = linkGenPart(genPartCollection[tmpMoth], tmpMoth, genPartCollection, linkChain=linkChain)
    return linkChain

def linkGenPart(inPart, inPartIdx, genPartCollection, linkChain=None):
    #If not passed a list of tuples, create an empty one to be returned
    if linkChain==None:
        linkChain = []
    #Set partIdx if an appropriate one is passed in ("find" triggers a search within this method)
    partIdx = -1
    if inPartIdx == "find":
        for Idx, gen in enumerate(genPartCollection):
            if inPart == gen:
                partIdx = Idx
                break
    elif -1 < inPartIdx < len(genPartCollection):
        partIdx = inPartIdx
    else:
        partIdx = -999
    #temporary mother Idx storage
    tmpMoth = inPart.genPartIdxMother
    #temporary deltaR with a default (only stored under logic error) and a calculation against the 'head' of the chain
    tmpDeltaR = -9999.786
    if len(linkChain) > 0:
        tmpDeltaR = deltaR(inPart, linkChain[0][6])
    elif len(linkChain) == 0:
        tmpDeltaR = 0.0
    linkChain.append( ("GenPart", partIdx, tmpMoth, inPart.pdgId, tmpDeltaR, inPart.statusFlags, inPart) )
    #Call next iteration on the mother particle, passing it the linkChain and mother's positional index
    if -1 < tmpMoth < len(genPartCollection):
        __ = linkGenPart(genPartCollection[tmpMoth], tmpMoth, genPartCollection, linkChain=linkChain)
    return linkChain

def linkJet(inJet, inJetIdx, jetCollection, genJetCollection, genPartCollection, linkChain=None):
    """process input Jet, find lineage within gen particles

    link jets to genJets"""
    if not (genJetCollection and jetCollection):
        raise RuntimeException("linkJet requires the jet and genJet collections")
    if linkChain==None:
        linkChain = []
    #Set jetIdx if an appropriate one is passed in ("find" triggers a search within this method)
    jetIdx = -1
    typeName = "Jet"
    if inJetIdx == "find":
        for Idx, jet in enumerate(jetCollection):
            if inJet == jet:
                jetIdx = Idx
                break
    elif -1 < inJetIdx < len(jetCollection):
        jetIdx = inJetIdx
    else:
        jetIdx = -999
    #tmpMoth
    tmpMoth = inJet.genJetIdx
    #temporary deltaR with a default (only stored under logic error) and a calculation against the 'head' of the chain
    tmpDeltaR = -9999.786
    if len(linkChain) > 0:
        tmpDeltaR = deltaR(inJet, linkChain[0][6])
    elif len(linkChain) == 0:
        tmpDeltaR = 0.0
    linkChain.append( (typeName, jetIdx, tmpMoth, inJet.hadronFlavour, tmpDeltaR, -987654321, inJet) )
######    print("\nJetID: " + str(inJet.jetId) + " Part Flav: " + str(inJet.partonFlavour)
######         + " QGL: " + str(inJet.qgl))
    if -1 < tmpMoth < len(genJetCollection):
        genJetReturn = linkGenJet(genJetCollection[tmpMoth], tmpMoth, jetCollection, genJetCollection, genPartCollection, linkChain=linkChain)
        return genJetReturn
    else:
        return linkChain


    #store genJets matching the jet in a list
    #intermediateResult = matchObjectCollectionMultiple([inJet], genJetCollection, dRmax=0.4)
    #if len(intermediateResult) != 1:
    #    raise ImplementationError("linkJet() has encountered a jet matching {0:3d} genJets. The method does"\
    #                              " not handle this case properly yet".format(len(intermediateResult)))
    #self.matchAK4counters[len(intermediateResult[inJet])] += 1
    #matches = {}
    #for i, k in enumerate(intermediateResult.keys()):
        #matches = intermediateResult[k]
    #matches[k] = intermediateResult[k for k in intermediateResult.keys()]
    #print(matches[k] for k in intermediateResult.keys())
        #print(" Jet Idx: {0:<2d}".format(i) + " " + strJet(inJet))
        #for m, match in enumerate(matches):
            #pass
            #print(" GenJet Match: {0:<2d}".format(m) + " " + strGenJet(match))
            #print(" deltaR: " + str(deltaR(k, match)))
    #print("inJet length and type: " +str(len(inJet)) + " " + str(type(inJet)))
    #if hasattr(inJet, "genJetIdx"):
    #    print(getattr(inJet, "genJetIdx"))
    #    outJet = genJetCollection[inJet.genJetIdx]
    #else:
    #    print("FUCKOFF")
    #    print(inJet.pt)
    #    return [(-10,-10,-10)]
    #Can add DeltaR fallback...
    #linJetPresel=lambda x, y: x.partonFlavour == y.pdgId
    #matchResult = matchObjectCollectionMultiple(outJet,genPartCollection,dRmax=0.4,presel=linJetPresel)
    #matchResult = matchObjectCollection(outJet,genPartCollection,dRmax=0.4)
    #print(type(matchResult))


def linkGenJet(inJet, inJetIdx, jetCollection, genJetCollection, genPartCollection, linkChain=None):
    """process input Jet, find lineage within gen particles

    if isGenJet=True, activate linking step from GenJet to GenParts"""
    if not (genPartCollection and genJetCollection):
        raise RuntimeException("linkGenJet requires the genJet, and genPart collections")
    if linkChain==None:
        linkChain = []
    #Set partIdx if an appropriate one is passed in ("find" triggers a search within this method)
    jetIdx = -1
    typeName = "GenJet"
    if inJetIdx == "find":
        for Idx, jet in enumerate(genJetCollection):
            if inJet == jet:
                jetIdx = Idx
                break
    elif -1 < inJetIdx < len(genJetCollection):
        jetIdx = inJetIdx
    else:
        jetIdx = -999
    #Compute list of endnodes in genPart collection, by subtracting the set of those which are
    # linked to by another gen particle (from genPartIdxMother in the entire collection)
    # from the set enumerating the ones which should be in the collection by length calculation
    allgens = set([x for x in xrange(len(genPartCollection)) ])
    mothgens = set([gen.genPartIdxMother for gen in genPartCollection ])
    lastgens = allgens - mothgens
    #print(allgens)
    #print(mothgens)
    #print(lastgens)
    lastGenPartCollection = [genPartCollection[x] for x in lastgens]
    #print(lastGenPartCollection)
    #temporary deltaR with a default (only stored under logic error) and a calculation against the 'head' of the chain
    tmpDeltaR = -9999.786
    if len(linkChain) > 0:
        tmpDeltaR = deltaR(inJet, linkChain[0][6])
    elif len(linkChain) == 0:
        tmpDeltaR = 0.0
    linkChain.append( (typeName, jetIdx, "FIXME", inJet.hadronFlavour, tmpDeltaR, -987654321, inJet) )

    #Get the list of matching lastGenParts (no daughters) by calling matchObj...Multiple with key [inJet], 
    # since we only ask for matches against the inJet and not multiple objects at once (list of inJets)
    partMatches = matchObjectCollectionMultiple([inJet], lastGenPartCollection, dRmax=0.4)[inJet]
######    print("Matches:" + str(len(partMatches)))
    tmpLinkChains = []
    for m, match in enumerate(partMatches):
        tmpLinkChains.append(copy.deepcopy(linkChain))
        #tmpLinkChains.append(linkGenPart(match, "find", genPartCollection))
        linkGenPart(match, "find", genPartCollection, linkChain=tmpLinkChains[m])
        for jj in xrange(len(tmpLinkChains[m])):
            #print(str(tmpLinkChains[m][jj]))
            pass
######        print("\n")
#       tmpLinkChain = []
#       tmpLinkChain += linkChain
#       for subchain in tmpLinkChains:
#           #MASSIVE WARNING: Deepcopy made in loop above cannot be properly accessed by strLink method called outside of this method!
#           #Must strip them from any chains passed higher up
#           tmpLinkChain += subchain[2:]
#       return tmpLinkChain

    tmpLinkChain = []
    tmpLinkChain.append(linkChain[:])
    for subchain in tmpLinkChains:
        tmpLinkChain.append(subchain[2:])
    return tmpLinkChain

#def testGenAncestry(gen, genPartCollection, Idx=None, depth=0, chain=None):
#    """
#    Test whether the passed gen particle is linked to Gen Particle with Idx selected.
#    
#    Idx must be an integer greater than -1, depth should not be specified for recursion to return proper value.
#    Returns True if a matching Ancestor exists, plus the depth at which it was found.
#    A depth of 1 means the gen particle's ancestor is its mother.
#    If a mother Idx of -1 is encountered, the algorithm returns (False, -1)
#    """
#    mothIdx = gen.genPartIdxMother
#    if chain == None:
#        chain = []
#    chain.append(mothIdx)
#    if mothIdx < 0:
#        return (False, -1, chain)
#    if type(Idx) is not int:
#        raise ValueError("testGenAncestry requires an integer for Idx greater than -1. See help(testGenAncestry)")
#    elif Idx > -1:
#        #if type(Idx) is list or type(Idx) is set:
#        #    if gen.genPartIdxMother in Idx:
#        #        return True, 
#        if mothIdx == Idx:
#            return (True, depth+1, chain)
#        else:
#            return testGenAncestry(genPartCollection[mothIdx], genPartCollection, Idx=Idx, depth=depth+1, chain=chain)      
#    else:
#        raise ValueError("testGenAncestry requires an integer for Idx greater than -1. See help(testGenAncestry)")
#        
#def getGenAncestry(gen, genPartCollection, chain=None):
#    """
#    Get ancestry of the passed gen particle.
#    
#    Returns a list of the Idx of each gen particle the gen is descended from, up to Idx=0 (initial parton)
#    chain should be left as None unless you have a list to continue appending Idx's to.
#    """
#    mothIdx = gen.genPartIdxMother
#    if chain == None:
#        chain = []
#    chain.append(mothIdx)
#    if mothIdx < 0:
#        return chain
#    else:
#        return getGenAncestry(genPartCollection[mothIdx], genPartCollection, chain=chain)      


def getFiles(query=None, globPath=None, globFileExp="*.root", globSort=lambda f: int(f.split('_')[-1].replace('.root', '')), dbsDataset=None, inFileName=None, redir="", outFileName=None, verbose=False):
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
        if query:
            if "dbs:" in query:
                cmd = 'dasgoclient --query="file dataset={0:s}" > {1:s}'.format(query.replace("dbs:",""),f.name)
                if verbose:
                    print("dbs query reformatted to:\n\t" + query)
                os.system(cmd)
                for line in f:
                    tmpName = redir + line
                    tmpName = tmpName.rstrip()
                    fileList.append(tmpName)
            elif "glob:" in query:
                query_stripped = query.replace("glob:","")
                fileList = glob(query_stripped)
            elif "list:" in query:
                query_stripped = query.replace("list:","")
                fileList = []
                with open(query_stripped) as in_f:
                    for line in in_f:
                        fileList.append(redir + line.rstrip())
            return fileList
            #Kept as reminder for how to produce list with these files for xrootd transfers
                # if "root://eoshome-{0:s}.cern.ch/".format(get_username()[0]) not in query_stripped:
                #     query = "root://eoshome-{0:s}.cern.ch/".format(get_username()[0]) + query_stripped
                #     if verbose:
                #         print("eoshome query reformatted to:\n\t" + query)
            # elif "eoscms:" in query:
            #     if "root://eoscms.cern.ch/" not in query:
            #         query_stripped = query.replace("eoscms:","")
            #         query = "root://eoscms.cern.ch/" + query_stripped
            #         if args.verbose:
            #             print("eoscms query reformatted to:\n\t" + query)
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
