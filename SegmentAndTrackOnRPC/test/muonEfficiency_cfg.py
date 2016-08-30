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

process.segmentExt = cms.EDAnalyzer("MuonSegmentFromRPCMuonAnalyzer",
    doHistByRun = cms.untracked.bool(False),
    vertex = cms.InputTag("goodVertices"),
    dtSegments = cms.InputTag("dt4DSegments"),
    cscSegments = cms.InputTag("cscSegments"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(20),
    maxMuonAbsEta = cms.double(2.5),
)

process.rpcExt = cms.EDAnalyzer("MuonHitFromTrackerMuonAnalyzer",
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

process.probeMuons = cms.EDProducer("RPCTrackerMuonProbeProducer",
    vertex = cms.InputTag("offlinePrimaryVertices"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(25),
    maxMuonAbsEta = cms.double(2.4),
    maxMuonRelIso = cms.double(0.25), # Loose isolation ~98% eff. (tight=0.15)
    minTrackPt = cms.double(20),
    maxTrackAbsEta = cms.double(2.1),
    doCheckSign = cms.bool(True),
    minDR = cms.double(0.1),
    minMass = cms.double(70),
    maxMass = cms.double(110),
    triggerObjects = cms.InputTag("hltTriggerSummaryAOD"),
    triggerResults = cms.InputTag("TriggerResults::HLT"),
    triggerPaths = cms.vstring("HLT_IsoMu22", "HLT_IsoMu22_eta2p1", "HLT_IsoTkMu22", "HLT_Mu50", "HLT_TkMu50"),
)
process.segmentExt.muons = "probeMuons"
process.rpcExt.muons = "probeMuons"

process.p = cms.Path(
#    process.trigger
    process.segmentExt + process.rpcExt
)

process.source.fileNames = [
    #'/store/data/Run2016B/MET/AOD/01Jul2016-v1/20000/B0368187-794F-E611-9A86-02163E01156C.root',
    '/store/data/Run2016B/SingleMuon/AOD/PromptReco-v2/000/273/450/00000/040B6B30-241C-E611-9ADB-02163E011907.root',
]
import FWCore.PythonUtilities.LumiList as LumiList
process.source.lumisToProcess = LumiList.LumiList(
    filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-279116_13TeV_PromptReco_Collisions16_JSON_NoL1T_MuonPhys.txt').getVLuminosityBlockRange()

