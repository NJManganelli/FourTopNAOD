from __future__ import print_function
import os, time
import ROOT
import collections
from IPython.display import Image, display, SVG
#import graphviz

useSpark = True
if useSpark:
    import PyRDF
    #PyRDF.use("spark", {'npartitions': '64'}) #was 32 in example
    PyRDF.use("local")
    RDF = PyRDF.RDataFrame
else:
    ROOT.ROOT.EnableImplicitMT()
    RS = ROOT.ROOT
    RDF = RS.RDataFrame

#FIXME: Need filter efficiency calculated for single lepton generator filtered sample. First approximation will be from MCCM (0.15) but as seen before, it's not ideal. 
#May need to recalculate using genWeight/sumWeights instead of sign(genWeight)/(nPositiveEvents - nNegativeEvents), confirm if there's any difference.
lumi = {"2017": 41.53,
        "2018": 1}
era = "2017"
leg_dict = {"ttbar_DL-GF": ROOT.kAzure-2,
            "ttbar_DL": ROOT.kRed,
            "ttbar_SL-GF": ROOT.kYellow,
            "ttbar_SL": ROOT.kCyan,
           }
source_DL_V2 = {
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar_DL"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
        "sourceSPARK": ["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/2A0100C0-5A95-0145-B62F-0CA9D9639F68.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/4ADB829B-0293-0D48-8AEA-31AAFD1936B8.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/FF239AE9-D713-5147-BB2C-FAFF45770541.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/FEFFCB04-A0CD-2945-BB46-D0D9013CD4F4.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/FB37F4B8-4878-AC41-80AD-1AC7BCC96FBF.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/F86F8AAA-A400-7340-A1B2-1BEDDD5C634C.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/F61A315A-0C50-F545-9D27-5821F2A16665.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/E8AEC963-FB46-604E-BFCA-4BAD27E9C457.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/E5D51928-D702-3B4E-93FF-10B011657478.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/E08462B0-0C0E-E54F-BFC6-8B09D73ABD59.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/DE610AC6-52C8-F243-B726-266E986C67C7.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/DC5D2C4D-0FA1-9448-BDAD-8B3212A417AC.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/DB9DB17D-00F1-C540-BF6A-0A3314CD31F7.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/DB2F7B58-0EFA-B241-B52A-8A14E3DC5356.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/DB097816-5864-3640-A472-37E4518131AD.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/D8B47A61-B47A-494C-B6B7-E2BE3F250C9E.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/D3582719-8222-9A48-8FD6-FE7CA90C10F2.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/CD496386-C278-0C4C-8F7E-BE62903ADD57.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/CAACE0A1-EA68-154E-8F4E-2D2298D087ED.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/C805AA80-6F12-E84C-B5F6-6AC7CDBDD568.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/C329E2BB-0C74-A640-9F7B-DFC5505DA4A9.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/C2DFBA51-FCE3-954D-B2FD-050DCF3BA2AE.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/C0CFCDB9-4C19-9243-B1F5-4CC8B34A5F53.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/B8C82709-DAFE-DE46-8207-ECB035DBE32C.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/B5A0D925-E6D2-964F-8FBF-B6DCF8311983.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/B40D0E48-C30F-144C-954D-C79F2E74BAC0.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/B1C73F9C-E932-E148-8178-AC2E912F77C7.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/B0CDDA70-01A8-DA47-A6DA-7E518609D349.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/A65E69A8-4F9A-6B4B-889E-787546455F50.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/A1ACAB6F-3CE4-8E4B-A148-5CFB78AAB153.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/9D587515-51E3-FB41-856E-41406CF1AA94.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/9C4ECF47-F241-E841-9017-524C3FE3F782.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/99E411C5-8086-3C41-B5E0-8356B93A62AE.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/9826D66E-2230-9A4E-AF59-99404C9CA0F8.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/96EA0AD0-7850-9742-800B-8732972FE897.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/96787088-4414-194C-9045-CB7B81923664.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/93648D0C-3759-5A4F-890B-5275C66BC423.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/8A267C63-CC35-3D49-9AA9-1D5E89C3FA8A.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/854ACC40-D83A-CB4D-8096-A3D5AB0CCEB7.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/8482B4BA-D619-CA42-92B8-D8AC7EE3E14A.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/824DD978-02EE-8540-84F4-45C81D901868.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/73C3619B-A47F-1D49-B4EC-E347B144C067.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/7027E474-2CF4-354C-928D-26A03AC64602.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/6974B155-E6FB-6046-8CF0-861DD75C65E9.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/67897CF3-3F11-AC48-9CB2-926BF1CF2088.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/66B78AE0-D4B0-A04D-B103-DB78ACC047E7.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/6530E34B-0886-6C41-A78A-74B945B9E23E.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/63BA2496-580D-CE4A-A9D5-FC81E299FEAC.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/5BB4B096-AC3F-BD49-B599-D43E0176890F.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/5AEEEC98-7170-114E-B4FF-FA3F9BDC3217.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/5A8E9758-665D-264D-9ACF-A7C69D56523B.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/55B03D69-AE5B-6142-80A6-1517F2B9F6CC.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/54EC1465-9EDA-7B40-8042-1FD34081497A.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/51640F96-C070-694F-A3EA-59507F27FA3B.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/33B12362-B2B9-2D46-ADBF-8BB30E9949B0.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/2C64BBC9-4082-424C-81F2-D0ED3406CBC9.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/52B5612E-888D-FA4C-8C83-C60104F70DD3.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/544DB558-0C6F-EC41-BFDC-B6EE46EC986F.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/46239DBE-8E5E-9744-B7F4-B72B44803619.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/460F269F-337C-7F4F-92FD-5A18525B33F8.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/42D378EC-A09E-C945-99C7-BC1F00E41D88.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/4179956C-6AC8-7041-AC46-DC2DE881F788.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/3992DEA8-A6A0-F946-9563-1FA0AACC9A0C.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/38E81C59-132D-6847-B0D8-77A1D0D5ED56.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/1663D9BD-F7FA-784B-A313-D540068B4BAB.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/14F0276E-7349-2741-9186-B5713E7EBEA8.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/0AA9D783-4D4C-924A-9B92-709702ED7915.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/03263E02-B201-3540-BE86-03A3DFF898F2.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/0010502D-08FD-9A45-9B8F-A2FB501C776D.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/1930F644-A4DF-9441-BCDE-48B2D6045607.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/1BE985E2-0F6A-7B4D-98D8-A5CC8BDF64C0.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/1C71F860-D8D2-E342-9FA3-A4815ABD60EA.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_new_pmx_102X_mc2017_realistic_v7-v1/110000/27A7A157-10B1-024C-AD51-53D05797FB47.root",
        ],
        "stitch": {"mode": 'Flag', "condition": 'Fail', "channel": 'DL'}
        },
    "tt_DL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8510388,
        "nEventsPositive": 8467543,
        "nEventsNegative": 42845,
        "sumWeights": 612101836.284397,
        "sumWeights2": 44925503249.097206,
        "isSignal": False,
        "crossSection": 89.0482, #1.4705, #After applying filter efficiency...
        "color": leg_dict["ttbar_DL-GF"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
        "sourceSPARK": ["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/F600BA86-6C79-F14E-843F-A18E5A82DD01.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/536EBC00-F7F9-B140-AEDC-ADE2B39AC3FA.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/464A3326-28B7-EC4D-834A-F9B8B826CA0A.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/3E4CF0E5-D1E3-BD48-AA6B-5E4549BE0B1B.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/3DFC9865-DFDA-6040-B0F8-009206A5D631.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/B28BA460-6A5A-8542-A237-BDA8F4B4AA51.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/7CE6ACA8-A74E-2342-8B4D-6CC1B26F4209.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/7AC648FD-8C1D-6647-BA0F-BAA05E97DA00.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/681BF9B5-1040-8547-A7E0-7CC780A404C5.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/4F512FE3-7DD1-9C46-A949-0FEFB217B957.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/2F732BBD-2C2C-5E4E-A5DC-48ECF57636EB.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/100000/CED06574-B2B8-F74A-9214-8FC0861D12DC.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/100000/C86A7E85-E6A1-F847-BE52-99E73DC04808.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/100000/C309E308-2D85-3341-969B-DD8154E1E5C3.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/100000/8FAA6F0A-6A3C-1D4E-A554-B4151598282C.root",
                       "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTTo2L2Nu_HT500Njet7_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/100000/2201EDF5-C5FE-C148-AE83-27F9240FBF4A.root",
                       ],
        "stitch": {"mode": 'Flag', "condition": 'Pass', "channel": 'DL'}
        },
}
source_SL_V2 = {
    "tt_SL":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar_SL"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
        "sourceSPARK": ["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/D686FCCA-429E-C044-8B98-B99D55C65859.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/D4EF446F-CF32-A445-B8D9-03FC868BCFBA.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/CC62B699-A9FF-394B-8C8C-4E3856FD98D2.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/C421BAF3-F52B-E74D-98B9-49B24650B835.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/BA76C3A0-5953-9D4B-8033-EECFFDA51A6A.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/A2A53855-CB90-AD46-B70C-604615947D35.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/94F03AF3-B18C-9A45-BD61-2DD6A82BCF4A.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/3DB84A5A-5479-FD46-A6F1-2F50490F7189.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/33C03093-04D1-1D49-97F4-BFFD2365B994.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/32A69C33-0262-4449-BF5D-AD1BE1A47C85.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/23636497-18C3-3842-90E7-9FB8C1402680.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/EF0B6094-19C2-9745-BFB5-234D8AD41332.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/E502CBAE-CFE6-9C46-8F24-724A0075DA19.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/D7909568-5273-3148-ABEA-F7CB0D1866CE.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/D394B8AA-7BB2-DC44-94CD-EE41978E6ACC.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/C11F6A73-627C-F341-9AD1-E91B8A4A92EF.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/A6746E57-C754-D149-8AC8-6FE6DD73E0E5.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/A2D14FA4-A93C-4D43-AB87-13BDA4D1C7D6.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/A213145C-B8BB-3A4F-A308-83D4C63D1E00.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/A1DC2776-3A7D-4047-A0E4-1094D2D8FA40.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/9CD2FFBB-AA38-3C46-99E3-7641F7F78013.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/93AF8675-716E-4F46-8179-775D4492D567.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/92963635-0E8A-2D47-A164-F46B6C7F5C0E.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/8A67C2BD-4E12-7643-93E8-A82A90E0F96C.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/68BAB3CE-588B-CB4F-B83E-E0A97F41ABDF.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/67674532-76D0-3940-B196-F3135299B87C.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/672FCC65-B125-0D45-B10E-128DBF16B460.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/5C722357-ADDC-9B44-B160-6EC6F283C4D3.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/57C0579F-1A15-B74F-A7F6-81706D7CA364.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/5202C039-E420-DC4B-8D33-264889424EFD.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/41B39F60-7580-A24F-BFD1-73F2FABC8451.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/3C940579-D915-D44D-A9B9-1155EAC0CB4A.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/3845EC7C-6772-D442-A88D-7C183BD4BDEC.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/37F6FD55-B43F-994E-B278-6E25EE225CFF.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/3368BAF5-1F1C-2E45-BAFF-715C3CFFCC20.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/2D39555F-38D8-854C-A59F-ED2F04833448.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/2CF31824-76F9-FE40-937A-A2ECB38B8AF1.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/1F01EA75-4A6F-2042-8CE2-5CA5823963AC.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/05DF7E5F-93BC-D749-9ED0-D34609A086B3.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/60000/04449851-5D38-D345-91F4-71A53FF5256F.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/F449E769-0706-A34C-AD7C-F369864CA977.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/C64D9C81-8E64-5A47-9928-B56F107FF36B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/98ED7A34-73CE-3C47-B90E-E9BE11BC05EE.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/7749A2B3-BA70-FF48-8460-7207A7049E13.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/60DB4489-73FC-A04B-8549-5D71E7DA3C95.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/3615F999-6326-D047-A00E-F140CF0EA3D1.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/25AB49E0-1C50-1548-B3AF-D7FEF02EC935.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/0ECACD7C-4805-2F43-86CA-025F41E6D70D.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/044B0BC2-8CA4-2C4B-A766-8519EBE3DE7F.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/F6F9E82C-FD48-C144-8585-4D76DA758BEC.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/EEC376C3-6572-2046-9E46-57FBC413428D.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/ECA31522-5FC7-4549-BAB8-93AB2120C94F.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/EB7998BC-1D8B-4545-BF96-857741C0B086.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/E643F0E5-5DDD-CE46-B5D8-305AC77D3E6B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/E1F00613-6B22-594A-AF4D-AC739D7408E9.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/DF4B8F12-536D-5741-9F18-2AC5CFB86F7D.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/DB90098A-A3F4-D041-8D43-970E7C120E69.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/D947E9AC-296E-7D42-814F-AEC22C308FF0.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/CD8A7E48-90B2-B14D-A43C-F1344CEE6237.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/C290373E-7127-3744-87BD-CA11CD1FF62C.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/C16B1661-518D-274A-848A-BE04951109D8.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/BBCE8E57-758F-2941-8F8A-4A6F5F35B2B7.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/AE46BBD3-5D20-DC4C-96DB-36FDA4060242.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/AA8DCC03-0EB6-DB4D-8ECA-3D07C23F44E1.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/A194E3B2-7853-C54E-AB5A-5ECCD2F72726.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/9F9008FA-6F7E-4548-A188-79AE98F871FA.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/935AA661-8BD7-0645-B431-5EBB37769B3B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/92D19833-5F3A-3B43-B402-385111B8666B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/8C9C4F6F-3E49-0F4C-B805-3B5D5F747E66.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/8437D94E-5F61-9149-8B3A-6B908DBBE95B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/7CCC70B7-0333-164C-8E4E-8979C4AAC3CD.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/778E67D2-6683-EE45-8FA3-4A852DF0A938.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/76F7EE18-97F1-194B-9346-13C734CD1C1C.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/6EB064B9-4337-414E-83BC-9BB2F82A2D67.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/5F9459CA-8505-C34B-879E-7C87578B7951.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/5D1A2264-B851-6A45-8340-82511047BA48.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/56D3202D-308D-984E-8B34-7F9DA0AB20CF.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/44C5336D-0BF7-5B4D-804F-5B5DE682C8C9.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/3345DAC7-48F8-1C43-8C3B-AA477027C578.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/3304ABCD-DD82-CC48-B1AF-A6DAE1CEC349.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/2D5E8874-07C9-724D-916C-18F8D56A4361.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/2A97FB56-AF3D-604F-B081-6489818B1EDC.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/28A22CFC-E78B-FC4A-ACBA-22FA36DFE3E5.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/1FD04315-053C-8846-9401-AA5210544F88.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/159803B7-8A47-F844-A329-27639CFAC6A9.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/148539FB-8BFA-E343-8E40-EFEC5DBF7067.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/114960A1-1F78-744F-A828-00B3FB77831D.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/05F2E7D5-86BF-344C-A87E-EFA3DD283F9B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/01150437-2B0C-BF4B-A6EA-6ECD4719D911.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/FAEF2067-51FE-CF4E-AD20-C70DE01C137F.root",                       
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/F751A8E8-B25E-9D49-AB19-38E9BD2AC04F.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/EEBE73AA-42D3-0A4E-B8C3-01D9F9660619.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/D34F052B-6717-E148-9A2C-3AE4D5C94636.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/D090CFDA-5B5B-A941-BB73-35F17D6EEB89.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/C5BE441F-5595-094B-A4D9-7F9AD6B50B6B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/C510D032-8263-1B43-9AB1-E9ECF623F676.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/B9F4AAAB-E750-7A47-B202-3DC7D88A21A0.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/B6CA8915-7D4B-8F4F-BE61-7F90C1DEDB49.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/ACFBB48F-D400-4D42-8D2C-7B7314E1DB06.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/A8F58206-1647-0943-85F0-63D6C199424D.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/A8510BE6-4689-FF46-BF79-C33C39817B8B.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/A55142EF-D15D-F74D-90B2-24FC3ECEA87C.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/93242D28-6E2E-A747-AC68-652871EB88C5.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/8F7736DF-8A39-DF4A-9BFA-476967FE21BA.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/8B8867F9-2577-5047-A983-02C244D1A2B9.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/7DD1CB31-0F41-AD42-A508-290B0A423487.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/722319BE-C2FC-7949-82AB-E9B28C302C4D.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/712A4396-C950-4B45-A612-977C3B3D3BD5.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/6F191C45-0C7C-874D-BD72-BEF32AE3F819.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/659F7FAC-15D6-7549-ACE7-AED40975CAE9.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/632BCD48-C17D-3F4F-BF66-10C33F1F5288.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/482573D0-CC42-3F43-BFD6-2E5ECB10D6DA.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/431557AD-7DB2-7E4B-8522-9150B23E8817.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/39635D4F-52C4-EA41-85D4-141BFFE2799A.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/38EAF19E-755F-2A49-A148-9F0738FED364.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/2D5CF857-B3AF-0149-B81A-80E092B846DC.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/177636D2-BAFA-7040-B65B-E013CC6EBB89.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/16C31B91-ADD0-8548-B34E-67366A60BA61.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/0F0E5869-C901-C14D-AEDD-B14D4A947E87.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/110000/0D2EE97B-AC68-E24A-A451-1D5127322521.root",
                       ],
        "stitch": {"mode": 'Flag', "condition": 'Fail', "channel": 'SL'}
        },
    "tt_SL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8836856,
        "nEventsPositive": 8794464,
        "nEventsNegative": 42392,
        "sumWeights": 2653328498.476976,
        "sumWeights2": 812201885978.209229,
        "isSignal": False,
        "crossSection": 366.2073, #???,
        "color": leg_dict["ttbar_SL-GF"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-GF_2017_v2.root",
        "sourceSPARK": ["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/0E27F419-ADDE-1E4C-AC0A-130DA36C1FA6.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/F5AEB3BB-5D35-5949-A0A3-2664AFFBAA94.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/70000/4741AE94-855A-8344-A1DA-84AAD948D419.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/F412C6EF-49E3-F94F-812D-14FCA6B78C51.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/D2B7659C-9C1E-094A-B0E8-A264BB57EB67.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/82FBCA1B-F11F-564B-9075-35B4486B45B6.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/6AF680DD-7ED5-7046-9906-DF0A7174EA61.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/68B095D2-20EC-1A4D-A93D-F89AF49BE9F6.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/4E7674E4-536E-B048-B646-DB8012B29D50.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/30000/3D2CE6BC-4EA6-834A-A036-F4E9D91D97F4.root ",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/DEB7211A-47D0-474B-A383-770775D86F01.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/CB0C5BE0-3698-8E4B-B49A-57F0A10F602F.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/5BA21135-FE65-E449-B954-2640B793FDA0.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/4A3A4BC6-ACC4-A642-AC3B-3B75E43E3ECE.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/28D3A741-5A66-AA4D-AB2C-4402F0224331.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/250000/1E1E3A21-1E31-D843-BCFB-50AE65A615C0.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/907839C8-A184-484C-9BED-44BEA845FDBB.root",
                        "root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv5/TTToSemiLepton_HT500Njet9_TuneCP5_PSweights_13TeV-powheg-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano1June2019_102X_mc2017_realistic_v7-v1/120000/294AF708-5AAC-2045-A851-6E1676E295E8.root",],
        "stitch": {"mode": 'Flag', "condition": 'Pass', "channel": 'SL'}
        },
}
stitched_DL_V2 = {
    "tt_DL":{
        "era": "2017",
        "isData": False,
        "nEvents": 69098644,
        "nEventsPositive": 68818780,
        "nEventsNegative": 279864,
        "sumWeights": 4980769113.241218,
        "sumWeights2": 364913493679.955078,
        "isSignal": False,
        "crossSection": 89.0482,
        "color": leg_dict["ttbar_DL"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-*_2017_v2.root",
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-2_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-3_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-4_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-5_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-6_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-7_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-8_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-9_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-10_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-11_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-12_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-13_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-NOM-14_2017_v2.root",],
        "stitch": {"mode": 'Flag', "condition": 'Fail', "channel": 'DL'}
        },
    "tt_DL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8510388,
        "nEventsPositive": 8467543,
        "nEventsNegative": 42845,
        "sumWeights": 612101836.284397,
        "sumWeights2": 44925503249.097206,
        "isSignal": False,
        "crossSection": 1.4705,
        "color": leg_dict["ttbar_DL-GF"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-*_2017_v2.root",
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-1_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-2_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-3_2017_v2.root",
                       "root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_DL-GF-4_2017_v2.root",],
        "stitch": {"mode": 'Flag', "condition": 'Pass', "channel": 'DL'}
        },
}
stitched_SL_V2 = {
    "tt_SL":{
        "era": "2017",
        "isData": False,
        "nEvents": 20122010,
        "nEventsPositive": 20040607,
        "nEventsNegative": 81403,
        "sumWeights": 6052480345.748356,
        "sumWeights2": 1850350248120.376221,
        "isSignal": False,
        "crossSection": 366.2073,
        "color": leg_dict["ttbar_SL"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-NOM_2017_v2.root",],
        "stitch": {"mode": 'Flag', "condition": 'Fail', "channel": 'SL'}
        },
    "tt_SL-GF":{
        "era": "2017",
        "isData": False,
        "nEvents": 8836856,
        "nEventsPositive": 8794464,
        "nEventsNegative": 42392,
        "sumWeights": 2653328498.476976,
        "sumWeights2": 812201885978.209229,
        "isSignal": False,
        "crossSection": 6,
        "color": leg_dict["ttbar_SL-GF"],
        "source": "/eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-GF_2017_v2.root",
        "sourceSPARK": ["root://eoshome-n.cern.ch//eos/user/n/nmangane/SWAN_projects/LogicChainRDF/FilesV2/tt_SL-GF_2017_v2.root"],
        "stitch": {"mode": 'Flag', "condition": 'Pass', "channel": 'SL'}
        },
}

def defineStitchVars(input_df, crossSection=0, sumWeights=-1, lumi=0,
                     nEvents=-1, nEventsPositive=2, nEventsNegative=1,
                     era="2017", verbose=False):
    stitchDict = {'2016': {'SL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None},
                                    'DL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None}
                                },
                           '2017': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                },
                           '2018': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                }
                       }
    stitchSL = stitchDict[era]['SL']
    stitchDL = stitchDict[era]['DL']                                                                                                                                                                      
    
    defines = collections.OrderedDict()
    defines["wgt_SUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / {sumw:s}"\
            .format(xs=str(crossSection), lumi=str(lumi), sumw=str(sumWeights))
    defines["wgt_NUMW"] = "({xs:s} * {lumi:s} * 1000 * genWeight) / (abs(genWeight) * ( {nevtp:s} - {nevtn:s} ) )"\
            .format(xs=str(crossSection), lumi=str(lumi), nevt=str(nEvents),
                    nevtp=str(nEventsPositive), nevtn=str(nEventsNegative))
    defines["jet_mask"] = "GenJet_pt > 30"
    defines["HT_mask"] = "GenJet_pt > 30 && GenJet_eta < 2.4"
    defines["lep_mask"] = "abs(LHEPart_pdgId) == 15 || abs(LHEPart_pdgId) == 13 || abs(LHEPart_pdgId) == 11"
    defines["stitch_nGenLep"] = "LHEPart_pdgId[lep_mask].size()"
    defines["stitch_nGenJet"] = "GenJet_pt[jet_mask].size()"
    defines["stitch_GenHT"] = "Sum(GenJet_pt[HT_mask])"
    rdf = input_df
    for k, v in defines.items():
        if verbose:
            print("Define(\"{}\", \"{}\")".format(k, v))
        rdf = rdf.Define(k, v)
    return rdf

def fillStitchVars(input_df, weights=["wgt_SUMW", "wgt_NUMW"], Cache=None,
                   HTBinWidth=50, desiredHTMin=200, desiredHTMax=800,
                   era="2017", channel="DL", source="Filtered", verbose=False):
    stitchDict = {'2016': {'SL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None},
                                    'DL': {'nGenJets': None,
                                           'nGenLeps': None,
                                           'GenHT': None}
                                },
                           '2017': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                },
                           '2018': {'SL': {'nGenJets': 9,
                                           'nGenLeps': 1,
                                           'GenHT': 500},
                                    'DL': {'nGenJets': 7,
                                           'nGenLeps': 2,
                                           'GenHT': 500}
                                }
                       }
    stitchSL = stitchDict[era]['SL']
    stitchDL = stitchDict[era]['DL']
    #Binning variables for determining continuity or normalization factor
    #nGenJet and nGenLep (just hardcoded here, don't see much use for varying these that much
    nGenJetMin = 2
    nGenJetMax = 20
    nGenJetBins = nGenJetMax - nGenJetMin
    nGenLepMin = 0
    nGenLepMax = 5
    nGenLepBins = nGenLepMax - nGenLepMin

    #HT
    HTBinWidth = HTBinWidth
    desiredHTMin = desiredHTMin
    desiredHTMax = desiredHTMax
    cutValue = stitchDict[era][channel]['GenHT']
    HTMin = cutValue
    HTMax = cutValue
    HTBins = 0
    while (HTMin > desiredHTMin):
        HTMin -= HTBinWidth
        HTBins += 1
    while (HTMax < desiredHTMax):
        HTMax += HTBinWidth
        HTBins += 1
    if verbose: 
        print("For desiredHTMin={0:<.1f} and desiredHTMax={1:<.1f}, with HTBinWidth={2:<.1f}, the calculated HTMin={3:<.1f} and HTMax={4:<.1f} with HTBins={5:<d}".format(desiredHTMin, desiredHTMax, HTBinWidth, HTMin, HTMax, HTBins))
   
    rdf = input_df
    if Cache == None:
        Cache = {}
    for wgtVar in weights:
        Cache[wgtVar] = {}
        Cache[wgtVar]["nGenLep"] = rdf.Histo1D(("nGenLep[{}]".format(wgtVar), "nGenLep[{}]; nGenLep; Events".format(wgtVar), nGenLepBins, nGenLepMin, nGenLepMax), "stitch_nGenLep", wgtVar)
        Cache[wgtVar]["nGenJet"] = rdf.Histo1D(("nGenJet[{}]".format(wgtVar), "nGenJet[{}]; nGenJet; Events".format(wgtVar), nGenJetBins, nGenJetMin, nGenJetMax), "stitch_nGenJet", wgtVar)
        Cache[wgtVar]["GenHT"] = rdf.Histo1D(("GenHT[{}]".format(wgtVar), "GenHT[{}]; GenHT; Events".format(wgtVar), HTBins, HTMin, HTMax), "stitch_GenHT", wgtVar)
        Cache[wgtVar]["GenHTvnGenJet"] = rdf.Histo2D(("GenHT[{}]".format(wgtVar), "GenHT[{}]; GenHT; Events".format(wgtVar),
                                                      HTBins, HTMin, HTMax, nGenJetBins, nGenJetMin, nGenJetMax),
                                                     "stitch_GenHT", "stitch_nGenJet", wgtVar)
    return Cache

