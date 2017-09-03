from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.transferLogs    = False
config.General.transferOutputs = True

config.section_("JobType")
config.JobType.pluginName  = 'Analysis'

config.section_("Data")
config.Data.publication  = False
#################################################################
# ALLOWS NON VALID DATASETS
config.Data.allowNonValidInputDataset = True

config.section_("Site")
# Where the output files will be transmitted to
config.Site.storageSite = 'T2_CH_CERN'

config.Data.splitting = 'LumiBased'

## Something that can be changed frequently
import os
if 'DATASET' not in os.environ:
    config.Data.inputDataset = "/SingleMuon/Run2017D-PromptReco-v1/AOD"
else:
    config.Data.inputDataset = os.environ['DATASET']
datasetSafeName = config.Data.inputDataset.replace('/', '_')
pd, sd, tier = config.Data.inputDataset.split('/')

if pd == 'RPCMonitor':
    config.Data.unitsPerJob = 10
    config.JobType.psetName    = 'analyzeRPCwithSegments_cfg.py'
else:
    config.Data.unitsPerJob = 40
    config.JobType.psetName    = 'analyzeRPCwithTnP_cfg.py'

username = os.environ['USER']

from datetime import datetime as dt
submitdate = dt.now().strftime('%Y%m%d')

#config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-279116_13TeV_PromptReco_Collisions16_JSON_NoL1T_MuonPhys.txt'
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-277148_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt'
#config.Data.lumiMask = 'notFinishedLumis.json'
config.Data.outLFNDirBase = '/store/user/%s/RPCChamberEfficiency/%s_1' % (username, submitdate)
config.General.requestName = "RPCEfficiency_%s" % (datasetSafeName)

