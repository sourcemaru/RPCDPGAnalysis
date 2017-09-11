/** \class DTandCSCSegmentsinTracks
 *
 *  Producer which take as input a muon track and return two containers 
 *  with the DTSegments and CSCSegments (respectively) used to fit it
 *
 *  $Date: 2012/02/15 14:19:57 $
 *  
 *  \author Juan Pablo Gomez - Uniandes
 */
#include <vector>

//standard include
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrackingRecHit/interface/TransientTrackingRecHit.h"
#include "TrackingTools/PatternTools/interface/TrajectoryMeasurement.h" 
#include "TrackingTools/DetLayers/interface/DetLayer.h"
#include "TrackingTools/PatternTools/interface/TrajMeasLessEstim.h"
#include "RecoMuon/TrackingTools/interface/MuonPatternRecoDumper.h"
#include "RecoMuon/TransientTrackingRecHit/interface/MuonTransientTrackingRecHit.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/TrackReco/interface/Track.h"
///

#include "DataFormats/TrajectorySeed/interface/TrajectorySeedCollection.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackingRecHit/interface/TrackingRecHit.h"
#include "DataFormats/MuonDetId/interface/MuonSubdetId.h"
#include "DataFormats/GeometryVector/interface/LocalPoint.h"
#include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/Common/interface/getRef.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/DTRecHit/interface/DTRecSegment4D.h"
#include "DataFormats/TrackingRecHit/interface/RecSegment.h"

#include "DataFormats/DTRecHit/interface/DTRecSegment4DCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHitCollection.h"
#include "DataFormats/DTRecHit/interface/DTRecHitCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCRecHit2DCollection.h"

#include "MagneticField/Engine/interface/MagneticField.h"
#include "MagneticField/Records/interface/IdealMagneticFieldRecord.h"
#include "Geometry/Records/interface/GlobalTrackingGeometryRecord.h"
#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"
#include "Geometry/CommonDetUnit/interface/GeomDet.h"

#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
//#include<fstream>

#include "DataFormats/DTRecHit/interface/DTRecSegment4DCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"

#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include <vector>
#include <memory>
#include <ctime>

class DTandCSCSegmentsinTracks : public edm::stream::EDProducer<>
{
public:
  DTandCSCSegmentsinTracks(const edm::ParameterSet& pset);
  ~DTandCSCSegmentsinTracks() = default;
  void produce(edm::Event&, const edm::EventSetup&) override;

private:

  edm::EDGetTokenT<DTRecSegment4DCollection> dt4DSegments;
  edm::EDGetTokenT<CSCSegmentCollection> cscSegments;
  edm::EDGetTokenT<reco::TrackCollection> tracks;

};

DTandCSCSegmentsinTracks::DTandCSCSegmentsinTracks(const edm::ParameterSet& iConfig)
{
  dt4DSegments = consumes<DTRecSegment4DCollection>(iConfig.getUntrackedParameter < edm::InputTag > ("dt4DSegments"));
  cscSegments = consumes<CSCSegmentCollection>(iConfig.getUntrackedParameter < edm::InputTag > ("cscSegments"));
  tracks = consumes<reco::TrackCollection>(iConfig.getUntrackedParameter < edm::InputTag > ("tracks"));

  produces<DTRecSegment4DCollection>("SelectedDtSegments");
  produces<CSCSegmentCollection>("SelectedCscSegments");  
}

