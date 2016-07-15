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
    propagatorName = cms.string("SteppingHelixPropagatorAny"),
    TrackAssociatorParameters = TrackAssociatorParameterBlock.TrackAssociatorParameters,
)

rpcPointFromTrackerMuons = cms.EDProducer("RPCPointFromTrackerMuonProducer",
    #vertex = cms.InputTag("offlinePrimaryVertices"),
    muons = cms.InputTag("muons"),
    minMuonPt = cms.double(25),
    maxMuonAbsEta = cms.double(2.4),
    #propagatorName = cms.string("SmartPropagatorAnyRKOpposite"),
    #propagatorName = cms.string("SmartPropagatorAny"),
    propagatorName = cms.string("SteppingHelixPropagatorAny"),
    #propagatorName = cms.string("SteppingHelixPropagatorAlong"),
    TrackAssociatorParameters = TrackAssociatorParameterBlock.TrackAssociatorParameters,
)

