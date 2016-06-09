#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
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

#include "TTree.h"
#include "TH1D.h"
#include "TH2D.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class RPCPointNtupleMaker : public edm::one::EDAnalyzer<edm::one::SharedResources>
{
public:
  RPCPointNtupleMaker(const edm::ParameterSet& pset);
  virtual ~RPCPointNtupleMaker() {};
  void analyze(const edm::Event& event, const edm::EventSetup& eventSetup) override;

private:
  edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_, dtPointToken_, cscPointToken_;
  edm::EDGetTokenT<reco::VertexCollection> vertexToken_;

  // Trees and histograms
  TTree* tree_;
  unsigned char b_run, b_lumi;
  unsigned long long int b_event;
  unsigned char b_nPV;

  // Per-detector information
  std::unique_ptr<std::vector<RPCBarrelData> > b_barrelData_;
  std::unique_ptr<std::vector<RPCEndcapData> > b_endcapData_;
};

RPCPointNtupleMaker::RPCPointNtupleMaker(const edm::ParameterSet& pset)
{
  rpcHitToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"));
  dtPointToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("dtPoints"));
  cscPointToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("cscPoints"));
  vertexToken_ = consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"));

  usesResource("TFileService");
  edm::Service<TFileService> fs;
  tree_ = fs->make<TTree>("tree", "tree");

  tree_->Branch("run", &b_run, "run/b"); // 8 bit unsigned integer
  tree_->Branch("lumi", &b_lumi, "lumi/b"); // 8 bit unsigned integer
  tree_->Branch("event", &b_event, "event/l"); // 64bit unsigned integer

  tree_->Branch("nPV", &b_nPV, "nPV/b");

  b_barrelData_.reset(new std::vector<RPCBarrelData>());
  b_endcapData_.reset(new std::vector<RPCEndcapData>());
  tree_->Branch("Barrel", "std::vector<RPCBarrelData>", &*b_barrelData_);
  tree_->Branch("Endcap", "std::vector<RPCEndcapData>", &*b_endcapData_);

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

  // Put everything into the output collection
  for ( auto itr = barrelDataMap.begin(); itr != barrelDataMap.end(); ++itr ) {
    b_barrelData_->push_back(itr->second);
  }
  for ( auto itr = endcapDataMap.begin(); itr != endcapDataMap.end(); ++itr ) {
    b_endcapData_->push_back(itr->second);
  }

  tree_->Fill();
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCPointNtupleMaker);
