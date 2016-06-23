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

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(1))
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
    ),
)
process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string("out.root"),
    outputCommands = cms.untracked.vstring(
        'drop *', 'keep *_muons_*_*',
    )
)
#from Configuration.EventContent.EventContent_cff import RECOSIMEventContent
#process.out.outputCommands += RECOSIMEventContent.outputCommands

## Define the DroppedRecHits producer module
process.droppedRecHits = cms.EDProducer("DroppedRecHitProducer",
    rpcHits = cms.InputTag("rpcRecHits"),
    dtHits = cms.InputTag("dt1DRecHits"),
    dtCosmicHits = cms.InputTag("dt1DCosmicRecHits"),
    cscHits = cms.InputTag("csc2DRecHits"),
)
## Change the input collections
process.dt4DSegments.recHits1DLabel = "droppedRecHits"
process.dt4DCosmicSegments.recHits1DLabel = "droppedRecHits:cosmic"
process.cscSegments.inputObjects = "droppedRecHits"
process.glbTrackQual.RefitterParameters.DTRecSegmentLabel = "droppedRecHits"
process.muonShowerInformation.ShowerInformationFillerParameters.DTRecSegmentLabel = "droppedRecHits"
process.tevMuons.RefitterParameters.DTRecSegmentLabel = "droppedRecHits"
process.glbTrackQual.RefitterParameters.CSCRecSegmentLabel = "droppedRecHits"
process.muonShowerInformation.ShowerInformationFillerParameters.CSCRecSegmentLabel = "droppedRecHits"
process.tevMuons.RefitterParameters.CSCRecSegmentLabel = "droppedRecHits"

## Reorder the sequence to run the droppedRecHits just after the 1D, 2D rechit reconstruction
## segments have to be built after the droppedRecHits
process.localreco.remove(process.dt1DCosmicRecHits)
process.localreco.remove(process.csc2DRecHits)
process.localreco.remove(process.rpcRecHits)
process.localreco.replace(process.dt1DRecHits, cms.Sequence(
                          process.dt1DRecHits + process.dt1DCosmicRecHits
                        + process.csc2DRecHits + process.rpcRecHits
                        + process.droppedRecHits))

process.p = cms.Path(
    process.RawToDigi
  * process.reconstruction
)

process.outPath = cms.EndPath(process.out)
