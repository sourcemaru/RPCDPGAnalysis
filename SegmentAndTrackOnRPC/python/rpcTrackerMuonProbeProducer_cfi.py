import FWCore.ParameterSet.Config as cms

probeTrackerMuons = cms.EDProducer("RPCTrackerMuonProbeProducer",
    vertex = cms.InputTag("goodVertices"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(25),
    maxMuonAbsEta = cms.double(2.4),
    maxMuonRelIso = cms.double(0.25), # Loose isolation ~98% eff. (tight=0.15)
    minTrackPt = cms.double(10),
    maxTrackAbsEta = cms.double(2.1),
    doCheckSign = cms.bool(True),
    minDR = cms.double(0.1),
    minMass = cms.double(70),
    maxMass = cms.double(110),
    triggerObjects = cms.InputTag("hltTriggerSummaryAOD"),
    triggerResults = cms.InputTag("TriggerResults::HLT"),
    triggerPaths = cms.vstring(""),
    triggerModules = cms.vstring(""), ## Make it to be a pair with the trigger path if given
    probeIdType = cms.string("Tracker"),
    tagIdType = cms.string("Tight"),
)

