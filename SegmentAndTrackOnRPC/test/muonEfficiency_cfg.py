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

process.source.fileNames = [
    '/store/data/Run2016B/SingleMuon/AOD/PromptReco-v2/000/275/376/00000/FE9B738C-A839-E611-A098-02163E01472F.root',
]
import FWCore.PythonUtilities.LumiList as LumiList
process.source.lumisToProcess = LumiList.LumiList(filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-277933_13TeV_PromptReco_Collisions16_JSON_NoL1T_MuonPhys_v2.txt').getVLuminosityBlockRange()

process.goodVertices = cms.EDFilter("VertexSelector",
    src = cms.InputTag("offlinePrimaryVertices"),
    cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2"),
    filter = cms.bool(True),
)

process.efficiencySegment = cms.EDAnalyzer("MuonSegmentFromRPCMuonAnalyzer",
    doHistByRun = cms.untracked.bool(False),
    vertex = cms.InputTag("goodVertices"),
    rpcRecHits = cms.InputTag("rpcRecHits"),
    dtSegments = cms.InputTag("dt4DSegments"),
    cscSegments = cms.InputTag("cscSegments"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(20),
    maxMuonAbsEta = cms.double(2.5),
)

process.efficienyRPCHit = cms.EDAnalyzer("MuonHitFromTrackerMuonAnalyzer",
    doHistByRun = cms.untracked.bool(False),
    vertex = cms.InputTag("goodVertices"),
    rpcRecHits = cms.InputTag("rpcRecHits"),
    dtSegments = cms.InputTag("dt4DSegments"),
    cscSegments = cms.InputTag("cscSegments"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(20),
    maxMuonAbsEta = cms.double(2.5),
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("hist.root"),
)

process.p = cms.Path(process.efficiencySegment+process.efficienyRPCHit)

