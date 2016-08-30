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

    std::map<int, TH2F*> hXYExpBarrelByWheel_, hXYRecBarrelByWheel_;
    std::map<int, TH2F*> hZPhiExpBarrelByStation_, hZPhiRecBarrelByStation_;
    std::map<int, TH2F*> hXYExpEndcapByDisk_, hXYRecEndcapByDisk_;
    std::map<int, TH1F*> hResBarrelByWheel_, hResBarrelByStation_, hResEndcapByDisk_;;
    std::map<int, TH1F*> hPullBarrelByWheel_, hPullBarrelByStation_, hPullEndcapByDisk_;;
    std::map<std::string, TH2F*> chToExps_, chToRPCs_;
    std::map<int, TH1F*> hSubdetExpBarrelByWheelStation_, hSubdetRecBarrelByWheelStation_;
    std::map<int, TH1F*> hSubdetExpEndcapByDiskRing_, hSubdetRecEndcapByDiskRing_;
    std::map<int, TH1F*> hSubdetExpBarrelByWheelStationNoFid_, hSubdetRecBarrelByWheelStationNoFid_;
    std::map<int, TH1F*> hSubdetExpEndcapByDiskRingNoFid_, hSubdetRecEndcapByDiskRingNoFid_;
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

    edm::ESHandle<RPCGeometry> rpcGeom;
    eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

    std::map<int, vector<string> > barrelBinLabels, endcapBinLabels;

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

        const string whStr = Form("Wheel%d", wh);
        auto dir_wheel = dir.mkdir(whStr);
        if ( !h.hXYExpBarrelByWheel_[wh] ) {
          h.hXYExpBarrelByWheel_[wh] = dir_wheel.make<TH2F>("hXYExp", ("Expected points "+whStr+";X (cm);Y (cm)").c_str(), 3200, -800, 800, 3200, -800, 800);
          h.hXYRecBarrelByWheel_[wh] = dir_wheel.make<TH2F>("hXYRec", ("Expected points matched to RPC in "+whStr+";X (cm);Y (cm)").c_str(), 3200, -800, 800, 3200, -800, 800);
          h.hResBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hResX", ("Residual in "+whStr+";#DeltaX (cm)").c_str(), 500, -50, 50);
          h.hPullBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hPullX", ("Pull in "+whStr+";#DeltaX (cm)").c_str(), 200, -10, 10);
        }

        const int stla = st*10+la;
        if ( !h.hZPhiExpBarrelByStation_[stla] ) {
          h.hZPhiExpBarrelByStation_[stla] = dir.make<TH2F>(Form("hZPhiExpBarrel_Station%d_Layer%d", st, la),
                                                            Form("Expected points in Barrel station %d layer %d;Z (cm);#phi", st, la),
                                                            2800, -700, 700, 360*5, -3.14159265, 3.14159265);
          h.hZPhiRecBarrelByStation_[stla] = dir.make<TH2F>(Form("hZPhiRecBarrel_Station%d_Layer%d", st, la),
                                                                 Form("Expected Points matched to RPC in Barrel station %d layer %d;Z (cm);#phi", st, la),
                                                                 2800, -700, 700, 360*5, -3.14159265, 3.14159265);
          h.hResBarrelByStation_[stla] = dir.make<TH1F>(Form("hResXBarrel_Station%d_Layer%d", st, la),
                                                        Form("Residual in Barrel Station %d layer %d;#DeltaX (cm)", st, la), 500, -50, 50);
          h.hPullBarrelByStation_[stla] = dir.make<TH1F>(Form("hPullXBarrel_Station%d_Layer%d", st, la),
                                                         Form("Pull in Barrel Station %d layer %d;#DeltaX (cm)", st, la), 200, -10, 10);
        }

        if ( doChamberMuography_ ) {
          auto dir_sector = dir_wheel.mkdir(Form("sector_%d", se));
          auto dir_station = dir_sector.mkdir(Form("station_%d", st));

          const int wh2 = int(std::max(height, width)/2+10);
          h.chToExps_[chName] = dir_station.make<TH2F>(("Exp_"+chName).c_str(), ("Expected points "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
          h.chToRPCs_[chName] = dir_station.make<TH2F>(("RPC_"+chName).c_str(), ("Expected points matched to RPC "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
        }

        const auto rolls = ch->rolls();
        const int nRoll = rolls.size();

        const int key = wh+10*st+100*la;
        if ( !h.hSubdetExpBarrelByWheelStation_[key] ) {
          const string suffix = Form("Station%d_Layer%d", st, la);
          h.hSubdetExpBarrelByWheelStation_[key] = dir_wheel.make<TH1F>(
            ("hSubdetExpBarrel_"+suffix).c_str(), ("Expected points in Barrel "+suffix).c_str(), 50, 1, 51);
          h.hSubdetRecBarrelByWheelStation_[key] = dir_wheel.make<TH1F>(
            ("hSubdetRecBarrel_"+suffix).c_str(), ("Expected points matched to RecHit in Barrel "+suffix).c_str(), 50, 1, 51);
          h.hSubdetExpBarrelByWheelStationNoFid_[key] = dir_wheel.make<TH1F>(
            ("hSubdetExpBarrel_"+suffix+"_NoFid").c_str(),
            ("Expected points in Barrel "+suffix+" without fiducial cut").c_str(), 50, 1, 51);
          h.hSubdetRecBarrelByWheelStationNoFid_[key] = dir_wheel.make<TH1F>(
            ("hSubdetRecBarrel_"+suffix+"_NoFid").c_str(),
            ("Expected points matched to RecHit in Barrel "+suffix+"without fiducial cut").c_str(), 50, 1, 51);
        }

        for ( int i=0; i<nRoll; ++i ) {
          const string rollName = RPCGeomServ(rolls[i]->id()).name();
          if ( barrelBinLabels.find(key) == barrelBinLabels.end() ) barrelBinLabels[key] = vector<string>();
          barrelBinLabels[key].push_back(rollName);
        }
      }
      else {
        const int di = rpcId.region()*rpcId.station();
        const int rn = rpcId.ring();
        const int se = rpcId.sector();

        const std::string diStr = Form("Disk%d", di);
        auto dir_disk = dir.mkdir(diStr);
        if ( !h.hXYExpEndcapByDisk_[di] ) {
          h.hXYExpEndcapByDisk_[di] = dir_disk.make<TH2F>("hXYExp", ("Expected points "+diStr+";X (cm);Y (cm)").c_str(), 3200, -800, 800, 3200, -800, 800);
          h.hXYRecEndcapByDisk_[di] = dir_disk.make<TH2F>("hXYRec", ("Expected points matched to RPC in "+diStr+";X (cm);Y (cm)").c_str(),
                                                          3200, -800, 800, 3200, -800, 800);
          h.hResEndcapByDisk_[di] = dir_disk.make<TH1F>("hResX", ("Residual "+diStr+";#DeltaX (cm)").c_str(), 500, -50, 50);
          h.hPullEndcapByDisk_[di] = dir_disk.make<TH1F>("hPull", ("Pull in "+diStr+";#DeltaX (cm)").c_str(), 200, -10, 10);
        }

        if ( doChamberMuography_ ) {
          auto dir_ring = dir_disk.mkdir(Form("ring_%d", rn));
          auto dir_sector = dir_ring.mkdir(Form("sector_%d", se));

          const auto bounds = dynamic_cast<const TrapezoidalPlaneBounds&>(ch->surface().bounds());
          const int wh2 = int(std::max(1.*bounds.width(), height)/2+10);
          h.chToExps_[chName] = dir_sector.make<TH2F>(("Exp_"+chName).c_str(), ("Expected points "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
          h.chToRPCs_[chName] = dir_sector.make<TH2F>(("RPC_"+chName).c_str(), ("Expected Points matched to RPC "+chName).c_str(), wh2, -wh2, wh2, wh2, -wh2, wh2);
        }

        const auto rolls = ch->rolls();
        const int nRoll = rolls.size();

        const int key = di+10*rn;
        if ( !h.hSubdetExpEndcapByDiskRing_[key] ) {
          const string suffix = Form("Ring%d", rn);
          h.hSubdetExpEndcapByDiskRing_[key] = dir_disk.make<TH1F>(
            ("hSubdetExpEndcap_"+suffix).c_str(), ("Expected points in Endcap "+suffix).c_str(), 36*3, 1, 1+36*3);
          h.hSubdetRecEndcapByDiskRing_[key] = dir_disk.make<TH1F>(
            ("hSubdetRecEndcap_"+suffix).c_str(), ("Expected points matched to RecHit in Endcap "+suffix).c_str(), 36*3, 1, 1+36*3);
          h.hSubdetExpEndcapByDiskRingNoFid_[key] = dir_disk.make<TH1F>(
            ("hSubdetExpEndcap_"+suffix+"_NoFid").c_str(),
            ("Expected points in Endcap "+suffix+" without fiducial cut").c_str(), 36*3, 1, 1+36*3);
          h.hSubdetRecEndcapByDiskRingNoFid_[key] = dir_disk.make<TH1F>(
            ("hSubdetRecEndcap_"+suffix+"_NoFid").c_str(),
            ("Expected points matched to RecHit in Endcap "+suffix+" without fiducial cut").c_str(), 36*3, 1, 1+36*3);
        }

        for ( int i=0; i<nRoll; ++i ) {
          const string rollName = RPCGeomServ(rolls[i]->id()).name();
          if ( endcapBinLabels.find(key) == endcapBinLabels.end() ) endcapBinLabels[key] = vector<string>();
          endcapBinLabels[key].push_back(rollName);
        }
      }
    }

    for ( auto x : barrelBinLabels ) {
      const int key = x.first;
      sort(x.second.begin(), x.second.end());
      for ( int i=0, n=x.second.size(); i<n; ++i ) {
        const auto rollName = x.second[i];
        h.hSubdetExpBarrelByWheelStation_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        h.hSubdetRecBarrelByWheelStation_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        h.hSubdetExpBarrelByWheelStationNoFid_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        h.hSubdetRecBarrelByWheelStationNoFid_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
      }
      h.hSubdetExpBarrelByWheelStation_[key]->LabelsDeflate("X");
      h.hSubdetRecBarrelByWheelStation_[key]->LabelsDeflate("X");
      h.hSubdetExpBarrelByWheelStationNoFid_[key]->LabelsDeflate("X");
      h.hSubdetRecBarrelByWheelStationNoFid_[key]->LabelsDeflate("X");
    }
    for ( auto x : endcapBinLabels ) {
      const int key = x.first;
      sort(x.second.begin(), x.second.end());
      for ( int i=0, n=x.second.size(); i<n; ++i ) {
        const auto rollName = x.second[i];
        h.hSubdetExpEndcapByDiskRing_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        h.hSubdetRecEndcapByDiskRing_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        h.hSubdetExpEndcapByDiskRingNoFid_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
        h.hSubdetRecEndcapByDiskRingNoFid_[key]->GetXaxis()->SetBinLabel(i+1, rollName.c_str());
      }
      h.hSubdetExpEndcapByDiskRing_[key]->LabelsDeflate("X");
      h.hSubdetRecEndcapByDiskRing_[key]->LabelsDeflate("X");
      h.hSubdetExpEndcapByDiskRingNoFid_[key]->LabelsDeflate("X");
      h.hSubdetRecEndcapByDiskRingNoFid_[key]->LabelsDeflate("X");
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
  b_nPV = 0;
  if ( vertexHandle.isValid() ) b_nPV = vertexHandle->size();
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
      if ( !bound.inside(LocalPoint(rpcItr->localPosition().x(), rpcItr->localPosition().y(), 0)) ) continue;
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
    if ( doChamberMuography_ and hExpsItr == h.chToExps_.end() ) continue;
    if ( doChamberMuography_ and hRPCsItr == h.chToRPCs_.end() ) continue;

    const int stla = id.station()*10+id.layer();
    const int key = id.ring()+10*id.station()+100*id.layer();
    const int binRoll = h.hSubdetExpBarrelByWheelStationNoFid_[key]->GetXaxis()->FindBin(rollName.c_str());

    for ( int i=0, n=dat.expLx.size(); i<n; ++i ) {
      h.hZPhiExpBarrelByStation_[stla]->Fill(dat.expGz[i], atan2(dat.expGy[i], dat.expGx[i]));
      h.hXYExpBarrelByWheel_[id.ring()]->Fill(dat.expGx[i], dat.expGy[i]);
      if ( doChamberMuography_ ) hExpsItr->second->Fill(dat.expLx[i], dat.expLy[i]);

      h.hSubdetExpBarrelByWheelStationNoFid_[key]->Fill(binRoll);
      if ( dat.isInFiducial[i] ) h.hSubdetExpBarrelByWheelStation_[key]->Fill(binRoll);

      int matched = -1;
      double dx = 50; //dat.rpcLex[i]*3;
      for ( int j=0, m=dat.rpcLx.size(); j<m; ++j ) {
        const double tmpdx = std::abs(dat.rpcLx[j]-dat.expLx[i]);
        if ( tmpdx < dx ) { matched = j; dx = tmpdx; }
      }
      if ( matched == -1 ) continue;
      dx = dat.rpcLx[matched]-dat.expLx[i];

      h.hXYRecBarrelByWheel_[id.ring()]->Fill(dat.expGx[i], dat.expGy[i]);
      h.hZPhiRecBarrelByStation_[stla]->Fill(dat.expGz[i], atan2(dat.expGy[i], dat.expGx[i]));
      if ( doChamberMuography_ ) hRPCsItr->second->Fill(dat.expLx[i], dat.expLy[i]);
      h.hResBarrelByWheel_[id.ring()]->Fill(dx);
      h.hResBarrelByStation_[stla]->Fill(dx);
      h.hPullBarrelByWheel_[id.ring()]->Fill(dx/dat.rpcLex[matched]);
      h.hPullBarrelByStation_[stla]->Fill(dx/dat.rpcLex[matched]);

      h.hSubdetRecBarrelByWheelStationNoFid_[key]->Fill(binRoll);
      if ( dat.isInFiducial[i] ) h.hSubdetRecBarrelByWheelStation_[key]->Fill(binRoll);
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
    if ( doChamberMuography_ and hExpsItr == h.chToExps_.end() ) continue;
    if ( doChamberMuography_ and hRPCsItr == h.chToRPCs_.end() ) continue;

    const int di = id.region()*id.station();
    const int key = di+10*id.ring();
    const int binRoll = h.hSubdetExpEndcapByDiskRing_[key]->GetXaxis()->FindBin(rollName.c_str());

    for ( int i=0, n=dat.expLx.size(); i<n; ++i ) {
      h.hXYExpEndcapByDisk_[di]->Fill(dat.expGx[i], dat.expGy[i]);
      if ( doChamberMuography_ ) hExpsItr->second->Fill(dat.expLx[i], dat.expLy[i]);

      h.hSubdetExpEndcapByDiskRingNoFid_[key]->Fill(binRoll);
      if ( dat.isInFiducial[i] ) h.hSubdetExpEndcapByDiskRing_[key]->Fill(binRoll);

      int matched = -1;
      double dx = 50; //dat.rpcLex[i]*3;
      for ( int j=0, m=dat.rpcLx.size(); j<m; ++j ) {
        const double tmpdx = std::abs(dat.rpcLx[j]-dat.expLx[i]);
        if ( tmpdx < dx ) { matched = j; dx = tmpdx; }
      }
      if ( matched == -1 ) continue;
      dx = dat.rpcLx[matched]-dat.expLx[i];

      h.hXYRecEndcapByDisk_[di]->Fill(dat.expGx[i], dat.expGy[i]);
      if ( doChamberMuography_ ) hRPCsItr->second->Fill(dat.expLx[i], dat.expLy[i]);
      h.hResEndcapByDisk_[di]->Fill(dx);
      h.hPullEndcapByDisk_[di]->Fill(dx/dat.rpcLex[matched]);

      h.hSubdetRecEndcapByDiskRingNoFid_[key]->Fill(binRoll);
      if ( dat.isInFiducial[i] ) h.hSubdetRecEndcapByDiskRing_[key]->Fill(binRoll);
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCPointAnalyzer);
