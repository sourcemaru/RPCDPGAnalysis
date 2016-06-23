#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/DTRecHit/interface/DTRecHit1DPair.h"
#include "DataFormats/DTRecHit/interface/DTRecHitCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCRecHit2D.h"
#include "DataFormats/CSCRecHit/interface/CSCRecHit2DCollection.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHit.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHitCollection.h"

//#include "FWCore/Framework/interface/ESHandle.h"
//#include "Geometry/Records/interface/MuonGeometryRecord.h"
//#include "Geometry/RPCGeometry/interface/RPCGeometry.h"
//#include "Geometry/RPCGeometry/interface/RPCGeomServ.h"

#include "TTree.h"
#include "TH1D.h"
#include "TH2D.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class DroppedRecHitProducer : public edm::stream::EDProducer<>
{
public:
  DroppedRecHitProducer(const edm::ParameterSet& pset);
  virtual ~DroppedRecHitProducer() {};
  void produce(edm::Event& event, const edm::EventSetup& eventSetup) override;

private:
  edm::EDGetTokenT<DTRecHitCollection> dtHitToken_, dtCosmicHitToken_;
  edm::EDGetTokenT<CSCRecHit2DCollection> cscHitToken_;
  edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_;
};

DroppedRecHitProducer::DroppedRecHitProducer(const edm::ParameterSet& pset)
{
  rpcHitToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcHits"));
  cscHitToken_ = consumes<CSCRecHit2DCollection>(pset.getParameter<edm::InputTag>("cscHits"));
  dtHitToken_ = consumes<DTRecHitCollection>(pset.getParameter<edm::InputTag>("dtHits"));
  dtCosmicHitToken_ = consumes<DTRecHitCollection>(pset.getParameter<edm::InputTag>("dtCosmicHits"));

  produces<DTRecHitCollection>();
  produces<DTRecHitCollection>("cosmic");
  produces<CSCRecHit2DCollection>();
  produces<RPCRecHitCollection>();
}

void DroppedRecHitProducer::produce(edm::Event& event, const edm::EventSetup& eventSetup)
{
  std::auto_ptr<DTRecHitCollection> out_dt(new DTRecHitCollection);
  std::auto_ptr<DTRecHitCollection> out_dtcosmic(new DTRecHitCollection);
  std::auto_ptr<CSCRecHit2DCollection> out_csc(new CSCRecHit2DCollection);
  std::auto_ptr<RPCRecHitCollection> out_rpc(new RPCRecHitCollection);

  edm::Handle<DTRecHitCollection> dtHitHandle;
  event.getByToken(dtHitToken_, dtHitHandle);
  edm::Handle<DTRecHitCollection> dtCosmicHitHandle;
  event.getByToken(dtCosmicHitToken_, dtCosmicHitHandle);
  edm::Handle<CSCRecHit2DCollection> cscHitHandle;
  event.getByToken(cscHitToken_, cscHitHandle);
  edm::Handle<RPCRecHitCollection> rpcHitHandle;
  event.getByToken(rpcHitToken_, rpcHitHandle);

  for ( auto dtLayerId : dtHitHandle->ids() ) {
    const auto& hits = dtHitHandle->get(dtLayerId);
    out_dt->put(dtLayerId, hits.first, hits.second);
  }
  for ( auto dtLayerId : dtCosmicHitHandle->ids() ) {
    const auto& hits = dtCosmicHitHandle->get(dtLayerId);
    out_dtcosmic->put(dtLayerId, hits.first, hits.second);
  }
  for ( auto cscId : cscHitHandle->ids() ) {
    const auto& hits = cscHitHandle->get(cscId);
    out_csc->put(cscId, hits.first, hits.second);
  }

  for ( auto rpcId : rpcHitHandle->ids() ) {
    const auto& hits = rpcHitHandle->get(rpcId);
    out_rpc->put(rpcId, hits.first, hits.second);
  }

  event.put(out_dt);
  event.put(out_dtcosmic, "cosmic");
  event.put(out_csc);
  event.put(out_rpc);
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(DroppedRecHitProducer);
