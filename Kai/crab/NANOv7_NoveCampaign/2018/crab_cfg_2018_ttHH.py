import os
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromCRIC

config = Configuration()

config.section_("General")
config.General.requestName = '2018_ttHH'
config.General.transferOutputs = True
config.General.transferLogs = True
config.section_("JobType")
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'crab_PSet_2018_ttHH.py'
config.JobType.maxMemoryMB = 3000
config.JobType.maxJobRuntimeMin = 1315
config.JobType.numCores = 1
config.JobType.scriptExe = 'crab_script_2018_ttHH.sh'
config.JobType.inputFiles = ['crab_script_2018_ttHH.py', 
                             os.path.join(os.environ['CMSSW_BASE'],'src/PhysicsTools/NanoAODTools/scripts/haddnano.py'),
                         ]
config.JobType.outputFiles = [] #['hist.root']
config.JobType.sendPythonFolder  = True
config.section_("Data")
config.Data.inputDataset = '/TTHH_TuneCP5_13TeV-madgraph-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_102X_upgrade2018_realistic_v21_ext1-v1/NANOAODSIM'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
if config.Data.splitting == 'FileBased':
    config.Data.unitsPerJob = 1
    # config.Data.totalUnits = $TOTAL_UNITS
# config.Data.userInputFiles = []

# config.Data.outLFNDirBase = '/store/user/{user}/NoveCampaign'.format(user=getUsernameFromCRIC())
config.Data.outLFNDirBase = '/store/group/fourtop/NoveCampaign'
config.Data.publication = True
config.Data.outputDatasetTag = 'NoveCampaign'
config.section_("Site")
config.Site.storageSite = 'T2_BE_IIHE'

