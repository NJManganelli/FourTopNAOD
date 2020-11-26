import os
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromCRIC

config = Configuration()

config.section_("General")
config.General.requestName = '$REQUEST_NAME'
config.General.transferOutputs = True
config.General.transferLogs = True
config.section_("JobType")
config.JobType.allowUndistributedCMSSW = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'crab_PSet_$REQUEST_NAME.py'
config.JobType.maxMemoryMB = $MAX_MEMORY_MB
config.JobType.maxJobRuntimeMin = $MAX_JOB_RUNTIME_MIN
config.JobType.numCores = $NUM_CORES
config.JobType.scriptExe = 'crab_script_$REQUEST_NAME.sh'
config.JobType.inputFiles = ['crab_script_$REQUEST_NAME.py', 
                             os.path.join(os.environ['CMSSW_BASE'],'src/PhysicsTools/NanoAODTools/scripts/haddnano.py'),
                         ]
config.JobType.outputFiles = [] #['hist.root']
config.JobType.sendPythonFolder  = True
config.section_("Data")
config.Data.inputDataset = '$INPUT_DATASET'
config.Data.inputDBS = '$DBS'
config.Data.splitting = '$SPLITTING'
if config.Data.splitting == 'FileBased':
    config.Data.unitsPerJob = $UNITS_PER_JOB
    # config.Data.totalUnits = $TOTAL_UNITS
# config.Data.userInputFiles = []

# config.Data.outLFNDirBase = '/store/user/{user}/$TAG'.format(user=getUsernameFromCRIC())
config.Data.outLFNDirBase = '/store/group/fourtop/$TAG'
config.Data.publication = $PUBLICATION
config.Data.outputDatasetTag = '$TAG'
config.section_("Site")
config.Site.storageSite = '$STORAGE_SITE'

