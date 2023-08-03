import FWCore.ParameterSet.Config as cms

process = cms.Process("RPCAnalysis")

process.load('Configuration/StandardSequences/Services_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.GeometryDB_cff")
#process.load("Configuration.Geometry.GeometryIdeal2015Reco_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load("Geometry.MuonNumbering.muonNumberingInitialization_cfi")
#process.load("DQMServices.Components.MEtoEDMConverter_cfi")
#process.load("DQMServices.Core.DQM_cfg")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Configuration.StandardSequences.MagneticField_AutoFromDBCurrent_cff")
from Configuration.AlCa.autoCond_condDBv2 import autoCond
#process.GlobalTag.globaltag = autoCond['run2_mc']
process.GlobalTag.globaltag = autoCond['run2_data']

process.load("RPCDPGAnalysis.SegmentAndTrackOnRPC.standAloneMuonsNoRPC_cff")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True),
    allowUnscheduled = cms.untracked.bool(True),
)
process.MessageLogger.cerr.FwkReport.reportEvery = 50000
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())

process.dTandCSCSegmentsinTracks = cms.EDProducer("DTandCSCSegmentsinTracks",
    cscSegments = cms.untracked.InputTag("hltCscSegments"),
    dt4DSegments = cms.untracked.InputTag("hltDt4DSegments"),
    #cscSegments = cms.untracked.InputTag("cscSegments"),
    #dt4DSegments = cms.untracked.InputTag("dt4DSegments"),
    tracks = cms.untracked.InputTag("standAloneMuons","UpdatedAtVtx")
)

process.load("RecoLocalMuon.RPCRecHit.rpcPointProducer_cff")
process.rpcPointProducer.cscSegments = 'dTandCSCSegmentsinTracks:SelectedCscSegments'
process.rpcPointProducer.dt4DSegments = 'dTandCSCSegmentsinTracks:SelectedDtSegments'

process.normfilter = cms.EDFilter("HLTHighLevel",
    TriggerResultsTag = cms.InputTag("TriggerResults","","HLT"),
    HLTPaths = cms.vstring("AlCa_RPCMuonNormalisation*"),
    eventSetupPathsKey = cms.string(''),
    andOr = cms.bool(True),
    throw = cms.bool(True)
)

process.muonHitFromTrackerMuonAnalyzer = cms.EDAnalyzer("RPCPointAnalyzer",
    minMuonPt = cms.double(4),
    maxMuonAbsEta = cms.double(2.1),
    rpcRecHits = cms.InputTag("hltRpcRecHits"),
    refPoints = cms.VInputTag(
        cms.InputTag("rpcPointProducer:RPCDTExtrapolatedPoints"),
        cms.InputTag("rpcPointProducer:RPCCSCExtrapolatedPoints"),
    ),
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("hist.root"),
)

process.p = cms.Path(
    process.normfilter
  * process.standAloneMuonNoRPCSequence
  * process.dTandCSCSegmentsinTracks
  * process.rpcPointProducer * process.muonHitFromTrackerMuonAnalyzer
)

process.source.fileNames = [
    '/store/data/Run2016B/RPCMonitor/RAW/v2/000/273/730/00001/FEFB0DB1-1620-E611-8E22-02163E01460E.root'
]
#import FWCore.PythonUtilities.LumiList as LumiList
#process.source.lumisToProcess = LumiList.LumiList(
#    filename = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-277148_13TeV_PromptReco_Collisions16_JSON_MuonPhys.txt').getVLuminosityBlockRange()

