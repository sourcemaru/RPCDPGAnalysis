from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.transferLogs    = False
config.General.transferOutputs = True
config.General.requestName = "RPCEfficiency"

config.section_("JobType")
config.JobType.pluginName  = 'Analysis'
config.JobType.psetName    = 'rpcPointFromMuons_cfg.py'

config.section_("Data")
config.Data.publication  = False
#################################################################
# ALLOWS NON VALID DATASETS
config.Data.allowNonValidInputDataset = True

config.section_("Site")
# Where the output files will be transmitted to
config.Site.storageSite = 'T2_CH_CERN'
config.Data.outLFNDirBase = '/store/user/jhgoh/RPCChamberEfficiency/20160715_1'

config.Data.inputDataset = '/SingleMuon/Run2016B-PromptReco-v2/AOD'
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 30
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-275783_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt'
