import FWCore.ParameterSet.Config as cms

process = cms.Process("RPCAnalysis")

process.load('Configuration/StandardSequences/Services_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load("Configuration.StandardSequences.GeometryDB_cff")
#process.load("Configuration.Geometry.GeometryIdeal2015Reco_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
from Configuration.AlCa.autoCond_condDBv2 import autoCond
#process.GlobalTag.globaltag = autoCond['run2_mc']
process.GlobalTag.globaltag = autoCond['run2_data']

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True),
    allowUnscheduled = cms.untracked.bool(True),
)
process.MessageLogger.cerr.FwkReport.reportEvery = 50000
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())

process.goodVertices = cms.EDFilter("VertexSelector",
    src = cms.InputTag("offlinePrimaryVertices"),
    cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2"),
    filter = cms.bool(True),
)

process.probeTrackerMuons = cms.EDFilter("MuonSelector",
    src = cms.InputTag("muons"),
    cut = cms.string("pt > 10 && abs(eta) < 2.1 && isTrackerMuon"),
)

process.load("RPCDPGAnalysis.SegmentAndTrackOnRPC.muonHitFromTrackerMuonAnalyzer_cfi")
process.muonHitFromTrackerMuonAnalyzer.resonanceType = "Inclusive"

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("hist.root"),
)

process.p = cms.Path(process.goodVertices+process.probeTrackerMuons+process.muonHitFromTrackerMuonAnalyzer)

process.source.fileNames = [
#    'root://cms-xrd-global.cern.ch//store/data/Run2018A/SingleMuon/AOD/PromptReco-v2/000/316/505/00000/9C8A29DC-3C5C-E811-841C-FA163E626FD1.root',
    'file:/xrootd/store/user/heewon/RPCChamberEfficiency/METGoodMuonSets.root',
]