##################################################
##################################################
### CHOOSE SAMPLE DICT AND CHANNEL TO ANALYZE ####
##################################################
##################################################

#Focus on limited set of events at a time
levels_of_interest = set(["baseline"])
#Choose the sample dictionary to run
theSampleDict = source_DL_V2 #Unprocessed NanoAODv5 samples
#theSampleDict = source_SL_V2
#theSampleDict = stitched_DL_V2
#theSampleDict = stitched_SL_V2

#Name the channel that's being analyzed for saving files, and the format (.C, .root, .pdf, .eps, .gif, .png, .jpeg, etc)
fileChannel = "StitchCalculation"
theFormat = ".pdf"

filtered = {}
for name, vals in theSampleDict.items():
    #if name == "tttt_orig": continue
    print("Booking - {}".format(name))
    if useSpark == True:
        filtered[name] = RDF("Events", vals["sourceSPARK"]).Filter("nGenJet > 0", "trivial")#.Cache()
    else: 
        filtered[name] = RDF("Events", vals["source"]).Filter("nGenJet > 0", "trivial")#.Filter(b[JMLOG], JMLOG)#.Cache()

samples = {}
counts = {}
histos = {}
the_df = {}
print("Starting loop for booking")
for name, vals in theSampleDict.items():
    print("Booking - {}".format(name))
    the_df[name] = filtered[name]
    the_df[name] = defineStitchVars(the_df[name], crossSection=vals["crossSection"], sumWeights=vals["sumWeights"], 
                                    lumi=lumi[vals["era"]], nEvents=vals["nEvents"], nEventsPositive=vals["nEventsPositive"], 
                                    nEventsNegative=vals["nEventsNegative"],)
    counts[name] = the_df[name].Count()
    histos[name] = fillStitchVars(the_df[name], weights=["wgt_SUMW", "wgt_NUMW"], Cache=None,
                                  HTBinWidth=50, desiredHTMin=200, desiredHTMax=800,
                                  era=vals["era"], channel=vals["stitch"]["channel"],
                                 )

print("Warning: if filtered[name] RDFs are not reset, then calling Define(*) on them will cause the error"\
      " with 'program state reset' due to multiple definitions for the same variable")
loopcounter = 0
start = time.clock()
substart = {}
subfinish = {}
for name, cnt in counts.items():
    print("Working...")
    substart[name] = time.clock()
    loopcounter += 1
    print("{} = {}".format(name, str(cnt.GetValue())))
    subfinish[name] = time.clock()
finish = time.clock()

print("Took {}s to process".format(finish - start))
for name, val in substart.items():
    print("Took {}s to process sample {}".format(subfinish[name] - substart[name], name))

c = ROOT.TCanvas("c", "", 800, 600)
c.cd()
histos["tt_DL-GF"]["wgt_SUMW"]["GenHTvnGenJet"].Draw("COLZ TEXT")
c.Draw()
c.SaveAs("PyRDFTest.pdf")
