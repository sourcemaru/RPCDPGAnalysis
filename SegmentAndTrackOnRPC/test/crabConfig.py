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
config.Data.inputDataset = "/SingleMuon/Run2016B-23Sep2016-v3/AOD"
if 'DATASET' in os.environ:
    config.Data.inputDataset = os.environ['DATASET']

pd, sd = config.Data.inputDataset.split('/')[1:3]

if pd == 'RPCMonitor':
    config.Data.unitsPerJob = 50
    config.JobType.psetName    = 'analyzeRPCwithSegments_cfg.py'
else:
    config.Data.unitsPerJob = 200
    config.JobType.psetName    = 'analyzeRPCwithTnP_cfg.py'

username = os.environ['USER']

config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_MuonPhys.txt'
#config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Reprocessing/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_MuonPhys.txt'
submitdate = '20170303_1'
config.Data.outLFNDirBase = '/store/user/%s/RPCChamberEfficiency/%s' % (username, submitdate)
config.General.requestName = "RPCEfficiency_%s_%s" % (pd, sd)

#config.Data.unitsPerJob = 1
#config.Data.lumiMask = 'resub/crab_%s/results/notFinishedLumis.json' % config.General.requestName

