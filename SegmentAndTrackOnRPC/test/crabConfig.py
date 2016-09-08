from WMCore.Configuration import Configuration
config = Configuration()

config.section_("General")
config.General.transferLogs    = False
config.General.transferOutputs = True

config.section_("JobType")
config.JobType.pluginName  = 'Analysis'
config.JobType.psetName    = 'analyzeRPCwithTnP_cfg.py'
#config.JobType.psetName    = 'analyzeRPCwithSegments_cfg.py'

config.section_("Data")
config.Data.publication  = False
#################################################################
# ALLOWS NON VALID DATASETS
config.Data.allowNonValidInputDataset = True

config.section_("Site")
# Where the output files will be transmitted to
config.Site.storageSite = 'T2_CH_CERN'

config.Data.splitting = 'LumiBased'
#config.Data.unitsPerJob = 1
config.Data.unitsPerJob = 20

## Something that can be changed frequently
import os
if 'DATASET' in os.environ: dataset = os.environ['DATASET']
else: dataset = "Run2016B"

primDSet = "SingleMuon"
#primDSet = "JetHT"
if dataset[:-1] == "Run2016":
    if dataset[-1] in "BCDE":
        config.Data.inputDataset = '/%s/%s-PromptReco-v2/AOD' % (primDSet, dataset)
    else:
        config.Data.inputDataset = '/%s/%s-PromptReco-v1/AOD' % (primDSet, dataset)

username = os.environ['USER']

from datetime import datetime as dt
submitdate = dt.now().strftime('%Y%m%d')

#config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-279116_13TeV_PromptReco_Collisions16_JSON_NoL1T_MuonPhys.txt'
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-277148_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt'
#config.Data.lumiMask = 'notFinishedLumis.json'
config.Data.outLFNDirBase = '/store/user/%s/RPCChamberEfficiency/%s_1' % (username, submitdate)
config.General.requestName = "RPCEfficiency_%s" % dataset

