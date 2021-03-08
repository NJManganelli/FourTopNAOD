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

channelCut = {"2017": {}, "2018": {}}
channelCut["2018"]["ElMu"] = "(ESV_TriggerAndLeptonLogic_selection & 20480) > 0"
channelCut["2018"]["MuMu"] = "(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) > 0"
channelCut["2018"]["ElEl"] = "(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) > 0"
channelCut["2018"]["Mu"] = "(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) == 0 && (ESV_TriggerAndLeptonLogic_selection & 256) > 0"
channelCut["2018"]["El"] = "(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) == 0 && (ESV_TriggerAndLeptonLogic_selection & 256) == 0 && (ESV_TriggerAndLeptonLogic_selection & 128) > 0"
channelCut["2018"]["MET"] = "(ESV_TriggerAndLeptonLogic_selection & 20480) == 0 && (ESV_TriggerAndLeptonLogic_selection & 2048) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) == 0 && (ESV_TriggerAndLeptonLogic_selection & 256) == 0 && (ESV_TriggerAndLeptonLogic_selection & 128) == 0 && (ESV_TriggerAndLeptonLogic_selection & 14) > 0"
channelCut["2017"]["ElMu"] = "(ESV_TriggerAndLeptonLogic_selection & 24576) > 0"
channelCut["2017"]["MuMu"] = "(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) > 0"
channelCut["2017"]["ElEl"] = "(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) > 0"
channelCut["2017"]["Mu"] = "(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) == 0 && (ESV_TriggerAndLeptonLogic_selection & 128) > 0"
channelCut["2017"]["El"] = "(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) == 0 && (ESV_TriggerAndLeptonLogic_selection & 128) == 0 && (ESV_TriggerAndLeptonLogic_selection & 64) > 0"
channelCut["2017"]["MET"] = "(ESV_TriggerAndLeptonLogic_selection & 24576) == 0 && (ESV_TriggerAndLeptonLogic_selection & 6144) == 0 && (ESV_TriggerAndLeptonLogic_selection & 512) == 0 && (ESV_TriggerAndLeptonLogic_selection & 128) == 0 && (ESV_TriggerAndLeptonLogic_selection & 64) == 0 && (ESV_TriggerAndLeptonLogic_selection & 14) > 0"

for era in ["2017", "2018"]:
    for channel in ["ElMu", "MuMu", "ElEl", "Mu", "El"]: #, "MET"]
        inputSamplesAll, inputSampleCardDict = load_yaml_cards(["../Kai/python/samplecards/{}_NanoAODv7.yaml".format(era)])
        for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
            for name in inputSampleCardYaml.keys():
                if inputSampleCardYaml[name].get("isData", False) and inputSampleCardYaml[name]["channel"] != channel:
                    # print("Skipping sample due to data of mismatching channel:", era, channel, name)
                    continue
                if inputSampleCardYaml[name].get("source", {}).get("NANOv7_CorrNov") is None:
                    # print(inputSampleCardYaml[name].get("source", {}))
                    print("Skipping sample due to lack of source being available:", era, channel, name)
                else:
                    print("print", era, channel, name)
                    print("python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input", 
                          "'{}'".format(inputSampleCardYaml[name].get("source", {}).get("NANOv7_CorrNov")), 
                          "--filter '{cutname}>==>{cut}'".format(cutname=channel, cut=channelCut[era][channel]),
                          "--simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/user/n/nmangane/files/NANOv7_CorrNov/skims/{era}/{name}/{channel}/".format(era=era, name=name, channel=channel))
                          # "--simultaneous 4 --nThreads 8 --write --prefetch --redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir /eos/cms/store/user/nmangane/NANOv7_CorrNov/skims/{era}/{name}/{channel}/".format(era=era, name=name, channel=channel))