void DTandCSCSegmentsinTracks::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  edm::ESHandle<GlobalTrackingGeometry> theTrackingGeometry;
  iSetup.get<GlobalTrackingGeometryRecord>().get(theTrackingGeometry);

  edm::Handle<DTRecSegment4DCollection> all4DSegments;
  iEvent.getByToken(dt4DSegments, all4DSegments); 

  edm::Handle<CSCSegmentCollection> allCSCSegments;
  iEvent.getByToken(cscSegments, allCSCSegments);

  edm::Handle<reco::TrackCollection> alltracks;
  iEvent.getByToken(tracks,alltracks);

  auto selectedDtSegments = std::make_unique<DTRecSegment4DCollection>();
  auto selectedCscSegments = std::make_unique<CSCSegmentCollection>();

  std::vector<CSCDetId> chamberIdCSC;
  std::vector<DTLayerId> chamberIdDT;

  for  ( auto Track=alltracks->begin(); Track!=alltracks->end();   Track++) {
    for( auto recHit = Track->recHitsBegin(); recHit != Track->recHitsEnd(); ++recHit) {
      const GeomDet* geomDet = theTrackingGeometry->idToDet( (*recHit)->geographicalId() );

      if( geomDet->subDetector() == GeomDetEnumerators::DT ) {
        edm::OwnVector<DTRecSegment4D> DTSegmentsVector;
        //Take the layer associated to this hit                                                                                                                                         
        DTLayerId myLayer( (*recHit)->geographicalId().rawId() );
        DTRecSegment4DCollection::range  range = all4DSegments->get(myLayer);

        // Loop over the 4Dsegments of this *ChamberId=myLayer
        int counter=0;  
        for ( auto segmentDT = range.first; segmentDT!=range.second; ++segmentDT) {
          counter++;      
        }

        //if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId
        if (counter==1){
          //By default the chamber associated to the segment is new  
          bool isNewChamber = true;
          //Loop over DTChambers already used 
          for( std::vector<DTLayerId>::iterator chamberIdDTIt = chamberIdDT.begin(); chamberIdDTIt != chamberIdDT.end(); chamberIdDTIt++ )
          {
            //If this chamber has been used before isNewChamber = false
            if( myLayer.wheel() == (*chamberIdDTIt).wheel() &&  myLayer.station() == (*chamberIdDTIt).station() && myLayer.sector() == (*chamberIdDTIt).sector() ) 
            {
              isNewChamber = false;
            }
          }//Loop over DTChambers already used
          if (isNewChamber)
          {
            chamberIdDT.push_back(myLayer);
            DTSegmentsVector.push_back(*(range.first));
            selectedDtSegments->put(myLayer, DTSegmentsVector.begin(), DTSegmentsVector.end());
          }
        }//if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId

      }//It's a DTHit                                                                                                                                                                   
      //It's a CSCHit
      if( geomDet->subDetector() == GeomDetEnumerators::CSC ) {
        edm::OwnVector<CSCSegment> CSCSegmentsVector;
        //Take the layer associated to this hit                                                                                                                                         
        CSCDetId myLayer( (*recHit)->geographicalId().rawId() );
        CSCSegmentCollection::range  range = allCSCSegments->get(myLayer);
        // Loop over the CSCsegments of this *ChamberId=myLayer
        int counter=0;  
        for ( auto segmentCSC = range.first; segmentCSC!=range.second; ++segmentCSC) 
        {
          counter++;      
        }//Loop over the CSCsegments of this *ChamberId=myLayer
        //if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId
        if (counter==1){
          //By default the chamber associated to the segment is new  
          bool isNewChamber = true;
          //Loop over CSCChambers already used 
          for( std::vector<CSCDetId>::iterator chamberIdCSCIt = chamberIdCSC.begin(); chamberIdCSCIt != chamberIdCSC.end(); chamberIdCSCIt++ )
          {
            //If this chamber has been used before isNewChamber = false
            if( myLayer.chamberId() == (*chamberIdCSCIt).chamberId() ) 
            {
              isNewChamber = false;
            }
          }//Loop over CSCChambers already used
          if (isNewChamber)
          {
            //std::cout<<"paso8a"<<std::endl;
            chamberIdCSC.push_back(myLayer);
            CSCSegmentsVector.push_back(*(range.first));
            selectedCscSegments->put(myLayer, CSCSegmentsVector.begin(), CSCSegmentsVector.end());
          }
        }//if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId

      }//It's a CSCHit
    }//Loop over the trackingRecHits

  }//loop over alltracks
  iEvent.put(std::move(selectedCscSegments),"SelectedCscSegments");
  iEvent.put(std::move(selectedDtSegments),"SelectedDtSegments");
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(DTandCSCSegmentsinTracks);

