#ruamel may create environment conflicts, proceed with caution:
# pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps
import ruamel.yaml as yaml
from FourTopNAOD.RDF.tools.toolbox import load_yaml_cards, getFiles, write_yaml_cards

for card, era in [("../Kai/python/samplecards/2017_NanoAODv7.yaml", "2017"), 
                  ("../Kai/python/samplecards/2018_NanoAODv7.yaml", "2018"),
]:
    print(era, card)
    inputSamplesAll, inputSampleCardDict = load_yaml_cards([card])
    for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
        for name in inputSampleCardYaml.keys():
            # print(name)
            sample_era = inputSampleCardYaml[name].get("era", "FAILURE")
            assert sample_era == era, "Mismatch in era, maybe you oughta fucking check that!"
            # if inputSampleCardYaml[name].get("isData", True):
            if "splitProcess" in inputSampleCardYaml[name].keys():
                print(name)
                XS = inputSampleCardYaml[name]["crossSection"]
                residual = XS
                for process in inputSampleCardYaml[name]['splitProcess']['processes'].keys():
                    print('effectiveCrossSection', inputSampleCardYaml[name]['splitProcess']['processes'][process]['effectiveCrossSection'])
                    print('nominalXS', inputSampleCardYaml[name]['splitProcess']['processes'][process]['nominalXS'])
                    inputSampleCardYaml[name]['splitProcess']['processes'][process]['effectiveCrossSection'] = inputSampleCardYaml[name]['splitProcess']['processes'][process]['nominalXS']
                    print('effectiveCrossSection', inputSampleCardYaml[name]['splitProcess']['processes'][process]['effectiveCrossSection'])
                    residual -= inputSampleCardYaml[name]['splitProcess']['processes'][process]['effectiveCrossSection']
                if abs(residual) > 1e-4:
                    print(f"{name} residual =", residual / XS)
                print("\n\n")
        #             if dName == "sumWeights::Sum": print(preProcessName, " updated in yaml file for split process")
        #             inputSampleCard[sampleName]['splitProcess']['processes'][preProcessName][parseDName[0]] = dNode.GetValue()
    write_yaml_cards(inputSampleCardDict, ".junk")
        # with open(inputSampleCardName.replace(".yaml", ".roundtrip.test.yaml"), "w") as of:
        #     of.write(yaml.dump(inputSampleCardYaml, Dumper=yaml.RoundTripDumper))
