import FWCore.ParameterSet.Config as cms

#from TrackingTools.TrackAssociator.default_cfi import *
#from TrackingTools.TrackAssociator.DetIdAssociatorESProducer_cff import *
#from TrackingTools.Configuration.TrackingTools_cff import *
#from RecoMuon.TrackingTools.MuonServiceProxy_cff import *
#from Configuration.StandardSequences.MagneticField_cff import *

rpcPointFromTagProbe = cms.EDProducer("RPCPointFromTagProbeProducer",
    vertex = cms.InputTag("offlinePrimaryVertices"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(25),
    maxMuonAbsEta = cms.double(2.4),
    maxMuonRelIso = cms.double(0.25), # Loose isolation ~98% eff. (tight=0.15)
    minTrackPt = cms.double(20),
    maxTrackAbsEta = cms.double(2.1),
    minMass = cms.double(70),
    maxMass = cms.double(110),
    triggerObjects = cms.InputTag("hltTriggerSummaryAOD"),
    triggerResults = cms.InputTag("TriggerResults::HLT"),
    triggerPaths = cms.vstring("HLT_IsoMu22", "HLT_IsoMu22_eta2p1", "HLT_IsoTkMu22", "HLT_Mu50", "HLT_TkMu50"),
)

rpcPointFromTrackerMuons = cms.EDProducer("RPCPointFromTrackerMuonProducer",
    #vertex = cms.InputTag("offlinePrimaryVertices"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(20),
    maxMuonAbsEta = cms.double(2.1),
)

