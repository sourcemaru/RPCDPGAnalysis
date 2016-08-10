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
#include "TH1F.h"
#include "TH2F.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class RPCPointAnalyzer : public edm::one::EDAnalyzer<edm::one::WatchRuns, edm::one::SharedResources>
{
public:
  RPCPointAnalyzer(const edm::ParameterSet& pset);
  virtual ~RPCPointAnalyzer() {};
  void beginRun(const edm::Run& run, const edm::EventSetup& eventSetup) override;
  void endRun(const edm::Run&, const edm::EventSetup&) override {};
  void analyze(const edm::Event& event, const edm::EventSetup& eventSetup) override;

  struct Hists {
    std::vector<TH1F*> hFloatVars_;

    TH2F* hXYExpBarrel_, * hXYExpEndcapP_, * hXYExpEndcapM_;
    TH2F* hXYRPCBarrel_, * hXYRPCEndcapP_, * hXYRPCEndcapM_;
    std::map<int, TH2F*> hXYExpBarrelByWheel_, hXYRPCBarrelByWheel_;
    std::map<int, TH2F*> hZPhiExpBarrelByStation_, hZPhiExpOnRPCBarrelByStation_;
    std::map<int, TH2F*> hXYExpEndcapByDisk_, hXYRPCEndcapByDisk_, hXYExpOnRPCEndcapByDisk_;
    std::map<int, TH1F*> hResBarrelByWheel_, hResBarrelByStation_, hResEndcapByDisk_;;
    std::map<int, TH1F*> hPullBarrelByWheel_, hPullBarrelByStation_, hPullEndcapByDisk_;;
    std::map<std::string, TH2F*> chToExps_, chToRPCs_;
    std::map<std::string, TH1F*> chToRollExps_, chToRollRPCs_;
    std::map<std::string, TH1F*> chToRollExpsNoFid_, chToRollRPCsNoFid_;
  };

private:
  void fillHistograms(const std::map<RPCDetId, RPCBarrelData>& barrelDataMap,
                      const std::map<RPCDetId, RPCEndcapData>& endcapDataMap,
                      Hists& h);

  edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_;
  std::vector< edm::EDGetTokenT<RPCRecHitCollection>> refHitTokens_;
  edm::EDGetTokenT<reco::VertexCollection> vertexToken_;

  const bool doTree_, doHist_, doHistByRun_;
  const bool doChamberMuography_;

  // Trees and histograms
  TTree* tree_;
  unsigned int b_run, b_lumi;
  unsigned long long int b_event;
  unsigned char b_nPV;

  // Per-detector information
  std::unique_ptr<std::vector<RPCBarrelData> > b_barrelData_;
  std::unique_ptr<std::vector<RPCEndcapData> > b_endcapData_;

  std::map<unsigned int, Hists> hists_;
};

RPCPointAnalyzer::RPCPointAnalyzer(const edm::ParameterSet& pset):
  doTree_(pset.getUntrackedParameter<bool>("doTree")),
  doHist_(pset.getUntrackedParameter<bool>("doHist")),
  doHistByRun_(pset.getUntrackedParameter<bool>("doHistByRun")),
  doChamberMuography_(pset.getUntrackedParameter<bool>("doChamberMuography"))
{
  rpcHitToken_ = consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"));
  for ( auto x : pset.getParameter<std::vector<edm::InputTag>>("refPoints") ) {
    refHitTokens_.push_back(consumes<RPCRecHitCollection>(x));
  }
  vertexToken_ = consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"));

  b_barrelData_.reset(new std::vector<RPCBarrelData>());
  b_endcapData_.reset(new std::vector<RPCEndcapData>());

  usesResource("TFileService");
  edm::Service<TFileService> fs;
  if ( doTree_ ) {
    tree_ = fs->make<TTree>("tree", "tree");

    tree_->Branch("run", &b_run, "run/i"); // unsigned integer
    tree_->Branch("lumi", &b_lumi, "lumi/i"); // unsigned integer
    tree_->Branch("event", &b_event, "event/l"); // 64bit unsigned integer

    tree_->Branch("nPV", &b_nPV, "nPV/b");

    tree_->Branch("Barrel", "std::vector<RPCBarrelData>", &*b_barrelData_);
    tree_->Branch("Endcap", "std::vector<RPCEndcapData>", &*b_endcapData_);
  }
}

void RPCPointAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  usesResource("TFileService");
  edm::Service<TFileService> fs;

  const int runNumber = doHistByRun_ ? run.id().run() : 0;
  if ( hists_.count(runNumber) == 0 ) {
    auto dir = fs->mkdir(Form("Run%06d", runNumber));
    auto& h = hists_[runNumber] = Hists();

    auto dir_barrel = dir.mkdir("Barrel");
    h.hXYExpBarrel_  = dir_barrel.make<TH2F>("hXYExpBarrel" , "Expected points in Barrel;X (cm);Y (cm)" , 500, -1000, 1000, 500, -1000, 1000);
    h.hXYRPCBarrel_  = dir_barrel.make<TH2F>("hXYRPCBarrel" , "RPC in Barrel;X (cm);Y (cm)" , 500, -1000, 1000, 500, -1000, 1000);

    auto dir_endcapP = dir.mkdir("Endcap+");
    h.hXYExpEndcapP_ = dir_endcapP.make<TH2F>("hXYExpEndcap+", "Expected points in Endcap+;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);
    h.hXYRPCEndcapP_ = dir_endcapP.make<TH2F>("hXYRPCEndcap+", "RPC in Endcap+;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);
    auto dir_endcapM = dir.mkdir("Endcap-");
    h.hXYExpEndcapM_ = dir_endcapM.make<TH2F>("hXYExpEndcap-", "Expected points in Endcap-;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);
    h.hXYRPCEndcapM_ = dir_endcapM.make<TH2F>("hXYRPCEndcap-", "RPC in Endcap-;X (cm);Y (cm)", 500, -1000, 1000, 500, -1000, 1000);

    edm::ESHandle<RPCGeometry> rpcGeom;
    eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

    for ( const RPCChamber* ch : rpcGeom->chambers() ) {
      const RPCDetId rpcId = ch->id();
      const std::string chName = RPCGeomServ(rpcId).chambername();
      const double height = ch->surface().bounds().length();
      const double width = ch->surface().bounds().width();
      if ( rpcId.region() == 0 ) {
        const int wh = rpcId.ring();
        const int st = rpcId.station();
        const int se = rpcId.sector();
        const int la = rpcId.layer();

        const string whStr = Form("Wheel_%d", wh);
        auto dir_wheel = dir_barrel.mkdir(whStr);
        if ( !h.hXYExpBarrelByWheel_[wh] ) {
          h.hXYExpBarrelByWheel_[wh] = dir_wheel.make<TH2F>(("hXYExp"+whStr).c_str(), ("Expected points "+whStr+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
          h.hXYRPCBarrelByWheel_[wh] = dir_wheel.make<TH2F>(("hXYRPC"+whStr).c_str(), ("RPC in "+whStr+";X (cm);Y (cm)").c_str(), 500, -1000, 1000, 500, -1000, 1000);
          h.hResBarrelByWheel_[wh] = dir_wheel.make<TH1F>(("hRes"+whStr).c_str(), ("Residual in "+whStr+";#DeltaX (cm)").c_str(), 500, -50, 50);
          h.hPullBarrelByWheel_[wh] = dir_wheel.make<TH1F>(("hPull"+whStr).c_str(), ("Pull in "+whStr+";#DeltaX (cm)").c_str(), 200, -10, 10);
        }

        const int stla = st*10+la;
        if ( !h.hZPhiExpBarrelByStation_[stla] ) {
          h.hZPhiExpBarrelByStation_[stla] = dir_barrel.make<TH2F>(Form("hZPhiExpBarrel_Station%d_Layer%d", st, la),
                                                                   Form("Expected points in Barrel station %d layer %d;Z (cm);#phi", st, la),
                                                                   700, -700, 700, 720, -3.14159265, 3.14159265);
          h.hZPhiExpOnRPCBarrelByStation_[stla] = dir_barrel.make<TH2F>(Form("hZPhiExpOnRPCBarrel_Station%d_Layer%d", st, la),
                                                                        Form("Expected Points matched to RPC in Barrel station %d layer %d;Z (cm);#phi", st, la),
                                                                        700, -700, 700, 720, -3.14159265, 3.14159265);
          h.hResBarrelByStation_[stla] = dir_barrel.make<TH1F>(Form("hResBarrel_Station%d_Layer%d", st, la),
                                                               Form("Residual in Barrel Station %d layer %d;#DeltaX (cm)", st, la), 500, -50, 50);
          h.hPullBarrelByStation_[stla] = dir_barrel.make<TH1F>(Form("hPullBarrel_Station%d_Layer%d", st, la),
                                                                Form("Pull in Barrel Station %d layer %d;#DeltaX (cm)", st, la), 200, -10, 10);
        }
        auto dir_sector = dir_wheel.mkdir(Form("sector_%d", se));
        auto dir_station = dir_sector.mkdir(Form("station_%d", st));

        if ( doChamberMuography_ ) {
          const int wh2 = int(std::max(height, width)/2+10);
          h.chToExps_[chName] = dir_station.make<TH2F>(("Exp_"+chName).c_str(), ("Expected points "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
          h.chToRPCs_[chName] = dir_station.make<TH2F>(("RPC_"+chName).c_str(), ("Expected points matched to RPC "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
        }

        const auto rolls = ch->rolls();
        const int nRoll = rolls.size();
        h.chToRollExps_[chName] = dir_station.make<TH1F>(("RollExp_"+chName).c_str(), ("Roll Expected points "+chName).c_str(), nRoll, 1, nRoll+1);
        h.chToRollRPCs_[chName] = dir_station.make<TH1F>(("RollRPC_"+chName).c_str(), ("RPCs "+chName).c_str(), nRoll, 1, nRoll+1);
        h.chToRollExpsNoFid_[chName] = dir_station.make<TH1F>(("RollExpNoFid_"+chName).c_str(), ("Roll Expected points no fiducial cut"+chName).c_str(), nRoll, 1, nRoll+1);
        h.chToRollRPCsNoFid_[chName] = dir_station.make<TH1F>(("RollRPCNoFid_"+chName).c_str(), ("RPCs no fiducial cut"+chName).c_str(), nRoll, 1, nRoll+1);
        for ( int i=0; i<nRoll; ++i ) {
          const string rollName = RPCGeomServ(rolls[i]->id()).name();
          h.chToRollExps_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
          h.chToRollRPCs_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
          h.chToRollExpsNoFid_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
          h.chToRollRPCsNoFid_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        }
      }
      else {
        const int di = rpcId.region()*rpcId.station();
        const int rn = rpcId.ring();
        const int se = rpcId.sector();

        const std::string diStr = Form("Disk_%d", di);
        auto dir_disk = rpcId.region() == 1 ? dir_endcapP.mkdir(diStr) : dir_endcapM.mkdir(diStr);
        if ( !h.hXYExpEndcapByDisk_[di] ) {
          h.hXYExpEndcapByDisk_[di] = dir_disk.make<TH2F>(("hXYExp_"+diStr).c_str(), ("Expected points "+diStr+";X (cm);Y (cm)").c_str(), 1000, -1000, 1000, 1000, -1000, 1000);
          h.hXYRPCEndcapByDisk_[di] = dir_disk.make<TH2F>(("hXYRPC_"+diStr).c_str(), ("RPC in "+diStr+";X (cm);Y (cm)").c_str(), 1000, -1000, 1000, 1000, -1000, 1000);
          h.hXYExpOnRPCEndcapByDisk_[di] = dir_disk.make<TH2F>(("hXYExpOnRPC_"+diStr).c_str(),
                                                               ("Expected points matched to RPC in "+diStr+";X (cm);Y (cm)").c_str(),
                                                               1000, -1000, 1000, 1000, -1000, 1000);
          h.hResEndcapByDisk_[di] = dir_disk.make<TH1F>(("hRes_"+diStr).c_str(), ("Residual "+diStr+";#DeltaX (cm)").c_str(), 500, -50, 50);
          h.hPullEndcapByDisk_[di] = dir_disk.make<TH1F>(("hPull"+diStr).c_str(), ("Pull in "+diStr+";#DeltaX (cm)").c_str(), 200, -10, 10);
        }

        auto dir_ring = dir_disk.mkdir(Form("ring_%d", rn));
        auto dir_sector = dir_ring.mkdir(Form("sector_%d", se));

        if ( doChamberMuography_ ) {
          const auto bounds = dynamic_cast<const TrapezoidalPlaneBounds&>(ch->surface().bounds());
          const int wh2 = int(std::max(1.*bounds.width(), height)/2+10);
          h.chToExps_[chName] = dir_sector.make<TH2F>(("Exp_"+chName).c_str(), ("Expected points "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
          h.chToRPCs_[chName] = dir_sector.make<TH2F>(("RPC_"+chName).c_str(), ("Expected Points matched to RPC "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
        }

        const auto rolls = ch->rolls();
        const int nRoll = rolls.size();
        h.chToRollExps_[chName] = dir_sector.make<TH1F>(("RollExp_"+chName).c_str(), ("Roll Expected points "+chName).c_str(), nRoll, 1, nRoll+1);
        h.chToRollRPCs_[chName] = dir_sector.make<TH1F>(("RollRPC_"+chName).c_str(), ("RPCs "+chName).c_str(), nRoll, 1, nRoll+1);
        h.chToRollExpsNoFid_[chName] = dir_sector.make<TH1F>(("RollExpNoFid_"+chName).c_str(), ("Roll Expected points no fiducial cut"+chName).c_str(), nRoll, 1, nRoll+1);
        h.chToRollRPCsNoFid_[chName] = dir_sector.make<TH1F>(("RollRPCNoFid_"+chName).c_str(), ("RPCs no fiducial cut"+chName).c_str(), nRoll, 1, nRoll+1);
        for ( int i=0; i<nRoll; ++i ) {
          const string rollName = RPCGeomServ(rolls[i]->id()).name();
          h.chToRollExps_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
          h.chToRollRPCs_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
          h.chToRollExpsNoFid_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
          h.chToRollRPCsNoFid_[chName]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        }
      }
    }
  }
}

void RPCPointAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
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
  for ( auto refHitToken : refHitTokens_ ) {
    edm::Handle<RPCRecHitCollection> refHitHandle;
    event.getByToken(refHitToken, refHitHandle);
    for ( auto rpcItr = refHitHandle->begin(); rpcItr != refHitHandle->end(); ++rpcItr ) {
      const auto rpcId = rpcItr->rpcId();
      const auto roll = rpcGeom->roll(rpcId);
      const auto& bound = roll->surface().bounds();
      if ( !bound.inside(rpcItr->localPosition()) ) continue;
      const auto rpcGp = roll->toGlobal(rpcItr->localPosition());
      const auto rpcLp = rpcGeom->chamber(rpcId)->toLocal(rpcGp);
      const auto rpcLx = rpcLp.x();
      const auto rpcLy = rpcLp.y();
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

        datItr->second.isInFiducial.push_back([&](){
          const double h = bound.length();
          if ( std::abs(rpcItr->localPosition().y()) > h/2-8 ) return false;

          const double w = bound.width();
          if ( std::abs(rpcItr->localPosition().x()) > w/2-8 ) return false;

          return true;
        }());
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

        datItr->second.isInFiducial.push_back([&](){
          const double h = bound.length();
          if ( std::abs(rpcItr->localPosition().y()) > h/2-8 ) return false;

          const double wT = bound.width();
          const double w0 = bound.widthAtHalfLength();
          const double slope = (wT-w0)/h;
          const double w2AtY = slope*rpcItr->localPosition().y() + w0/2;
          if ( std::abs(rpcItr->localPosition().x()) > w2AtY-8 ) return false;

          return true;
        }());
      }
    }
  }

  // Skip if no extrapolated point
  if ( barrelDataMap.empty() and endcapDataMap.empty() ) return;

  // Find matching RPC hits
  edm::Handle<RPCRecHitCollection> rpcHitHandle;
  event.getByToken(rpcHitToken_, rpcHitHandle);
  for ( auto rpcItr = rpcHitHandle->begin(); rpcItr != rpcHitHandle->end(); ++rpcItr ) {
    const auto rpcId = rpcItr->rpcId();
    if ( !rpcGeom->roll(rpcId) or !rpcGeom->chamber(rpcId) ) continue;
    const auto rpcGp = rpcGeom->roll(rpcId)->toGlobal(rpcItr->localPosition());
    const auto rpcLp = rpcGeom->chamber(rpcId)->toLocal(rpcGp);
    const auto rpcLx = rpcLp.x();
    const auto rpcLex = sqrt(rpcItr->localPositionError().xx());
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

  if ( doHist_ ) {
    fillHistograms(barrelDataMap, endcapDataMap, hists_[doHistByRun_ ? event.id().run() : 0]);
  }

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

void RPCPointAnalyzer::fillHistograms(const std::map<RPCDetId, RPCBarrelData>& barrelDataMap,
                                         const std::map<RPCDetId, RPCEndcapData>& endcapDataMap,
                                         RPCPointAnalyzer::Hists& h)
{
  for ( auto itr = barrelDataMap.begin(); itr != barrelDataMap.end(); ++itr ) {
    const RPCDetId& id = itr->first;
    const RPCBarrelData& dat = itr->second;

    RPCGeomServ rpcName(id);
    const string chName = rpcName.chambername();
    const string rollName = rpcName.name();
    auto hExpsItr = h.chToExps_.find(chName);
    auto hRPCsItr = h.chToRPCs_.find(chName);
    auto hRollExpsItr = h.chToRollExps_.find(chName);
    auto hRollRPCsItr = h.chToRollRPCs_.find(chName);
    auto hRollExpsNoFidItr = h.chToRollExpsNoFid_.find(chName);
    auto hRollRPCsNoFidItr = h.chToRollRPCsNoFid_.find(chName);
    if ( doChamberMuography_ and hExpsItr == h.chToExps_.end() ) continue;
    if ( doChamberMuography_ and hRPCsItr == h.chToRPCs_.end() ) continue;
    if ( hRollExpsItr == h.chToRollExps_.end() ) continue;
    if ( hRollRPCsItr == h.chToRollRPCs_.end() ) continue;
    if ( hRollExpsNoFidItr == h.chToRollExpsNoFid_.end() ) continue;
    if ( hRollRPCsNoFidItr == h.chToRollRPCsNoFid_.end() ) continue;

    const int stla = id.station()*10+id.layer();

    for ( int i=0, n=dat.expLx.size(); i<n; ++i ) {
      h.hXYExpBarrel_->Fill(dat.expGx[i], dat.expGy[i]);
      h.hZPhiExpBarrelByStation_[stla]->Fill(dat.expGz[i], atan2(dat.expGy[i], dat.expGx[i]));
      h.hXYExpBarrelByWheel_[id.ring()]->Fill(dat.expGx[i], dat.expGy[i]);
      if ( doChamberMuography_ ) hExpsItr->second->Fill(dat.expLx[i], dat.expLy[i]);

      const int binRoll = hRollExpsItr->second->GetXaxis()->FindBin(rollName.c_str());
      hRollExpsNoFidItr->second->Fill(binRoll);
      if ( dat.isInFiducial[i] ) hRollExpsItr->second->Fill(binRoll);

      int matched = -1;
      double dx = 50; //dat.rpcLex[i]*3;
      for ( int j=0, m=dat.rpcLx.size(); j<m; ++j ) {
        const double tmpdx = std::abs(dat.rpcLx[j]-dat.expLx[i]);
        if ( tmpdx < dx ) { matched = j; dx = tmpdx; }
      }
      if ( matched == -1 ) continue;
      dx = dat.rpcLx[matched]-dat.expLx[i];

      h.hXYRPCBarrel_->Fill(dat.rpcGx[matched], dat.rpcGy[matched]);
      h.hZPhiExpOnRPCBarrelByStation_[stla]->Fill(dat.expGz[i], atan2(dat.expGy[i], dat.expGx[i]));
      h.hXYRPCBarrelByWheel_[id.ring()]->Fill(dat.rpcGx[matched], dat.rpcGy[matched]);
      if ( doChamberMuography_ ) hRPCsItr->second->Fill(dat.expLx[i], dat.expLy[i]);
      h.hResBarrelByWheel_[id.ring()]->Fill(dx);
      h.hResBarrelByStation_[stla]->Fill(dx);
      h.hPullBarrelByWheel_[id.ring()]->Fill(dx/dat.rpcLex[matched]);
      h.hPullBarrelByStation_[stla]->Fill(dx/dat.rpcLex[matched]);

      hRollRPCsNoFidItr->second->Fill(binRoll);
      if ( dat.isInFiducial[i] ) hRollRPCsItr->second->Fill(binRoll);
    }
  }
  for ( auto itr = endcapDataMap.begin(); itr != endcapDataMap.end(); ++itr ) {
    const RPCDetId& id = itr->first;
    const RPCEndcapData& dat = itr->second;

    RPCGeomServ rpcName(id);
    const string chName = rpcName.chambername();
    const string rollName = rpcName.name();
    auto hExpsItr = h.chToExps_.find(chName);
    auto hRPCsItr = h.chToRPCs_.find(chName);
    auto hRollExpsItr = h.chToRollExps_.find(chName);
    auto hRollRPCsItr = h.chToRollRPCs_.find(chName);
    auto hRollExpsNoFidItr = h.chToRollExpsNoFid_.find(chName);
    auto hRollRPCsNoFidItr = h.chToRollRPCsNoFid_.find(chName);
    if ( doChamberMuography_ and hExpsItr == h.chToExps_.end() ) continue;
    if ( doChamberMuography_ and hRPCsItr == h.chToRPCs_.end() ) continue;
    if ( hRollExpsItr == h.chToRollExps_.end() ) continue;
    if ( hRollRPCsItr == h.chToRollRPCs_.end() ) continue;
    if ( hRollExpsNoFidItr == h.chToRollExpsNoFid_.end() ) continue;
    if ( hRollRPCsNoFidItr == h.chToRollRPCsNoFid_.end() ) continue;

    const int di = id.region()*id.station();

    for ( int i=0, n=dat.expLx.size(); i<n; ++i ) {
      if      ( id.region() == +1 ) h.hXYExpEndcapP_->Fill(dat.expGx[i], dat.expGy[i]);
      else if ( id.region() == -1 ) h.hXYExpEndcapM_->Fill(dat.expGx[i], dat.expGy[i]);
      h.hXYExpEndcapByDisk_[di]->Fill(dat.expGx[i], dat.expGy[i]);
      if ( doChamberMuography_ ) hExpsItr->second->Fill(dat.expLx[i], dat.expLy[i]);

      const int binRoll = hRollExpsItr->second->GetXaxis()->FindBin(rollName.c_str());
      hRollExpsNoFidItr->second->Fill(binRoll);
      if ( dat.isInFiducial[i] ) hRollExpsItr->second->Fill(binRoll);

      int matched = -1;
      double dx = 50; //dat.rpcLex[i]*3;
      for ( int j=0, m=dat.rpcLx.size(); j<m; ++j ) {
        const double tmpdx = std::abs(dat.rpcLx[j]-dat.expLx[i]);
        if ( tmpdx < dx ) { matched = j; dx = tmpdx; }
      }
      if ( matched == -1 ) continue;
      dx = dat.rpcLx[matched]-dat.expLx[i];

      if      ( id.region() == +1 ) h.hXYRPCEndcapP_->Fill(dat.rpcGx[matched], dat.rpcGy[matched]);
      else if ( id.region() == -1 ) h.hXYRPCEndcapM_->Fill(dat.rpcGx[matched], dat.rpcGy[matched]);
      h.hXYRPCEndcapByDisk_[di]->Fill(dat.rpcGx[matched], dat.rpcGy[matched]);
      h.hXYExpOnRPCEndcapByDisk_[di]->Fill(dat.expGx[i], dat.expGy[i]);
      if ( doChamberMuography_ ) hRPCsItr->second->Fill(dat.expLx[i], dat.expLy[i]);
      h.hResEndcapByDisk_[di]->Fill(dx);
      h.hPullEndcapByDisk_[di]->Fill(dx/dat.rpcLex[matched]);

      hRollRPCsNoFidItr->second->Fill(binRoll);
      if ( dat.isInFiducial[i] ) hRollRPCsItr->second->Fill(binRoll);
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCPointAnalyzer);
