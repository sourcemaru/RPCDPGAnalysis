#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "DataFormats/DTRecHit/interface/DTRecSegment4DCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonFwd.h"
#include "DataFormats/MuonReco/interface/MuonSelectors.h"

#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"

#include "DataFormats/RPCRecHit/interface/RPCRecHit.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHitCollection.h"
#include "DataFormats/MuonDetId/interface/RPCDetId.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"
#include "Geometry/RPCGeometry/interface/RPCGeometry.h"

#include "TrackingTools/TrackAssociator/interface/TrackDetectorAssociator.h"
#include "TrackingTools/Records/interface/TrackingComponentsRecord.h"

#include <vector>
#include <string>
#include <memory>
#include <cmath>

class RPCPointFromTrackerMuonProducer : public edm::stream::EDProducer<>
{
public:
  RPCPointFromTrackerMuonProducer(const edm::ParameterSet& pset);
  void produce(edm::Event& event, const edm::EventSetup&) override;

private:
  const edm::EDGetTokenT<reco::MuonCollection> muonToken_;

  const double minMuonPt_, maxMuonAbsEta_;
};

RPCPointFromTrackerMuonProducer::RPCPointFromTrackerMuonProducer(const edm::ParameterSet& pset):
  muonToken_(consumes<reco::MuonCollection>(pset.getParameter<edm::InputTag>("muons"))),
  minMuonPt_(pset.getParameter<double>("minMuonPt")),
  maxMuonAbsEta_(pset.getParameter<double>("maxMuonAbsEta"))
{
  produces<RPCRecHitCollection>();
}

void RPCPointFromTrackerMuonProducer::produce(edm::Event& event, const edm::EventSetup& eventSetup)
{
  using namespace std;

  std::unique_ptr<RPCRecHitCollection> out_points(new RPCRecHitCollection);

  edm::Handle<reco::MuonCollection> muonHandle;
  event.getByToken(muonToken_, muonHandle);

  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  std::map<RPCDetId, edm::OwnVector<RPCRecHit>> pointMap;
  for ( int i=0, n=muonHandle->size(); i<n; ++i ) {
    const auto& mu = muonHandle->at(i);
    const double pt = mu.pt();

    // Basic cuts
    if ( pt < minMuonPt_ or std::abs(mu.eta()) > maxMuonAbsEta_ ) continue;
    if ( !mu.isTrackerMuon() ) continue;
    if ( !muon::isGoodMuon(mu, muon::TMOneStationLoose) ) continue;
    if ( mu.track()->originalAlgo() == reco::TrackBase::muonSeededStepOutIn ) continue; // To avoid bias from muon seeded one

    for ( auto match : mu.matches() ) {
      if ( match.detector() != 3 ) continue;
      //auto rpcMatch = muMatch.rpcMatches;

      const LocalError lErr(match.xErr, match.yErr, 0);
      const LocalPoint lPos(match.x, match.y, 0);

      const RPCRoll* roll = rpcGeom->roll(match.id);
      if ( !roll->surface().bounds().inside(lPos) ) continue;
      //const RPCChamber* chamber = rpcGeom->chamber(match.id);
      //if ( !chamber->surface().bounds().inside(chamber->toLocal(roll->toGlobal(lPos))) ) continue;

      auto pointItr = pointMap.find(match.id);
      if ( pointItr == pointMap.end() ) pointItr = pointMap.insert(std::make_pair(match.id, edm::OwnVector<RPCRecHit>())).first;
      pointItr->second.push_back(RPCRecHit(match.id, 0, lPos, lErr));
      pointItr->second.back().setTimeAndError(mu.time().timeAtIpInOut, mu.time().timeAtIpInOutErr);
    }
  }

  for ( auto itr = pointMap.begin(); itr != pointMap.end(); ++itr ) {
    auto id = itr->first;
    auto pointVector = itr->second;
    out_points->put(id, pointVector.begin(), pointVector.end());
  }
  event.put(std::move(out_points));
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCPointFromTrackerMuonProducer);

