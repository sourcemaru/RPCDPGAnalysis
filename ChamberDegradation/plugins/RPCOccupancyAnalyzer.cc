#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/MuonReco/interface/MuonFwd.h"
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
#include "TRandom3.h"

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
  edm::EDGetTokenT<reco::MuonCollection> muonToken_;

  TH1D* hBxBarrel_, * hBxEndcapP_, * hBxEndcapM_;
  TH1D* hBxFromGlbMuBarrel_, * hBxFromGlbMuEndcapP_, * hBxFromGlbMuEndcapM_;

  std::map<int, TH2D*> hXYRPCBarrelByWheel_, hXYRPCEndcapByDisk_;
  std::map<int, TH2D*> hXYRPCDetBarrelByWheel_, hXYRPCDetEndcapByDisk_;
  std::map<int, TH2D*> hZPhiRPCBarrelByStationLayer_;
  std::map<int, TH2D*> hZPhiRPCDetBarrelByStationLayer_;

};

RPCOccupancyAnalyzer::RPCOccupancyAnalyzer(const edm::ParameterSet& pset)
{
  rpcHitToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"));
  muonToken_ = consumes<reco::MuonCollection>(pset.getParameter<edm::InputTag>("muons"));

  usesResource("TFileService");
  edm::Service<TFileService> fs;

  hBxBarrel_ = fs->make<TH1D>("hBxBarrel", "Barrel bx distr;Bunch crossing", 13, -6.5, 6.5);
  hBxEndcapP_ = fs->make<TH1D>("hBxEndcapP", "Endcap+ bx distr;Bunch crossing", 13, -6.5, 6.5);
  hBxEndcapM_ = fs->make<TH1D>("hBxEndcapM", "Endcap- bx distr;Bunch crossing", 13, -6.5, 6.5);

  hBxFromGlbMuBarrel_ = fs->make<TH1D>("hBxFromGlbMuBarrel", "Barrel bx distr from GlbMu;Bunch crossing", 13, -6.5, 6.5);
  hBxFromGlbMuEndcapP_ = fs->make<TH1D>("hBxFromGlbMuEndcapP", "Endcap+ bx distr from GlbMu;Bunch crossing", 13, -6.5, 6.5);
  hBxFromGlbMuEndcapM_ = fs->make<TH1D>("hBxFromGlbMuEndcapM", "Endcap- bx distr from GlbMu;Bunch crossing", 13, -6.5, 6.5);

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

  TRandom3 rnd;
  const int nPoint = 100000;
  for ( const RPCRoll* roll : rpcGeom->rolls() ) {
    const RPCDetId rpcId = roll->id();
    const double height = roll->surface().bounds().length();
    const double width = roll->surface().bounds().width();
    const double area = height*roll->surface().bounds().widthAtHalfLength();
    if ( rpcId.region() == 0 ) {
      const int wh = rpcId.ring();
      const int st = rpcId.station();
      const int la = rpcId.layer();
      const int stla = st*10+la;

      if ( !hXYRPCDetBarrelByWheel_[wh] ) {
        const string whStr = Form("Wheel_%d", wh);
        hXYRPCDetBarrelByWheel_[wh] = dir.make<TH2D>(("hXYRPCDet_"+whStr).c_str(), ("RPCDet in "+whStr+";X (cm);Y (cm)").c_str(),
                                                     1600, -800, 800, 1600, -800, 800);
      }
      if ( !hZPhiRPCDetBarrelByStationLayer_[stla] ) {
        hZPhiRPCDetBarrelByStationLayer_[stla] = dir.make<TH2D>(Form("hZPhiRPCDetBarrel_Station%d_Layer%d", st, la),
                                                                Form("RPCDet in Barrel station %d layer %d;Z (cm);#phi", st, la),
                                                                1400, -700, 700, 1000, -3.14159265, 3.14159265);
      }

      for ( int i=0; i<nPoint; ++i ) {
        const double x = rnd.Uniform(-width/2, width/2);
        const double y = rnd.Uniform(-height/2, height/2);
        const LocalPoint lp(x, y, 0);
        if ( !roll->surface().bounds().inside(lp) ) continue;
        const GlobalPoint gp = roll->toGlobal(lp);

        hXYRPCDetBarrelByWheel_[wh]->Fill(gp.x(), gp.y());
        hZPhiRPCDetBarrelByStationLayer_[stla]->Fill(gp.z(), gp.phi(), area/nPoint);
      }
    }
    else {
      const int di = rpcId.station()*rpcId.region();

      if ( !hXYRPCDetEndcapByDisk_[di] ) {
        const std::string diStr = Form("Disk_%d", di);
        hXYRPCDetEndcapByDisk_[di] = dir.make<TH2D>(("hXYDet_"+diStr).c_str(), ("RPCDet in"+diStr+";X (cm);Y (cm)").c_str(),
                                                    1600, -800, 800, 1600, -800, 800);
      }

      for ( int i=0; i<nPoint; ++i ) {
        const double x = rnd.Uniform(-width/2, width/2);
        const double y = rnd.Uniform(-height/2, height/2);
        const LocalPoint lp(x, y, 0);
        if ( !roll->surface().bounds().inside(lp) ) continue;
        const GlobalPoint gp = roll->toGlobal(lp);

        hXYRPCDetEndcapByDisk_[di]->Fill(gp.x(), gp.y(), area/nPoint);
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

  // Find RPC hits from muons
  edm::Handle<reco::MuonCollection> muonHandle;
  event.getByToken(muonToken_, muonHandle);
  for ( auto mu : *muonHandle ) {
    if ( !mu.isGlobalMuon() ) continue;
    const auto glbTrack = mu.globalTrack();
    for ( auto hit = glbTrack->recHitsBegin(); hit != glbTrack->recHitsEnd(); ++hit ) {
      auto rpcHit = dynamic_cast<const RPCRecHit*>(*hit);
      if ( !rpcHit ) continue;
      const int reg = rpcHit->rpcId().region();
      const int bx = rpcHit->BunchX();

      if      ( reg == 0 ) hBxFromGlbMuBarrel_->Fill(bx);
      else if ( reg > 0  ) hBxFromGlbMuEndcapP_->Fill(bx);
      else if ( reg < 0  ) hBxFromGlbMuEndcapM_->Fill(bx);
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCOccupancyAnalyzer);
