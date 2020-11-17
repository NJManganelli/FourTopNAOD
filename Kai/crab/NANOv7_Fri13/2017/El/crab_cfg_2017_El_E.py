import os
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromCRIC

config = Configuration()

config.section_("General")
config.General.requestName = '2017_El_E'
config.General.transferOutputs = True
config.General.transferLogs = True
config.section_("JobType")
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.maxMemoryMB = 2000
config.JobType.maxJobRuntimeMin = 1315
config.JobType.numCores = 1
config.JobType.scriptExe = 'crab_script_2017_El_E.sh'
config.JobType.inputFiles = ['crab_script_2017_El_E.py', 
                             os.path.join(os.environ['CMSSW_BASE'],'src/PhysicsTools/NanoAODTools/scripts/haddnano.py'),
                         ]
config.JobType.outputFiles = ['hist.root']
config.JobType.sendPythonFolder  = True
config.section_("Data")
config.Data.inputDataset = '/SingleElectron/Run2017E-02Apr2020-v1/NANOAOD'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
if config.Data.splitting == 'FileBased':
    config.Data.unitsPerJob = 1
    # config.Data.totalUnits = $TOTAL_UNITS
# config.Data.userInputFiles = []

config.Data.outLFNDirBase = '/store/user/{user}/Fri13'.format(user=getUsernameFromCRIC())
config.Data.publication = True
config.Data.outputDatasetTag = 'Fri13'
config.section_("Site")
config.Site.storageSite = 'T2_CH_CERN'

