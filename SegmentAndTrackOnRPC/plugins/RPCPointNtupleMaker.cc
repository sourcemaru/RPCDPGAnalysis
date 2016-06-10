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

#include "TTree.h"
#include "TH1D.h"
#include "TH2D.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class RPCPointNtupleMaker : public edm::one::EDAnalyzer<edm::one::WatchRuns, edm::one::SharedResources>
{
public:
  RPCPointNtupleMaker(const edm::ParameterSet& pset);
  virtual ~RPCPointNtupleMaker() {};
  void beginRun(const edm::Run& run, const edm::EventSetup& eventSetup) override;
  void endRun(const edm::Run&, const edm::EventSetup&) override {};
  void analyze(const edm::Event& event, const edm::EventSetup& eventSetup) override;

private:
  void fillHistograms(const std::map<RPCDetId, RPCBarrelData>& barrelDataMap,
                      const std::map<RPCDetId, RPCEndcapData>& endcapDataMap);

  edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_, dtPointToken_, cscPointToken_;
  edm::EDGetTokenT<reco::VertexCollection> vertexToken_;

  const bool doTree_, doHist_;

  // Trees and histograms
  TTree* tree_;
  unsigned char b_run, b_lumi;
  unsigned long long int b_event;
  unsigned char b_nPV;

  // Per-detector information
  std::unique_ptr<std::vector<RPCBarrelData> > b_barrelData_;
  std::unique_ptr<std::vector<RPCEndcapData> > b_endcapData_;

  TH2D* hXYExpBarrel_, * hXYExpEndcapP_, * hXYExpEndcapM_;
  TH2D* hXYRPCBarrel_, * hXYRPCEndcapP_, * hXYRPCEndcapM_;
  std::map<int, TH2D*> hXYExpBarrelByWheel_, hXYRPCBarrelByWheel_;
  std::map<int, TH2D*> hXYExpEndcapByDisk_, hXYRPCEndcapByDisk_;
  std::map<std::string, TH2D*> chToPoints_, chToRPCs_;
};

RPCPointNtupleMaker::RPCPointNtupleMaker(const edm::ParameterSet& pset):
  doTree_(pset.getUntrackedParameter<bool>("doTree")),
  doHist_(pset.getUntrackedParameter<bool>("doHist"))
{
  rpcHitToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"));
  dtPointToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("dtPoints"));
  cscPointToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("cscPoints"));
  vertexToken_ = consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"));

  b_barrelData_.reset(new std::vector<RPCBarrelData>());
  b_endcapData_.reset(new std::vector<RPCEndcapData>());

  usesResource("TFileService");
  edm::Service<TFileService> fs;
  if ( doTree_ ) {
    tree_ = fs->make<TTree>("tree", "tree");

    tree_->Branch("run", &b_run, "run/b"); // 8 bit unsigned integer
    tree_->Branch("lumi", &b_lumi, "lumi/b"); // 8 bit unsigned integer
    tree_->Branch("event", &b_event, "event/l"); // 64bit unsigned integer

    tree_->Branch("nPV", &b_nPV, "nPV/b");

    tree_->Branch("Barrel", "std::vector<RPCBarrelData>", &*b_barrelData_);
    tree_->Branch("Endcap", "std::vector<RPCEndcapData>", &*b_endcapData_);
  }
}

