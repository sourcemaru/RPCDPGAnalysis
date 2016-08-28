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

process.load("RPCDPGAnalysis.SegmentAndTrackOnRPC.rpcPointFromTagProbeProducer_cff")

process.load("RecoLocalMuon.RPCRecHit.rpcPointProducer_cff")
process.rpcPointProducer.dt4DSegments = "dt4DSegments"
process.rpcPointProducer.cscSegments = "cscSegments"

process.rpcPoint = cms.EDAnalyzer("RPCPointAnalyzer",
    doTree = cms.untracked.bool(False),
    doHist = cms.untracked.bool(True),
    doHistByRun = cms.untracked.bool(False),
    doChamberMuography = cms.untracked.bool(False),
    vertex = cms.InputTag("goodVertices"),
    rpcRecHits = cms.InputTag("rpcRecHits"),
    refPoints = cms.VInputTag(
        cms.InputTag("rpcPointProducer:RPCDTExtrapolatedPoints"),
        cms.InputTag("rpcPointProducer:RPCCSCExtrapolatedPoints"),
    ),
)
process.tmPoint = process.rpcPoint.clone(refPoints = cms.VInputTag(cms.InputTag("rpcPointFromTrackerMuons")))

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("hist.root"),
)

process.p = cms.Path(process.rpcPoint+process.tmPoint)

process.source.fileNames = [
    '/store/express/Run2016F/ExpressPhysics/FEVT/Express-v1/000/278/167/0047E384-225A-E611-B0ED-FA163E8359E6.root',
]
import FWCore.PythonUtilities.LumiList as LumiList
process.source.lumisToProcess = LumiList.LumiList(
    filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-279116_13TeV_PromptReco_Collisions16_JSON_NoL1T_MuonPhys.txt').getVLuminosityBlockRange()

