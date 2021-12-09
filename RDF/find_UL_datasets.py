#ruamel may create environment conflicts, proceed with caution:
# pip install --user 'ruamel.yaml<0.16,>0.15.95' --no-deps
import ruamel.yaml as yaml
import subprocess, os
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

inputSamplesAll, inputSampleCardDict = load_yaml_cards(["../Kai/python/samplecards/2018_NanoAODv7.yaml", 
                                                        "../Kai/python/samplecards/2018_NanoAODv7_additional.yaml"])
# inputSamplesAll, inputSampleCardDict = load_yaml_cards(["../Kai/python/samplecards/2017_NanoAODv7_additional.yaml"])
for inputSampleCardName, inputSampleCardYaml in inputSampleCardDict.items():
    for name in inputSampleCardYaml.keys():
        _, first, second, third = inputSampleCardYaml[name]['source']['NANOv7'].split("/")
        if inputSampleCardYaml[name]['isData']:
            new_second = "Run201*UL201*_NanoAODv9*"
        else:
            new_second = "RunIISummer20UL*_NanoAOD*v9*"
        query = "/".join(['dasgoclient --query="dataset=', first, new_second, third + '"'])
        # print("print " + name)
        # print(query)
        my_env = os.environ
        # my_env["PATH"] = "/usr/sbin:/sbin:" + my_env["PATH"]
        result = subprocess.Popen(query, env=my_env, shell=True)

