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
#config.Site.storageSite = 'T2_CH_CERN'
config.Site.storageSite = 'T3_KR_KISTI'

config.Data.splitting = 'LumiBased'

## Something that can be changed frequently
import os
config.Data.inputDataset = "/SingleMuon/Run2017D-PromptReco-v1/AOD"
if 'DATASET' in os.environ:
    config.Data.inputDataset = os.environ['DATASET']

pd, sd = config.Data.inputDataset.split('/')[1:3]

config.Data.unitsPerJob = 100
if pd == 'RPCMonitor':
    config.Data.unitsPerJob = 10
    config.JobType.psetName    = 'analyzeRPCwithSegments_cfg.py'
elif pd == "SingleMuon":
    config.JobType.psetName    = 'analyzeRPCwithTnP_Z_cfg.py'
elif pd == "Charmonium":
    config.JobType.psetName    = 'analyzeRPCwithTnP_Jpsi_cfg.py'
elif pd == "MuOnia":
    config.JobType.psetName    = 'analyzeRPCwithTnP_Upsilon_cfg.py'

username = os.environ['USER']

config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-317080_13TeV_PromptReco_Collisions18_JSON_MuonPhys.txt'
#config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PromptReco/Cert_294927-302343_13TeV_PromptReco_Collisions17_JSON_MuonPhys.txt'
#config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_MuonPhys.txt'
#config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Reprocessing/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_MuonPhys.txt'

#submitdate = dt.now().strftime('%Y%m%d')+'_1'
submitdate = '20180612_1'
config.Data.outLFNDirBase = '/store/user/%s/RPCChamberEfficiency/%s' % (username, submitdate)
config.General.requestName = "RPCEfficiency_%s_%s" % (pd, sd)

#config.Data.lumiMask = 'notFinishedLumis.json'

