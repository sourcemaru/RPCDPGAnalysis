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
#include "FWCore/Framework/interface/MakerMacros.h"
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

#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EDProducer.h"
//#include<fstream>

#include "DataFormats/DTRecHit/interface/DTRecSegment4DCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"

#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"


class DTandCSCSegmentsinTracks : public edm::EDProducer {
   public:
//      explicit DTandCSCSegmentsinTracks(const edm::ParameterSet&);
      DTandCSCSegmentsinTracks(edm::ParameterSet const&);
      ~DTandCSCSegmentsinTracks();

   private:
//      edm::InputTag cscSegments;
//      edm::InputTag dt4DSegments;
//      edm::InputTag tracks;
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      // ----------member data ---------------------------

      edm::EDGetTokenT<DTRecSegment4DCollection> dt4DSegments;
      edm::EDGetTokenT<CSCSegmentCollection> cscSegments;
      edm::EDGetTokenT<reco::TrackCollection> tracks;

};

// -*- C++ -*-
//
// Class:      DTandCSCSegmentsinTracks
// 
/**\class DTandCSCSegmentsinTracks DTandCSCSegmentsinTracks.cc RecoLocalMuon/RPCRecHit/src/DTandCSCSegmentsinTracks.cc
   
Description: [one line class summary]

Implementation:
[Notes on implementation]
*/
//
// Original Author:  Juan Pablo Gomez Cardona,42 R-023,+41227662349,
//         Created:  Thu Jan  19 13:03:28 CEST 2012
// $Id: DTandCSCSegmentsinTracks.cc,v 1.1.1.1 2012/07/17 01:17:51 jgomezca Exp $
//
//
#include "FWCore/Framework/interface/MakerMacros.h"
#include "DTandCSCSegmentsinTracks/DTandCSCSegmentsinTracks/interface/DTandCSCSegmentsinTracks.h"
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

#include <vector>


using namespace std;

#include <memory>
#include <ctime>

#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Utilities/interface/EDGetToken.h"

DTandCSCSegmentsinTracks::DTandCSCSegmentsinTracks(const edm::ParameterSet& iConfig)
{
//  cscSegments=iConfig.getParameter<edm::InputTag>("cscSegments");
//  dt4DSegments=iConfig.getParameter<edm::InputTag>("dt4DSegments");
//  tracks=iConfig.getParameter<edm::InputTag>("tracks");

  dt4DSegments = consumes<DTRecSegment4DCollection>(iConfig.getUntrackedParameter < edm::InputTag > ("dt4DSegments"));
  cscSegments = consumes<CSCSegmentCollection>(iConfig.getUntrackedParameter < edm::InputTag > ("cscSegments"));
  tracks = consumes<reco::TrackCollection>(iConfig.getUntrackedParameter < edm::InputTag > ("tracks"));

  produces<DTRecSegment4DCollection>("SelectedDtSegments");
  produces<CSCSegmentCollection>("SelectedCscSegments");  
}


DTandCSCSegmentsinTracks::~DTandCSCSegmentsinTracks(){
  
}

