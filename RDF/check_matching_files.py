#ruamel may create environment conflicts, proceed with caution:
# pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps
import ruamel.yaml as yaml
from FourTopNAOD.RDF.tools.toolbox import load_yaml_cards, getFiles

for card, era in [("../Kai/python/samplecards/2017_NanoAODv7.yaml", "2017"), 
                  ("../Kai/python/samplecards/2017_NanoAODv7_additional.yaml", "2017"), 
                  ("../Kai/python/samplecards/2018_NanoAODv7.yaml", "2018"),
                  ("../Kai/python/samplecards/2018_NanoAODv7_additional.yaml", "2018")
]:
    print(era, card)
    inputSamplesAll, inputSampleCardDict = load_yaml_cards([card])
    for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
        for name in inputSampleCardYaml.keys():
            print(name)
            sample_era = inputSampleCardYaml[name].get("era", "FAILURE")
            assert sample_era == era, "Mismatch in era, maybe you oughta fucking check that!"
            sources = inputSampleCardYaml[name].get("source")
            list1 = getFiles(sources['NANOv7'], redir='root://cms-xrd-global.cern.ch/')
            # list2 = getFiles(sources['NANOv7_CorrNov'], redir='root://cms-xrd-global.cern.ch//pnfs/iihe/cms')
            list2 = getFiles(sources['NANOv7_CorrNov'], redir='root://maite.iihe.ac.be/pnfs/iihe/cms')
            list3 = getFiles(sources['NANOv7_CorrNov__ElEl']) + getFiles(sources['NANOv7_CorrNov__ElEl'].replace(".root", ".empty"))
            list4 = getFiles(sources['NANOv7_CorrNov__ElMu']) + getFiles(sources['NANOv7_CorrNov__ElMu'].replace(".root", ".empty"))
            list5 = getFiles(sources['NANOv7_CorrNov__MuMu']) + getFiles(sources['NANOv7_CorrNov__MuMu'].replace(".root", ".empty"))
            # print('NANOv7', len(list1), 'NANOv7_CorrNov', len(list2))
            if not len(list2) == len(list1): 
                print("NANOv7_CorrNov", len(list1) - len(list2))
                print( str([ll.split("/")[-1] for ll in list1]))
                print( str([ll.split("/")[-1] for ll in list2]) + " :: " + name)
            if not inputSampleCardYaml[name].get("isData", True) and not len(list3) == len(list1): 
                print("NANOv7_CorrNov__ElEl", len(list1) - len(list3))
                print( str([ll.split("/")[-1] for ll in list1]))
                print( str([ll.split("/")[-1] for ll in list3]) + " :: " + name)
            if not inputSampleCardYaml[name].get("isData", True) and not len(list4) == len(list1): 
                print("NANOv7_CorrNov__ElMu", len(list1) - len(list4))
                print( str([ll.split("/")[-1] for ll in list1]))
                print( str([ll.split("/")[-1] for ll in list4]) + " :: " + name)
            if not inputSampleCardYaml[name].get("isData", True) and not len(list5) == len(list1): 
                print("NANOv7_CorrNov__MuMu", len(list1) - len(list5))
                print( str([ll.split("/")[-1] for ll in list1]))
                print( str([ll.split("/")[-1] for ll in list5]) + " :: " + name)
            if inputSampleCardYaml[name].get("isData", True):
                if len(list3) != len(list1) and len(list4) != len(list1) and len(list5) != len(list1) and not (name.startswith("El_") or name.startswith("Mu_")):
                    print( str([ll.split("/")[-1] for ll in list1]))
                    print( str(list(set([ll.split("/")[-1] for ll in list5 + list4 + list3]))) + " :: " + name)
                # print("python ~/Work/CMSSW_10_2_24_patch1/src/FourTopNAOD/RDF/scripts/nanoframe.py --input", 
                #       "'{}'".format(inputSampleCardYaml[name].get("source", {}).get("NANOv7_CorrNov")), 
                #       "--filter", "'{}'".format(code), "--simultaneous 4 --nThreads 8 --write --prefetch",
                #       "--redir root://cms-xrd-global.cern.ch//pnfs/iihe/cms --outdir",
                #       "{}".format("/eos/user/n/nmangane/files/NANOv7_CorrNov/skims/"+era+"/"+name+"/"+channel+"/"))
