import FWCore.ParameterSet.Config as cms

rpcExt = cms.EDAnalyzer("MuonHitFromTrackerMuonAnalyzer",
    doHybrid = cms.untracked.bool(False),
    vertex = cms.InputTag("goodVertices"),
    rpcRecHits = cms.InputTag("rpcRecHits"),
    dtSegments = cms.InputTag("dt4DSegments"),
    cscSegments = cms.InputTag("cscSegments"),
    muons = cms.InputTag("probeTrackerMuons"),
    minMuonPt = cms.double(10),
    maxMuonAbsEta = cms.double(2.1),
    tpMass = cms.InputTag("probeTrackerMuons", "mass"),
    resonanceType = cms.string("Z"),
)

