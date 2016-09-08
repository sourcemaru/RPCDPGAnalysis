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
if 'ERA' not in os.environ: era = "Run2016B"
else: era = os.environ['ERA']
if 'DATASET' not in os.environ: dataset = "SingleMuon"
else: dataset = os.environ['DATASET']

if era[:-1] == "Run2016" and era[-1] in "BCDE": datasetVer = 'v2'
else: datasetVer = 'v1'

if dataset == 'RPCMonitor':
    config.Data.unitsPerJob = 10
    config.JobType.psetName    = 'analyzeRPCwithSegments_cfg.py'
    config.Data.inputDataset = "/%s/%s-%s/RAW" % (dataset, era, datasetVer)
else:
    config.Data.unitsPerJob = 40
    config.JobType.psetName    = 'analyzeRPCwithTnP_cfg.py'
    config.Data.inputDataset = "/%s/%s-PromptReco-%s/AOD" % (dataset, era, datasetVer)

username = os.environ['USER']

from datetime import datetime as dt
submitdate = dt.now().strftime('%Y%m%d')

#config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-279116_13TeV_PromptReco_Collisions16_JSON_NoL1T_MuonPhys.txt'
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-277148_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt'
#config.Data.lumiMask = 'notFinishedLumis.json'
config.Data.outLFNDirBase = '/store/user/%s/RPCChamberEfficiency/%s_1' % (username, submitdate)
config.General.requestName = "RPCEfficiency_%s_%s" % (dataset, era)

