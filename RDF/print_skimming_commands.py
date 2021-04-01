#ruamel may create environment conflicts, proceed with caution:
# pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps
import ruamel.yaml as yaml
def load_yaml_cards(sample_cards):
    SampleList = None
    SampleDict = dict()
    try:
        import ruamel.yaml
        ruamel.yaml.preserve_quotes = True
    except:
        print("Cannot load ruamel package to convert yaml file. Consider installing in a virtual environment with 'pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps'")

    for scard in sample_cards:
        with open(scard, "r") as sample:
            if SampleList is None:
                SampleList = ruamel.yaml.load(sample, Loader=ruamel.yaml.RoundTripLoader)
            else:
                SampleList.update(ruamel.yaml.load(sample, Loader=ruamel.yaml.RoundTripLoader))

    for scard in sample_cards:
        with open(scard, "r") as sample:
            SampleDict[scard] = ruamel.yaml.load(sample, Loader=ruamel.yaml.RoundTripLoader)
    return SampleList, SampleDict

inputSamplesAll, inputSampleCardDict = load_yaml_cards(["../Kai/python/samplecards/2018_NanoAODv7_additional.yaml"])
# inputSamplesAll, inputSampleCardDict = load_yaml_cards(["../Kai/python/samplecards/2017_NanoAODv7_additional.yaml"])
for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
    for name in inputSampleCardYaml.keys():
        print("print " + name)
        era = inputSampleCardYaml[name].get("era", "FAILURE")
        for channel, code in {"2017": {"ElMu": "ElMu=(ESV_TriggerAndLeptonLogic_selection & 24576) > 0", 
                                       "MuMu": "MuMu=(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) > 0",
                                       "ElEl": "ElEl=(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) > 0"},
                              "2018": {"ElMu": "ElMu=(ESV_TriggerAndLeptonLogic_selection & 20480) > 0",
                                       "MuMu": "MuMu=(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) > 0",
                                       "ElEl": "ElEl=(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) > 0"}
        }[era].items():
            print("python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input", 
                  "'{}'".format(inputSampleCardYaml[name].get("source", {}).get("NANOv7_CorrNov")), 
                  "--filter", "'{}'".format(code), "--simultaneous 4 --nThreads 8 --write --prefetch",
                  "--redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir",
                  "{}".format("/eos/user/n/nmangane/files/NANOv7_CorrNov/skims/"+era+"/"+name+"/"+channel+"/"))

# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/nmangane-NoveCampaign-31deb7c86682c648bf5094175e82e051/USER instance=prod/phys03' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 24576) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2017/ST_tW/ElMu/

# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/nmangane-NoveCampaign-31deb7c86682c648bf5094175e82e051/USER instance=prod/phys03' --filter 'MuMu>==>(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2017/ST_tW/MuMu/

# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'dbs:/ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8/nmangane-NoveCampaign-31deb7c86682c648bf5094175e82e051/USER instance=prod/phys03' --filter 'ElEl>==>(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2017/ST_tW/ElEl/

# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:/eos/home-n/nmangane/analysis/LongTermFilelists/2018__NANOv7_CorrNov__ElMu_A.txt' --filter 'ElMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ElMu_A/ElMu/

# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:/eos/home-n/nmangane/analysis/LongTermFilelists/2018__NANOv7_CorrNov__MuMu_A.txt' --filter 'MuMu>==>(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/MuMu_A/MuMu/

# python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input 'list:/eos/home-n/nmangane/analysis/LongTermFilelists/2018__NANOv7_CorrNov__ElEl_A.txt' --filter 'ElEl>==>(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) > 0' --simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/2018/ElEl_A/ElEl/
