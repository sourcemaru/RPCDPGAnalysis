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
config.Data.unitsPerJob = 40

## Something that can be changed frequently
import os
if 'DATASET' in os.environ: dataset = os.environ['DATASET']
else: dataset = "Run2016B"

username = os.environ['USER']

from datetime import datetime as dt
submitdate = dt.now().strftime('%Y%m%d')

config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-277148_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt'
config.Data.outLFNDirBase = '/store/user/%s/RPCChamberEfficiency/%s_1' % (username, submitdate)
config.General.requestName = "RPCEfficiency_%s" % dataset
config.Data.inputDataset = '/SingleMuon/%s-PromptReco-v2/AOD' % dataset
