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

process.probeTrackerMuons = cms.EDProducer("RPCTrackerMuonProbeProducer",
    vertex = cms.InputTag("goodVertices"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(8),
    maxMuonAbsEta = cms.double(2.4),
    maxMuonRelIso = cms.double(999.), # No isolation cut
    minTrackPt = cms.double(4),
    maxTrackAbsEta = cms.double(2.1),
    doCheckSign = cms.bool(True),
    minDR = cms.double(0.1),
    minMass = cms.double(8.5),
    maxMass = cms.double(11.5),
    triggerObjects = cms.InputTag("hltTriggerSummaryAOD"),
    triggerResults = cms.InputTag("TriggerResults::HLT"),
    triggerPaths = cms.vstring("HLT_Mu7p5_Track3p5_Upsilon"),
    triggerModules = cms.vstring("hltL3fLMu7p5TrackL3Filtered7p5"), ## Make it to be a pair with the trigger path if given
    probeIdType = cms.string("Tracker"),
)

process.rpcExt = cms.EDAnalyzer("MuonHitFromTrackerMuonAnalyzer",
    doHistByRun = cms.untracked.bool(True),
    vertex = cms.InputTag("goodVertices"),
    rpcRecHits = cms.InputTag("rpcRecHits"),
    muons = cms.InputTag("probeTrackerMuons"),
    minMuonPt = cms.double(4),
    maxMuonAbsEta = cms.double(2.1),
    tpMass = cms.InputTag("probeTrackerMuons", "mass"),
    resonanceType = cms.string("Upsilon"),
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("hist.root"),
)

process.p = cms.Path(process.goodVertices+process.probeTrackerMuons+process.rpcExt)

process.source.fileNames = [
    '/store/data/Run2018A/MuOnia/AOD/PromptReco-v3/000/316/615/00000/B2A93043-B964-E811-B741-FA163E3240B9.root',
]
import FWCore.PythonUtilities.LumiList as LumiList
process.source.lumisToProcess = LumiList.LumiList(
    #filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Final/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt').getVLuminosityBlockRange()
    #filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/PromptReco/Cert_294927-301567_13TeV_PromptReco_Collisions17_JSON.txt').getVLuminosityBlockRange()
    filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/PromptReco/Cert_314472-317080_13TeV_PromptReco_Collisions18_JSON_MuonPhys.txt').getVLuminosityBlockRange()
