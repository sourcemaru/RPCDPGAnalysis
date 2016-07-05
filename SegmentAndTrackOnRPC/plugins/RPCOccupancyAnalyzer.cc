#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHit.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHitCollection.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"
#include "Geometry/RPCGeometry/interface/RPCGeometry.h"
#include "RPCDPGAnalysis/SegmentAndTrackOnRPC/interface/RPCPointData.h"
#include "Geometry/RPCGeometry/interface/RPCGeomServ.h"
#include "DataFormats/GeometrySurface/interface/TrapezoidalPlaneBounds.h"

#include "TTree.h"
#include "TH1D.h"
#include "TH2D.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class RPCOccupancyAnalyzer : public edm::one::EDAnalyzer<edm::one::WatchRuns, edm::one::SharedResources>
{
public:
  RPCOccupancyAnalyzer(const edm::ParameterSet& pset);
  virtual ~RPCOccupancyAnalyzer() {};
  void beginRun(const edm::Run& run, const edm::EventSetup& eventSetup) override;
  void endRun(const edm::Run&, const edm::EventSetup&) override {};
  void analyze(const edm::Event& event, const edm::EventSetup& eventSetup) override;

private:
  edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_;

  TH1D* hBxBarrel_, * hBxEndcapP_, * hBxEndcapM_;

  std::map<int, TH2D*> hXYRPCBarrelByWheel_, hXYRPCEndcapByDisk_;
  std::map<int, TH2D*> hZPhiRPCBarrelByStationLayer_;
};

RPCOccupancyAnalyzer::RPCOccupancyAnalyzer(const edm::ParameterSet& pset)
{
  rpcHitToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"));

  usesResource("TFileService");
  edm::Service<TFileService> fs;

  hBxBarrel_ = fs->make<TH1D>("hBxBarrel", "Barrel bx distr;Bunch crossing", 13, -6.5, 6.5);
  hBxEndcapP_ = fs->make<TH1D>("hBxEndcapP", "Endcap+ bx distr;Bunch crossing", 13, -6.5, 6.5);
  hBxEndcapM_ = fs->make<TH1D>("hBxEndcapM", "Endcap- bx distr;Bunch crossing", 13, -6.5, 6.5);
}

void RPCOccupancyAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  usesResource("TFileService");
  edm::Service<TFileService> fs;

  auto dir = fs->mkdir(Form("Run%06d", run.id().run()));

  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  for ( const RPCChamber* ch : rpcGeom->chambers() ) {
    const RPCDetId rpcId = ch->id();
    //const std::string chName = RPCGeomServ(rpcId).chambername();
    //const double height = ch->surface().bounds().length();
    //const double width = ch->surface().bounds().width();
    if ( rpcId.region() == 0 ) {
      const int wh = rpcId.ring();
      const int st = rpcId.station();
      const int la = rpcId.layer();

      const string whStr = Form("Wheel_%d", wh);
      if ( !hXYRPCBarrelByWheel_[wh] ) {
        hXYRPCBarrelByWheel_[wh] = dir.make<TH2D>(("hXYRPC_"+whStr).c_str(), ("RPC in "+whStr+";X (cm);Y (cm)").c_str(),
                                                  1600, -800, 800, 1600, -800, 800);
      }

      const int stla = st*10+la;
      if ( !hZPhiRPCBarrelByStationLayer_[stla] ) {
        hZPhiRPCBarrelByStationLayer_[stla] = dir.make<TH2D>(Form("hZPhiRPCBarrel_Station%d_Layer%d", st, la),
                                                             Form("RPC in Barrel station %d layer %d;Z (cm);#phi", st, la),
                                                             1400, -700, 700, 1000, -3.14159265, 3.14159265);
      }
    }
    else {
      const int di = rpcId.region()*rpcId.station();

      const std::string diStr = Form("Disk_%d", di);
      if ( !hXYRPCEndcapByDisk_[di] ) {
        hXYRPCEndcapByDisk_[di] = dir.make<TH2D>(("hXY_"+diStr).c_str(), ("RPC in"+diStr+";X (cm);Y (cm)").c_str(),
                                                 1600, -800, 800, 1600, -800, 800);
      }
    }
  }
}

void RPCOccupancyAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  // Find matching RPC hits
  edm::Handle<RPCRecHitCollection> rpcHitHandle;
  event.getByToken(rpcHitToken_, rpcHitHandle);
  for ( auto rpcItr = rpcHitHandle->begin(); rpcItr != rpcHitHandle->end(); ++rpcItr ) {
    const auto rpcId = rpcItr->rpcId();
    if ( !rpcGeom->roll(rpcId) or !rpcGeom->chamber(rpcId) ) continue;

    const int reg = rpcId.region();
    const int bx = rpcItr->BunchX();
    const auto rpcGp = rpcGeom->roll(rpcId)->toGlobal(rpcItr->localPosition());

    if ( reg == 0 ) {
      const int wheel = rpcId.ring();
      const int station = rpcId.station();
      const int layer = rpcId.layer();
      const int stla = station*10+layer;

      hBxBarrel_->Fill(bx);
      hXYRPCBarrelByWheel_[wheel]->Fill(rpcGp.x(), rpcGp.y());
      hZPhiRPCBarrelByStationLayer_[stla]->Fill(rpcGp.z(), rpcGp.phi());
    }
    else {
      const int disk = reg*rpcId.station();
      if ( reg > 0 ) hBxEndcapP_->Fill(bx);
      else           hBxEndcapM_->Fill(bx);

      hXYRPCEndcapByDisk_[disk]->Fill(rpcGp.x(), rpcGp.y());
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCOccupancyAnalyzer);
