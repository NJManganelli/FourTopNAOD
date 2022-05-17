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

iterator = 0
for era in ["2017", "2018"]:    
    inputSamplesAll, inputSampleCardDict = load_yaml_cards(["../Kai/python/samplecards/{}_NanoAODv7.yaml".format(era),
                                                            "../Kai/python/samplecards/{}_NanoAODv7_additional.yaml".format(era),
                                                        ])
    for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
        for name in inputSampleCardYaml.keys():
            if inputSampleCardYaml[name].get("isData", False):
                # print("Skipping sample due to data of mismatching channel:", era, channel, name)
                continue
            if inputSampleCardYaml[name].get("source", {}).get("NANOv7") is None:
                # print(inputSampleCardYaml[name].get("source", {}))
                print("Skipping sample due to lack of source being available:", era, name)
            else:
                print("if [ $2 -eq " + str(iterator) + " ]; then\n", f"   print Running {era} {name};\n"
                      "    python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input", 
                      "'{}'".format(inputSampleCardYaml[name].get("source", {}).get("NANOv7")), 
                      "--simultaneous 8 --nThreads 8 --write --redir root://cms-xrd-global.cern.ch/ --outdir",
                      f"/eos/cms/store/user/nmangane/NANOv7_slimbookkeeping/{era}/{name} --keep",
                      "run event luminosityBlock genWeight genTtbarId nPSWeight PSWeight nLHEReweightingWeight LHEReweightingWeight nLHEScaleWeight LHEScaleWeight LHEWeight nLHEPdfWeight LHEPdfWeight fixedGridRhoFastjetAll fixedGridRhoFastjetCentralCalo fixedGridRhoFastjetCentralChargedPileUp fixedGridRhoFastjetCentralNeutral fixedGridRhoFastjetCentral LHE nLHEPart LHEPart Pileup",
                      "--tempdir ./ --noProgressBar;",
                      "\nfi"
                )
                iterator += 1
