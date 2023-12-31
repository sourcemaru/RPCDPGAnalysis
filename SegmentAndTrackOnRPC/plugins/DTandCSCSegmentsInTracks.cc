/** \class DTandCSCSegmentsinTracks
 *
 *  Producer which take as input a muon track and return two containers
 *  with the DTSegments and CSCSegments (respectively) used to fit it
 *
 *  $Date: 2012/02/15 14:19:57 $
 *
 *  \author Juan Pablo Gomez - Uniandes
 */

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "DataFormats/DTRecHit/interface/DTRecSegment4DCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHitCollection.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "Geometry/Records/interface/GlobalTrackingGeometryRecord.h"
#include "Geometry/CommonDetUnit/interface/GlobalTrackingGeometry.h"

#include <vector>

class DTandCSCSegmentsinTracks : public edm::stream::EDProducer<>
{
public:
  DTandCSCSegmentsinTracks(const edm::ParameterSet& pset);
  ~DTandCSCSegmentsinTracks() = default;
  void produce(edm::Event&, const edm::EventSetup&) override;

private:
  edm::EDGetTokenT<DTRecSegment4DCollection> dt4DSegmentsToken;
  edm::EDGetTokenT<CSCSegmentCollection> cscSegmentsToken;
  edm::EDGetTokenT<reco::TrackCollection> tracksToken;

  edm::ESGetToken<GlobalTrackingGeometry, MuonGeometryRecord> trackingGeomToken_;

};

DTandCSCSegmentsinTracks::DTandCSCSegmentsinTracks(const edm::ParameterSet& iConfig)
{
  dt4DSegmentsToken = consumes<DTRecSegment4DCollection>(iConfig.getUntrackedParameter<edm::InputTag>("dt4DSegments"));
  cscSegmentsToken = consumes<CSCSegmentCollection>(iConfig.getUntrackedParameter<edm::InputTag>("cscSegments"));
  tracksToken = consumes<reco::TrackCollection>(iConfig.getUntrackedParameter<edm::InputTag>("tracks"));

  trackingGeomToken_ = esConsumes<edm::Transition::BeginRun>();

  produces<DTRecSegment4DCollection>("SelectedDtSegments");
  produces<CSCSegmentCollection>("SelectedCscSegments");
}

void DTandCSCSegmentsinTracks::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  const auto& trackingGeom = iSetup.getData(trackingGeomToken_);

  edm::Handle<DTRecSegment4DCollection> dt4DSegmentsHandle;
  iEvent.getByToken(dt4DSegmentsToken, dt4DSegmentsHandle);

  edm::Handle<CSCSegmentCollection> cscSegmentsHandle;
  iEvent.getByToken(cscSegmentsToken, cscSegmentsHandle);

  edm::Handle<reco::TrackCollection> tracksHandle;
  iEvent.getByToken(tracksToken,tracksHandle);

  auto selectedDtSegments = std::make_unique<DTRecSegment4DCollection>();
  auto selectedCscSegments = std::make_unique<CSCSegmentCollection>();

  std::vector<DTLayerId> chamberIdsDT;
  std::vector<CSCDetId> chamberIdsCSC;

  for ( auto track : *tracksHandle ) {
    for( auto recHit = track.recHitsBegin(); recHit != track.recHitsEnd(); ++recHit) {
      const GeomDet* geomDet = trackingGeom.idToDet( (*recHit)->geographicalId() );

      if( geomDet->subDetector() == GeomDetEnumerators::DT ) {
        //Take the layer associated to this hit
        DTLayerId myLayer( (*recHit)->geographicalId().rawId() );
        DTRecSegment4DCollection::range  range = dt4DSegmentsHandle->get(myLayer);

        const int nSegment = range.second-range.first;
        if ( nSegment != 1 ) continue;

        bool isNewChamber = true;
        for( auto chamberIdDT : chamberIdsDT ) {
          if( myLayer.wheel() == chamberIdDT.wheel() && myLayer.station() == chamberIdDT.station() && myLayer.sector() == chamberIdDT.sector() ) {
            isNewChamber = false;
            break;
          }
        }
        if ( !isNewChamber ) continue;

        chamberIdsDT.emplace_back(myLayer);
        edm::OwnVector<DTRecSegment4D> dtSegmentsVector;
        dtSegmentsVector.push_back(*(range.first));
        selectedDtSegments->put(myLayer, dtSegmentsVector.begin(), dtSegmentsVector.end());
      }
      else if ( geomDet->subDetector() == GeomDetEnumerators::CSC ) {
        //Take the layer associated to this hit
        CSCDetId myLayer( (*recHit)->geographicalId().rawId() );
        CSCSegmentCollection::range  range = cscSegmentsHandle->get(myLayer);
        const int nSegments = range.second-range.first;
        if ( nSegments != 1 ) continue;

        bool isNewChamber = true;
        for( auto chamberIdCSC : chamberIdsCSC ) {
          if( myLayer.chamberId() == chamberIdCSC.chamberId() ) {
            isNewChamber = false;
            break;
          }
        }
        if ( !isNewChamber ) continue;

        chamberIdsCSC.emplace_back(myLayer);
        edm::OwnVector<CSCSegment> cscSegmentsVector;
        cscSegmentsVector.push_back(*(range.first));
        selectedCscSegments->put(myLayer, cscSegmentsVector.begin(), cscSegmentsVector.end());
      }
    }
  }

  iEvent.put(std::move(selectedCscSegments),"SelectedCscSegments");
  iEvent.put(std::move(selectedDtSegments),"SelectedDtSegments");
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(DTandCSCSegmentsinTracks);

