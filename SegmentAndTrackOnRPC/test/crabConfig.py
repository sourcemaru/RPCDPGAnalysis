from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.transferLogs    = False
config.General.transferOutputs = True

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

config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 20

## Something that can be changed frequently
dataset = "Run2016B"
#dataset = "Run2016C"
#dataset = "Run2016D"
#dataset = "Run2016E"
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-276811_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt'
config.Data.outLFNDirBase = '/store/user/jhgoh/RPCChamberEfficiency/20160802_2'
config.General.requestName = "RPCEfficiency_%s" % dataset
config.Data.inputDataset = '/SingleMuon/%s-PromptReco-v2/AOD' % dataset
