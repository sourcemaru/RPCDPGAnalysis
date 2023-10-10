import FWCore.ParameterSet.Config as cms
from Configuration.AlCa.autoCond import autoCond

from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')
options.register(
    name='autoCond',
    default='run3_data',
    mytype=VarParsing.varType.string,
    info='a key of autoCond for global tag',
)
options.parseArguments()

process = cms.Process('RPCAnalysis')
process.load('Configuration.StandardSequences.Services_cff')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('RPCDPGAnalysis.ChamberGeometry.rpcGeometryDumper_cfi')

process.GlobalTag.globaltag = autoCond[options.autoCond]

process.source = cms.Source('PoolSource',
    fileNames = cms.untracked.vstring(options.inputFiles)
)
process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(1)
)
process.p = cms.Path(process.rpcGeometryDumper)
