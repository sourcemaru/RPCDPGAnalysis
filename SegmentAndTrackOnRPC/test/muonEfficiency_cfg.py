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

process.efficiencySegment = cms.EDAnalyzer("MuonSegmentFromRPCMuonAnalyzer",
    doHistByRun = cms.untracked.bool(False),
    vertex = cms.InputTag("goodVertices"),
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
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(20),
    maxMuonAbsEta = cms.double(2.5),
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("hist.root"),
)

process.trigger = cms.EDFilter("HLTHighLevel",
    TriggerResultsTag = cms.InputTag("TriggerResults::HLT"),
    andOr = cms.bool(True),
    throw = cms.bool(False),
    HLTPaths = cms.vstring(
        "HLT_PFMET120_PFMHT120_IDTight_v*",
        "HLT_PFMET170_JetIdCleaned_v*",
        "HLT_PFMET170_HBHECleaned_v*",
        "HLT_PFHT350_PFMET100_v*",
        "HLT_PFHT800_v*",
        "HLT_MET250_v*",
        "HLT_PFHT750_4JetPt50_v*",
    ),
)

process.p = cms.Path(
    process.trigger
  * process.efficiencySegment+process.efficienyRPCHit
)

process.source.fileNames = [
    '/store/data/Run2016B/MET/AOD/01Jul2016-v1/20000/B0368187-794F-E611-9A86-02163E01156C.root',
]
import FWCore.PythonUtilities.LumiList as LumiList
process.source.lumisToProcess = LumiList.LumiList(
    filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-279116_13TeV_PromptReco_Collisions16_JSON_NoL1T_MuonPhys.txt').getVLuminosityBlockRange()