void DTandCSCSegmentsinTracks::produce(edm::Event& iEvent, const edm::EventSetup& iSetup){
  
  edm::ESHandle<GlobalTrackingGeometry> theTrackingGeometry;
  iSetup.get<GlobalTrackingGeometryRecord>().get(theTrackingGeometry);
  
  edm::Handle<DTRecSegment4DCollection> all4DSegments;
  iEvent.getByToken(dt4DSegments, all4DSegments); 
  
  edm::Handle<CSCSegmentCollection> allCSCSegments;
  iEvent.getByToken(cscSegments, allCSCSegments);
  
  edm::Handle<reco::TrackCollection> alltracks;
  iEvent.getByToken(tracks,alltracks);
  
  reco::TrackCollection::const_iterator Track;
  DTRecSegment4DCollection::const_iterator segmentDT;
  CSCSegmentCollection::const_iterator segmentCSC;
  DTRecSegment4D segmentDTToStore;
  CSCSegment segmentCSCToStore;

  auto selectedDtSegments = std::make_unique<DTRecSegment4DCollection>();
  auto selectedCscSegments = std::make_unique<CSCSegmentCollection>();
  
//  std::auto_ptr<DTRecSegment4DCollection> selectedDtSegments(new DTRecSegment4DCollection());
//  std::auto_ptr<CSCSegmentCollection> selectedCscSegments(new CSCSegmentCollection());

  std::vector<CSCDetId> chamberIdCSC;
  std::vector<DTLayerId> chamberIdDT;
  
 
  //std::cout<<"paso1"<<std::endl;
  //loop over alltracks 
  for  (Track=alltracks->begin(); Track!=alltracks->end();   Track++)
    {
      //std::cout<<"paso2"<<std::endl;
      //Loop over the trackingRecHits 
      for(trackingRecHit_iterator recHit = Track->recHitsBegin(); recHit != Track->recHitsEnd(); ++recHit)
  {
    const GeomDet* geomDet = theTrackingGeometry->idToDet( (*recHit)->geographicalId() );
    //std::cout<<"paso3"<<std::endl;
    //It's a DTHit                                                                                                                                                                      
    if( geomDet->subDetector() == GeomDetEnumerators::DT )
      {
        edm::OwnVector<DTRecSegment4D> DTSegmentsVector;
              //Take the layer associated to this hit                                                                                                                                         
        DTLayerId myLayer( (*recHit)->geographicalId().rawId() );
        DTRecSegment4DCollection::range  range = all4DSegments->get(myLayer);
        //std::cout<<"paso4"<<std::endl;
        // Loop over the 4Dsegments of this *ChamberId=myLayer
        int counter=0;  
        for (segmentDT = range.first; segmentDT!=range.second; ++segmentDT) 
    {
      counter++;      
    }//Loop over the 4Dsegments of this *ChamberId=myLayer
        //if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId
        if (counter==1){
    //std::cout<<"paso5"<<std::endl;
    //By default the chamber associated to the segment is new  
    bool isNewChamber = true;
    //Loop over DTChambers already used 
    for( std::vector<DTLayerId>::iterator chamberIdDTIt = chamberIdDT.begin(); chamberIdDTIt != chamberIdDT.end(); chamberIdDTIt++ )
      {
        //std::cout<<"paso6"<<std::endl;
        //If this chamber has been used before isNewChamber = false
        if( myLayer.wheel() == (*chamberIdDTIt).wheel() &&  myLayer.station() == (*chamberIdDTIt).station() && myLayer.sector() == (*chamberIdDTIt).sector() ) 
          {
      //std::cout<<"paso7"<<std::endl;
      isNewChamber = false;
          }
      }//Loop over DTChambers already used
    if (isNewChamber)
      {
        //std::cout<<"paso8"<<std::endl;
        chamberIdDT.push_back(myLayer);
        DTSegmentsVector.push_back(*(range.first));
        selectedDtSegments->put(myLayer, DTSegmentsVector.begin(), DTSegmentsVector.end());
      }
    //std::cout<<"paso9"<<std::endl;
              }//if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId
        
      }//It's a DTHit                                                                                                                                                                   
    
    //std::cout<<"paso3a"<<std::endl;
          //It's a CSCHit                                                                                                                                                                     
    if( geomDet->subDetector() == GeomDetEnumerators::CSC )
      {
        edm::OwnVector<CSCSegment> CSCSegmentsVector;
              //Take the layer associated to this hit                                                                                                                                         
        CSCDetId myLayer( (*recHit)->geographicalId().rawId() );
        CSCSegmentCollection::range  range = allCSCSegments->get(myLayer);
        //std::cout<<"paso4a"<<std::endl;
        // Loop over the CSCsegments of this *ChamberId=myLayer
        int counter=0;  
        for (segmentCSC = range.first; segmentCSC!=range.second; ++segmentCSC) 
    {
      counter++;      
    }//Loop over the CSCsegments of this *ChamberId=myLayer
        //if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId
        if (counter==1){
    //std::cout<<"paso5a"<<std::endl;
    //By default the chamber associated to the segment is new  
    bool isNewChamber = true;
    //Loop over CSCChambers already used 
    for( std::vector<CSCDetId>::iterator chamberIdCSCIt = chamberIdCSC.begin(); chamberIdCSCIt != chamberIdCSC.end(); chamberIdCSCIt++ )
      {
        //std::cout<<"paso6a"<<std::endl;
        //If this chamber has been used before isNewChamber = false
        if( myLayer.chamberId() == (*chamberIdCSCIt).chamberId() ) 
          {
      //std::cout<<"paso7a"<<std::endl;
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
    //std::cout<<"paso9a"<<std::endl;
              }//if theres is only one segment and the chamber is new, the segment is stored as well as the ChamberId
        
      }//It's a CSCHit
  }//Loop over the trackingRecHits
      
    }//loop over alltracks
  iEvent.put(std::move(selectedCscSegments),"SelectedCscSegments");
  iEvent.put(std::move(selectedDtSegments),"SelectedDtSegments");
  //std::cout<<"paso10"<<std::endl;
}



// ------------ method called once each job just before starting event loop  ------------
void 
DTandCSCSegmentsinTracks::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
DTandCSCSegmentsinTracks::endJob() {
}

DEFINE_FWK_MODULE(DTandCSCSegmentsinTracks);

