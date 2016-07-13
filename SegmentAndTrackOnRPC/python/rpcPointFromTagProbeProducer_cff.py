import FWCore.ParameterSet.Config as cms

from TrackingTools.TrackAssociator.default_cfi import *
from TrackingTools.TrackAssociator.DetIdAssociatorESProducer_cff import *
from TrackingTools.Configuration.TrackingTools_cff import *
from RecoMuon.TrackingTools.MuonServiceProxy_cff import *
from Configuration.StandardSequences.MagneticField_cff import *

rpcPointFromTagProbe = cms.EDProducer("RPCPointFromTagProbeProducer",
    vertex = cms.InputTag("offlinePrimaryVertices"),
    muons = cms.InputTag("muons"),
    tracks = cms.InputTag("generalTracks"),
    minMuonPt = cms.double(25),
    maxMuonAbsEta = cms.double(2.4),
    maxMuonRelIso = cms.double(0.15),
    minTrackPt = cms.double(20),
    maxTrackAbsEta = cms.double(1.9),
    minMass = cms.double(70),
    maxMass = cms.double(110),
    triggerObjects = cms.InputTag("hltTriggerSummaryAOD"),
    triggerResults = cms.InputTag("TriggerResults::HLT"),
    triggerPaths = cms.vstring("HLT_IsoMu22"),
    TrackAssociatorParameters = TrackAssociatorParameterBlock.TrackAssociatorParameters,
)

