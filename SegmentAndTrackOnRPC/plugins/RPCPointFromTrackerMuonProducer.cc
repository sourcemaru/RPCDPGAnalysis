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

  std::auto_ptr<RPCRecHitCollection> out_points(new RPCRecHitCollection);

  edm::Handle<reco::MuonCollection> muonHandle;
  event.getByToken(muonToken_, muonHandle);

  std::map<RPCDetId, edm::OwnVector<RPCRecHit>> pointMap;
  for ( int i=0, n=muonHandle->size(); i<n; ++i ) {
    const auto& mu = muonHandle->at(i);
    const double pt = mu.pt();

    // Basic cuts
    if ( pt < minMuonPt_ or std::abs(mu.eta()) > maxMuonAbsEta_ ) continue;
    if ( !mu.isTrackerMuon() ) continue;
    if ( !muon::isGoodMuon(mu, muon::TMOneStationLoose) ) continue;

    for ( auto ch : mu.matches() ) {
      if ( ch.detector() != 3 ) continue;
      //auto rpcMatch = muMatch.rpcMatches;

      const LocalError lErr(ch.xErr, ch.yErr, 0);
      const LocalPoint lPos(ch.x, ch.y, 0);

      auto pointItr = pointMap.find(ch.id);
      if ( pointItr == pointMap.end() ) pointItr = pointMap.insert(std::make_pair(ch.id, edm::OwnVector<RPCRecHit>())).first;
      pointItr->second.push_back(RPCRecHit(ch.id, 0, lPos, lErr));
    }
  }

  for ( auto itr = pointMap.begin(); itr != pointMap.end(); ++itr ) {
    auto id = itr->first;
    auto pointVector = itr->second;
    out_points->put(id, pointVector.begin(), pointVector.end());
  }
  event.put(out_points);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCPointFromTrackerMuonProducer);

