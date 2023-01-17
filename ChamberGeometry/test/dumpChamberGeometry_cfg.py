import FWCore.ParameterSet.Config as cms

process = cms.Process("RPCAnalysis")

process.load('Configuration/StandardSequences/Services_cff')
process.load('FWCore/MessageService/MessageLogger_cfi')
process.load("Configuration.StandardSequences.GeometryDB_cff")
#process.load("Configuration.Geometry.GeometryIdeal2015Reco_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.autoCond import autoCond
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
    'root://cms-xrd-global.cern.ch//store/data/Run2018D/SingleMuon/AOD/15Feb2022_UL2018-v1/40000/21126605-A74A-854D-AC1F-22A7D9F384E5.root',

]
