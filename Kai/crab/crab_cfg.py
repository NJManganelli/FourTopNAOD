from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB

config = Configuration()

config.section_("General")
config.General.requestName = 'NanoGenTop_TTTT'
config.General.transferLogs=True
config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script.sh'
config.JobType.inputFiles = ['crab_script.py', '../../../PhysicsTools/NanoAODTools/scripts/haddnano.py'] #hadd nano will not be needed once nano tools are in cmssw
config.JobType.sendPythonFolder	 = True
config.section_("Data")
#config.Data.inputDataset = '/DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM'
#config.Data.inputDataset = '/DoubleMuon/Run2017B-Nano14Dec2018-v1/NANOAOD'
#config.Data.inputDataset = '/DoubleEG/Run2017B-Nano14Dec2018-v1/NANOAOD'
#config.Data.inputDataset = '/MuonEG/Run2017B-Nano14Dec2018-v1/NANOAOD'
#config.Data.inputDataset = '/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_new_pmx_102X_mc2017_realistic_v6-v1/NANOAODSIM'
config.Data.inputDataset = '/TTTT_TuneCP5_PSweights_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM'
#config.Data.inputDataset = '/TTTT_TuneCP5_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM'
#config.Data.inputDataset = '/TT_DiLept_TuneCP5_13TeV-amcatnlo-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM'
#config.Data.inputDataset = '/TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8/RunIIFall17NanoAODv4-PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/NANOAODSIM'
#config.Data.inputDataset = ''
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
#opt1
#config.Data.splitting = 'Automatic'
#opt 2
#config.Data.splitting = 'EventAwareLumiBased'
#opt 3
config.Data.splitting = 'FileBased'
#config.Data.unitsPerJob = 4
#config.Data.totalUnits = 150

config.Data.outLFNDirBase = '/store/user/%s/NanoGenTop_TTTT' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.outputDatasetTag = 'NanoGenTop_TTTT'
config.section_("Site")
#config.Site.storageSite = "T2_DE_DESY"
config.Site.storageSite = "T2_CH_CERN"
#config.section_("User")
#config.User.voGroup = 'dcms'

