import FWCore.ParameterSet.Config as cms

def customise_DropMuonHits(process):
    ## Define the DroppedRecHits producer module
    process.droppedRecHits = cms.EDProducer("DroppedRecHitProducer",
        rpcHits = cms.InputTag("rpcRecHits"),
        dtHits = cms.InputTag("dt1DRecHits"),
        dtCosmicHits = cms.InputTag("dt1DCosmicRecHits"),
        cscHits = cms.InputTag("csc2DRecHits"),
    )
    ## Change the input collections
    process.dt4DSegments.recHits1DLabel = "droppedRecHits"
    process.dt4DCosmicSegments.recHits1DLabel = "droppedRecHits:cosmic"
    process.cscSegments.inputObjects = "droppedRecHits"
    process.glbTrackQual.RefitterParameters.DTRecSegmentLabel = "droppedRecHits"
    process.muonShowerInformation.ShowerInformationFillerParameters.DTRecSegmentLabel = "droppedRecHits"
    process.tevMuons.RefitterParameters.DTRecSegmentLabel = "droppedRecHits"
    process.glbTrackQual.RefitterParameters.CSCRecSegmentLabel = "droppedRecHits"
    process.muonShowerInformation.ShowerInformationFillerParameters.CSCRecSegmentLabel = "droppedRecHits"
    process.tevMuons.RefitterParameters.CSCRecSegmentLabel = "droppedRecHits"

    ## Reorder the sequence to run the droppedRecHits just after the 1D, 2D rechit reconstruction
    ## segments have to be built after the droppedRecHits
    process.localreco.remove(process.dt1DCosmicRecHits)
    process.localreco.remove(process.csc2DRecHits)
    process.localreco.remove(process.rpcRecHits)
    process.localreco.replace(process.dt1DRecHits, cms.Sequence(
                              process.dt1DRecHits + process.dt1DCosmicRecHits
                            + process.csc2DRecHits + process.rpcRecHits
                            + process.droppedRecHits))

    return process
