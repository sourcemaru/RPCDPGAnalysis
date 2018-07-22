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

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(1) )
process.options = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(True),
    allowUnscheduled = cms.untracked.bool(True),
)
process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())

process.dumpRPCGeom = cms.EDAnalyzer("RPCGeometryDumper",
    outFileName = cms.untracked.string("rpcChambers.txt"),
)

process.p = cms.Path(process.dumpRPCGeom)

process.source.fileNames = [
    #'/store/data/Run2016H/SingleMuon/AOD/07Aug17-v1/50001/16496FB9-9080-E711-BAB1-001E675799D0.root',
    #'/store/data/Run2017C/SingleMuon/AOD/PromptReco-v2/000/300/122/00000/005F1A9F-4077-E711-BEA4-02163E0135A0.root',
    'root://cms-xrd-global.cern.ch//store/data/Run2018A/SingleMuon/AOD/PromptReco-v2/000/316/505/00000/9C8A29DC-3C5C-E811-841C-FA163E626FD1.root',

]
