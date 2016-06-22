import FWCore.ParameterSet.Config as cms

process = cms.Process("RERECO")

process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load("Configuration.StandardSequences.RawToDigi_cff")
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = autoCond['run2_mc']
#process.GlobalTag.globaltag = autoCond['run2_data']

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(False),
#    allowUnscheduled = cms.untracked.bool(True),
    allowUnscheduled = cms.untracked.bool(False),
)
process.MessageLogger.cerr.FwkReport.reportEvery = 50000

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/relval/CMSSW_8_0_10/RelValSingleMuPt100_UP15/GEN-SIM-DIGI-RAW-HLTDEBUG/80X_mcRun2_asymptotic_v14-v1/00000/42AC15DA-C528-E611-9790-0CC47A78A340.root',
        '/store/relval/CMSSW_8_0_10/RelValSingleMuPt100_UP15/GEN-SIM-DIGI-RAW-HLTDEBUG/80X_mcRun2_asymptotic_v14-v1/00000/C0C012CD-C528-E611-A193-0CC47A4D7606.root',
        #'/store/relval/CMSSW_8_0_10/RelValSingleMuPt100_UP15/GEN-SIM-RECO/80X_mcRun2_asymptotic_v14-v1/00000/0458C823-CF28-E611-ACDE-0025905B860E.root',
        #'/store/relval/CMSSW_8_0_10/RelValSingleMuPt100_UP15/GEN-SIM-RECO/80X_mcRun2_asymptotic_v14-v1/00000/AEF8DC28-CF28-E611-B744-0CC47A4D75F8.root',
    ),
    secondaryFileNames = cms.untracked.vstring(
    ),
    inputCommands = cms.untracked.vstring(
        'keep *',
        'drop *_dt1DRecHits_*_*',
        'drop *_csc2DRecHits_*_*',
        'drop *_dt4DSegments_*_*',
        'drop *_cscSegments_*_*',
    ),
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string("out.root"),
    outputCommands = cms.untracked.vstring("drop *", "keep *_*_*_RERECO"),
)

process.p = cms.Path(
    process.muonDTDigis + process.muonCSCDigis + process.muonRPCDigis
  * process.dt1DRecHits + process.csc2DRecHits
# * process.droppedRecHits
  * process.dt4DSegments * process.cscSegments
  #* process.localreco * process.globalreco
  #* process.muonshighlevelreco
)

process.outPath = cms.EndPath(process.out)
