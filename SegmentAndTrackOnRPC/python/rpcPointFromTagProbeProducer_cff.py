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
    minTrackPt = cms.double(10),
    maxTrackAbsEta = cms.double(2.1),
    doCheckSign = cms.bool(True),
    minDR = cms.double(0.1),
    minMass = cms.double(70),
    maxMass = cms.double(110),
    triggerObjects = cms.InputTag("hltTriggerSummaryAOD"),
    triggerResults = cms.InputTag("TriggerResults::HLT"),
    triggerPaths = cms.vstring(
        "HLT_Mu50",
        "HLT_IsoMu18", ## 2015C-D 25ns, 76X MC
        "HLT_IsoMu20", ## 2015B-C 50ns, 74X MC
        "HLT_IsoMu22", "HLT_IsoMuTk22", ## Do we need these paths?
        "HLT_IsoMu24", "HLT_IsoTkMu24", "HLT_IsoMu22_eta2p1", "HLT_IsoTkMu22_eta2p1", ## 2016B-H 25ns 80X MC
    ),
)

rpcPointFromTrackerMuons = cms.EDProducer("RPCPointFromTrackerMuonProducer",
    #vertex = cms.InputTag("offlinePrimaryVertices"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(20),
    maxMuonAbsEta = cms.double(2.1),
)

rpcPointFromTrackerMuonsTriggerVeto = rpcPointFromTagProbe.clone(
    doCheckSign = cms.bool(False),
    minDR = cms.double(0.3),
    minMass = cms.double(1),
    maxMass = cms.double(1e9),
    maxMuonRelIso = cms.double(1e9), ## Ignore isolation cut
)