void RPCPointNtupleMaker::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  usesResource("TFileService");
  edm::Service<TFileService> fs;

  char buffer[100];
  snprintf(buffer, 99, "Run%06d", run.id().run());
  auto dir = fs->mkdir(buffer);

  auto dir_barrel = dir.mkdir("Barrel");
  hXYExpBarrel_  = dir_barrel.make<TH2D>("hXYExpBarrel" , "Expected points in Barrel;X (cm);Y (cm)" , 500, -1000, 1000, 500, -1000, 1000);
  hXYRPCBarrel_  = dir_barrel.make<TH2D>("hXYRPCBarrel" , "RPC in Barrel;X (cm);Y (cm)" , 500, -1000, 1000, 500, -1000, 1000);
  auto dir_endcapP = dir.mkdir("Endcap+");
  hXYExpEndcapP_ = dir_endcapP.make<TH2D>("hXYExpEndcap+", "Expected points in Endcap+;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);
  hXYRPCEndcapP_ = dir_endcapP.make<TH2D>("hXYRPCEndcap+", "RPC in Endcap+;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);
  auto dir_endcapM = dir.mkdir("Endcap-");
  hXYExpEndcapM_ = dir_endcapM.make<TH2D>("hXYExpEndcap-", "Expected points in Endcap-;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);
  hXYRPCEndcapM_ = dir_endcapM.make<TH2D>("hXYRPCEndcap-", "RPC in Endcap-;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);

  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  for ( const RPCChamber* ch : rpcGeom->chambers() ) {
    const RPCDetId rpcId = ch->id();
    const std::string chName = RPCGeomServ(rpcId).chambername();
    const double height = ch->specificSurface().bounds().length()+20;
    const double width = ch->specificSurface().bounds().width()+20;
    if ( rpcId.region() == 0 ) {
      const int wh = rpcId.ring();
      const int st = rpcId.station();
      const int se = rpcId.sector();

      snprintf(buffer, 12, "Wheel_%d", wh);
      auto dir_wheel = dir_barrel.mkdir(buffer);
      if ( !hXYExpBarrelByWheel_[wh] ) {
        hXYExpBarrelByWheel_[wh] = dir_wheel.make<TH2D>((string("hXYExp")+buffer).c_str(), (string("Expected points ")+buffer+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
        hXYRPCBarrelByWheel_[wh] = dir_wheel.make<TH2D>((string("hXYRPC")+buffer).c_str(), (string("RPC in ")+buffer+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
      }

      snprintf(buffer, 12, "sector_%d", se);
      auto dir_sector = dir_wheel.mkdir(buffer);

      snprintf(buffer, 12, "station_%d", st);
      auto dir_station = dir_sector.mkdir(buffer);

      chToPoints_[chName] = dir_station.make<TH2D>(("Expected_"+chName).c_str(), ("Expected points "+chName).c_str(), 100, -width/2, width/2, 100, -height/2, height/2);
      chToRPCs_[chName] = dir_station.make<TH2D>(("RPC_"+chName).c_str(), ("RPC "+chName).c_str(), 100, -width/2, width/2, 100, -height/2, height/2);
    }
    else if ( rpcId.region() == +1 ) {
      const int di = rpcId.station();
      const int rn = rpcId.ring();
      const int se = rpcId.sector();

      snprintf(buffer, 12, "Disk_%d", di);
      auto dir_disk = dir_endcapP.mkdir(buffer);
      if ( !hXYExpEndcapByDisk_[di] ) {
        hXYExpEndcapByDisk_[di] = dir_disk.make<TH2D>((string("hXYExp")+buffer).c_str(), (string("Expected points ")+buffer+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
        hXYRPCEndcapByDisk_[di] = dir_disk.make<TH2D>((string("hXYRPC")+buffer).c_str(), (string("RPC in ")+buffer+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
      }

      snprintf(buffer, 12, "ring_%d", rn);
      auto dir_ring = dir_disk.mkdir(buffer);

      snprintf(buffer, 12, "sector_%d", se);
      auto dir_sector = dir_ring.mkdir(buffer);

      chToPoints_[chName] = dir_sector.make<TH2D>(("Expected_"+chName).c_str(), ("Expected points "+chName).c_str(), 100, -width/2, width/2, 100, -height/2, height/2);
      chToRPCs_[chName] = dir_sector.make<TH2D>(("RPC_"+chName).c_str(), ("RPC "+chName).c_str(), 100, -width/2, width/2, 100, -height/2, height/2);
    }
    else if ( rpcId.region() == -1 ) {
      const int di = rpcId.region()*rpcId.station();
      const int rn = rpcId.ring();
      const int se = rpcId.sector();

      snprintf(buffer, 12, "Disk_%d", di);
      auto dir_disk = dir_endcapM.mkdir(buffer);
      if ( !hXYExpEndcapByDisk_[di] ) {
        hXYExpEndcapByDisk_[di] = dir_disk.make<TH2D>((string("hXYExp")+buffer).c_str(), (string("Expected points ")+buffer+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
        hXYRPCEndcapByDisk_[di] = dir_disk.make<TH2D>((string("hXYRPC")+buffer).c_str(), (string("RPC in ")+buffer+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
      }

      snprintf(buffer, 12, "ring_%d", rn);
      auto dir_ring = dir_disk.mkdir(buffer);

      snprintf(buffer, 12, "sector_%d", se);
      auto dir_sector = dir_ring.mkdir(buffer);

      chToPoints_[chName] = dir_sector.make<TH2D>(("Expected_"+chName).c_str(), ("Expected points "+chName).c_str(), 100, -width/2, width/2, 100, -height/2, height/2);
      chToRPCs_[chName] = dir_sector.make<TH2D>(("RPC_"+chName).c_str(), ("RPC "+chName).c_str(), 100, -width/2, width/2, 100, -height/2, height/2);
    }
  }
}

void RPCPointNtupleMaker::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  b_barrelData_->clear();
  b_endcapData_->clear();

  b_run = event.id().run();
  b_lumi = event.id().luminosityBlock();
  b_event = event.id().event();

  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  edm::Handle<reco::VertexCollection> vertexHandle;
  event.getByToken(vertexToken_, vertexHandle);
  b_nPV = vertexHandle->size();
  //const reco::Vertex pv = vertexHandle->at(0);

  std::map<RPCDetId, RPCBarrelData> barrelDataMap;
  std::map<RPCDetId, RPCEndcapData> endcapDataMap;

  // Collect extrapolated points from DT
  edm::Handle<RPCRecHitCollection> dtPointHandle;
  event.getByToken(dtPointToken_, dtPointHandle);
  for ( auto rpcItr = dtPointHandle->begin(); rpcItr != dtPointHandle->end(); ++rpcItr ) {
    const auto rpcId = rpcItr->rpcId();
    const auto rpcLx = rpcItr->localPosition().x();
    const auto rpcLy = rpcItr->localPosition().y();
    const auto rpcGp = rpcGeom->roll(rpcId)->toGlobal(rpcItr->localPosition());
    if ( rpcId.region() == 0 ) {
      auto datItr = barrelDataMap.find(rpcId);
      if ( datItr == barrelDataMap.end() ) {
        datItr = barrelDataMap.insert(std::make_pair(rpcId, RPCBarrelData(rpcId))).first;
      }
      datItr->second.expLx.push_back(rpcLx);
      datItr->second.expLy.push_back(rpcLy);
      datItr->second.expGx.push_back(rpcGp.x());
      datItr->second.expGy.push_back(rpcGp.y());
      datItr->second.expGz.push_back(rpcGp.z());
    }
    else {
      auto datItr = endcapDataMap.find(rpcId);
      if ( datItr == endcapDataMap.end() ) {
        datItr = endcapDataMap.insert(std::make_pair(rpcId, RPCEndcapData(rpcId))).first;
      }
      datItr->second.expLx.push_back(rpcLx);
      datItr->second.expLy.push_back(rpcLy);
      datItr->second.expGx.push_back(rpcGp.x());
      datItr->second.expGy.push_back(rpcGp.y());
      datItr->second.expGz.push_back(rpcGp.z());
    }
  }

  // Collect extrapolated points from CSC
  edm::Handle<RPCRecHitCollection> cscPointHandle;
  event.getByToken(cscPointToken_, cscPointHandle);
  for ( auto rpcItr = cscPointHandle->begin(); rpcItr != cscPointHandle->end(); ++rpcItr ) {
    const auto rpcId = rpcItr->rpcId();
    const auto rpcLx = rpcItr->localPosition().x();
    const auto rpcLy = rpcItr->localPosition().y();
    const auto rpcGp = rpcGeom->roll(rpcId)->toGlobal(rpcItr->localPosition());
    if ( rpcId.region() == 0 ) {
      auto datItr = barrelDataMap.find(rpcId);
      if ( datItr == barrelDataMap.end() ) {
        datItr = barrelDataMap.insert(std::make_pair(rpcId, RPCBarrelData(rpcId))).first;
      }
      datItr->second.expLx.push_back(rpcLx);
      datItr->second.expLy.push_back(rpcLy);
      datItr->second.expGx.push_back(rpcGp.x());
      datItr->second.expGy.push_back(rpcGp.y());
      datItr->second.expGz.push_back(rpcGp.z());
    }
    else {
      auto datItr = endcapDataMap.find(rpcId);
      if ( datItr == endcapDataMap.end() ) {
        datItr = endcapDataMap.insert(std::make_pair(rpcId, RPCEndcapData(rpcId))).first;
      }
      datItr->second.expLx.push_back(rpcLx);
      datItr->second.expLy.push_back(rpcLy);
      datItr->second.expGx.push_back(rpcGp.x());
      datItr->second.expGy.push_back(rpcGp.y());
      datItr->second.expGz.push_back(rpcGp.z());
    }
  }

  // Skip if no extrapolated point
  if ( barrelDataMap.empty() and endcapDataMap.empty() ) return;

  // Find matching RPC hits
  edm::Handle<RPCRecHitCollection> rpcHitHandle;
  event.getByToken(rpcHitToken_, rpcHitHandle);
  for ( auto rpcItr = rpcHitHandle->begin(); rpcItr != rpcHitHandle->end(); ++rpcItr ) {
    const auto rpcId = rpcItr->rpcId();
    const auto rpcLx = rpcItr->localPosition().x();
    const auto rpcLex = rpcItr->localPositionError().xx();
    const auto rpcGp = rpcGeom->roll(rpcId)->toGlobal(rpcItr->localPosition());
    if ( rpcId.region() == 0 ) {
      auto datItr = barrelDataMap.find(rpcId);
      if ( datItr == barrelDataMap.end() ) continue;
      datItr->second.rpcLx.push_back(rpcLx);
      datItr->second.rpcLex.push_back(rpcLex);
      datItr->second.rpcGx.push_back(rpcGp.x());
      datItr->second.rpcGy.push_back(rpcGp.y());
      datItr->second.rpcGz.push_back(rpcGp.z());
    }
    else {
      auto datItr = endcapDataMap.find(rpcId);
      if ( datItr == endcapDataMap.end() ) continue;
      datItr->second.rpcLx.push_back(rpcLx);
      datItr->second.rpcLex.push_back(rpcLex);
      datItr->second.rpcGx.push_back(rpcGp.x());
      datItr->second.rpcGy.push_back(rpcGp.y());
      datItr->second.rpcGz.push_back(rpcGp.z());
    }
  }

  if ( doHist_ ) fillHistograms(barrelDataMap, endcapDataMap);

  if ( doTree_ ) {
    // Put everything into the output collection
    for ( auto itr = barrelDataMap.begin(); itr != barrelDataMap.end(); ++itr ) {
      b_barrelData_->push_back(itr->second);
    }
    for ( auto itr = endcapDataMap.begin(); itr != endcapDataMap.end(); ++itr ) {
      b_endcapData_->push_back(itr->second);
    }
    tree_->Fill();
  }

}

void RPCPointNtupleMaker::fillHistograms(const std::map<RPCDetId, RPCBarrelData>& barrelDataMap,
                                         const std::map<RPCDetId, RPCEndcapData>& endcapDataMap)
{
  for ( auto itr = barrelDataMap.begin(); itr != barrelDataMap.end(); ++itr ) {
    const RPCDetId& id = itr->first;
    const RPCBarrelData& dat = itr->second;

    const string chName = RPCGeomServ(id).chambername();
    auto hPointsItr = chToPoints_.find(chName);
    auto hRPCsItr = chToRPCs_.find(chName);
    if ( hPointsItr == chToPoints_.end() ) continue;
    if ( hRPCsItr == chToRPCs_.end() ) continue;

    for ( int i=0, n=dat.expLx.size(); i<n; ++i ) {
      hXYExpBarrel_->Fill(dat.expGx[i], dat.expGy[i]);
      hXYExpBarrelByWheel_[id.ring()]->Fill(dat.expGx[i], dat.expGy[i]);
      hPointsItr->second->Fill(dat.expLx[i], dat.expLy[i]);
    }
    for ( int i=0, n=dat.rpcLx.size(); i<n; ++i ) {
      int matched = -1;
      double dx = dat.rpcLex[i]*3;
      for ( int j=0, m=dat.expLx.size(); j<m; ++j ) {
        const double tmpdx = std::abs(dat.rpcLx[i]-dat.expLx[j]);
        if ( tmpdx < dx ) { matched = j; dx = tmpdx; }
      }
      if ( matched == -1 ) continue;

      hXYRPCBarrel_->Fill(dat.rpcGx[i], dat.rpcGy[i]);
      hXYRPCBarrelByWheel_[id.ring()]->Fill(dat.expGx[i], dat.expGy[i]);
      hRPCsItr->second->Fill(dat.expLx[matched], dat.expLy[matched]);
    }
  }
  for ( auto itr = endcapDataMap.begin(); itr != endcapDataMap.end(); ++itr ) {
    const RPCDetId& id = itr->first;
    const RPCEndcapData& dat = itr->second;

    const string chName = RPCGeomServ(id).chambername();
    auto hPointsItr = chToPoints_.find(chName);
    auto hRPCsItr = chToRPCs_.find(chName);
    if ( hPointsItr == chToPoints_.end() ) continue;
    if ( hRPCsItr == chToRPCs_.end() ) continue;

    for ( int i=0, n=dat.expLx.size(); i<n; ++i ) {
      hPointsItr->second->Fill(dat.expLx[i], dat.expLy[i]);
      if      ( id.region() == +1 ) {
        hXYExpEndcapP_->Fill(dat.expGx[i], dat.expGy[i]);
        hXYExpEndcapByDisk_[id.station()]->Fill(dat.expGx[i], dat.expGy[i]);
      }
      else if ( id.region() == -1 ) {
        hXYExpEndcapM_->Fill(dat.expGx[i], dat.expGy[i]);
        hXYExpEndcapByDisk_[id.station()]->Fill(dat.expGx[i], dat.expGy[i]);
      }
    }
    for ( int i=0, n=dat.rpcLx.size(); i<n; ++i ) {
      int matched = -1;
      double dx = dat.rpcLex[i]*3;
      for ( int j=0, m=dat.expLx.size(); j<m; ++j ) {
        const double tmpdx = std::abs(dat.rpcLx[i]-dat.expLx[j]);
        if ( tmpdx < dx ) { matched = j; dx = tmpdx; }
      }
      if ( matched == -1 ) continue;

      if      ( id.region() == +1 ) {
        hXYRPCEndcapP_->Fill(dat.rpcGx[i], dat.rpcGy[i]);
        hXYRPCEndcapByDisk_[id.station()]->Fill(dat.expGx[i], dat.expGy[i]);
      }
      else if ( id.region() == -1 ) {
        hXYRPCEndcapM_->Fill(dat.rpcGx[i], dat.rpcGy[i]);
        hXYRPCEndcapByDisk_[id.station()]->Fill(dat.expGx[i], dat.expGy[i]);
      }
      hRPCsItr->second->Fill(dat.expLx[matched], dat.expLy[matched]);
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCPointNtupleMaker);
