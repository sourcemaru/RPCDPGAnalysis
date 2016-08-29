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
#include "DataFormats/MuonReco/interface/MuonSelectors.h"

#include "DataFormats/RPCRecHit/interface/RPCRecHit.h"
#include "DataFormats/RPCRecHit/interface/RPCRecHitCollection.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"
#include "Geometry/RPCGeometry/interface/RPCGeometry.h"
#include "Geometry/RPCGeometry/interface/RPCGeomServ.h"
#include "DataFormats/GeometrySurface/interface/TrapezoidalPlaneBounds.h"

#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class MuonHitFromTrackerMuonAnalyzer : public edm::one::EDAnalyzer<edm::one::WatchRuns, edm::one::SharedResources>
{
public:
  MuonHitFromTrackerMuonAnalyzer(const edm::ParameterSet& pset);
  virtual ~MuonHitFromTrackerMuonAnalyzer() {};
  void beginRun(const edm::Run& run, const edm::EventSetup& eventSetup) override;
  void endRun(const edm::Run&, const edm::EventSetup&) override {};
  void analyze(const edm::Event& event, const edm::EventSetup& eventSetup) override;

  struct Hists {
    std::vector<TH1F*> hFloatVars_;

    TH2F* hXYExpBarrel_, * hXYExpEndcapP_, * hXYExpEndcapM_;
    TH2F* hXYRecBarrel_, * hXYRecEndcapP_, * hXYRecEndcapM_;

    std::map<int, TH2F*> hXYExpBarrelByWheel_, hXYRecBarrelByWheel_;
    std::map<int, TH2F*> hZPhiExpBarrelByStation_, hZPhiRecBarrelByStation_;
    std::map<int, TH2F*> hXYExpEndcapByDisk_, hXYRecEndcapByDisk_;

    std::map<int, TH1F*> hResXBarrelByWheel_, hResXBarrelByStation_, hResXEndcapByDisk_;;
    std::map<int, TH1F*> hPullXBarrelByWheel_, hPullXBarrelByStation_, hPullXEndcapByDisk_;;
    std::map<int, TH1F*> hResYBarrelByWheel_, hResYBarrelByStation_, hResYEndcapByDisk_;;
    std::map<int, TH1F*> hPullYBarrelByWheel_, hPullYBarrelByStation_, hPullYEndcapByDisk_;;

    std::map<int, TH1F*> hSubdetExpBarrelByWheelStation_, hSubdetRecBarrelByWheelStation_;
    std::map<int, TH1F*> hSubdetExpEndcapByDiskRing_, hSubdetRecEndcapByDiskRing_;
    std::map<int, TH1F*> hSubdetExpBarrelByWheelStationNoFid_, hSubdetRecBarrelByWheelStationNoFid_;
    std::map<int, TH1F*> hSubdetExpEndcapByDiskRingNoFid_, hSubdetRecEndcapByDiskRingNoFid_;
  };

private:
  const edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_;
  //const edm::EDGetTokenT<reco::VertexCollection> vertexToken_;
  const edm::EDGetTokenT<reco::MuonCollection> muonToken_;

  const bool doHistByRun_;
  const double minMuonPt_, maxMuonAbsEta_;

  std::map<unsigned int, Hists> hists_;
};

MuonHitFromTrackerMuonAnalyzer::MuonHitFromTrackerMuonAnalyzer(const edm::ParameterSet& pset):
  rpcHitToken_(consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"))),
  //vertexToken_(consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"))),
  muonToken_(consumes<reco::MuonCollection>(pset.getParameter<edm::InputTag>("muons"))),
  doHistByRun_(pset.getUntrackedParameter<bool>("doHistByRun")),
  minMuonPt_(pset.getParameter<double>("minMuonPt")),
  maxMuonAbsEta_(pset.getParameter<double>("maxMuonAbsEta"))
{
}

void MuonHitFromTrackerMuonAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  usesResource("TFileService");
  edm::Service<TFileService> fs;

  const int runNumber = doHistByRun_ ? run.id().run() : 0;
  if ( hists_.count(runNumber) == 0 ) {
    auto dir = fs->mkdir(Form("Run%06d", runNumber));
    auto& h = hists_[runNumber] = Hists();

    // Book histograms for the DTs
    edm::ESHandle<RPCGeometry> rpcGeom;
    eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

    std::map<int, vector<string> > barrelBinLabels, endcapBinLabels;

    for ( const RPCChamber* ch : rpcGeom->chambers() ) {
      const auto detId = ch->id();
      const auto rolls = ch->rolls();
      const int nRoll = rolls.size();
      const std::string chName = RPCGeomServ(detId).chambername();
      if ( detId.region() == 0 ) {
        const int wh = detId.ring();
        const int st = detId.station();
        const int la = detId.layer();

        const string whStr = Form("Wheel%d", wh);
        auto dir_wheel = dir.mkdir(whStr);
        if ( !h.hXYExpBarrelByWheel_[wh] ) {
          h.hXYExpBarrelByWheel_[wh] = dir_wheel.make<TH2F>("hXYExp", "Expected points;X (cm);Y (cm)", 800, -800, 800, 800, -800, 800);
          h.hXYRecBarrelByWheel_[wh] = dir_wheel.make<TH2F>("hXYRec", "Expected points matched to RecHit;X (cm);Y (cm)", 800, -800, 800, 800, -800, 800);
          h.hResXBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hResX", "X Residual#DeltaX (cm)", 500, -50, 50);
          h.hResYBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hResY", "Y Residual#DeltaY (cm)", 500, -50, 50);
          h.hPullXBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hPullX", "X Pull;Pull X", 200, -10, 10);
          h.hPullYBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hPullY", "Y Pull;Pull Y", 200, -10, 10);
        }

        const int stla = st*10+la;
        if ( !h.hZPhiExpBarrelByStation_[stla] ) {
          const string suffix = Form("Station%d_Layer%d", st, la);
          h.hZPhiExpBarrelByStation_[stla] = dir.make<TH2F>(
            ("hZPhiExpBarrel_"+suffix).c_str(), ("Expected points in "+suffix+";Z (cm);#phi").c_str(),
            700, -700, 700, 720, -3.14159265, 3.14159265);
          h.hZPhiRecBarrelByStation_[stla] = dir.make<TH2F>(
            ("hZPhiRecBarrel_"+suffix).c_str(), ("Expected Points matched to RecHit in Barrel "+suffix+";Z (cm);#phi").c_str(),
            700, -700, 700, 720, -3.14159265, 3.14159265);
          h.hResXBarrelByStation_[stla] = dir.make<TH1F>(
            ("hResXBarrel_"+suffix).c_str(), ("X Residual in "+suffix+";#DeltaX (cm)").c_str(), 500, -50, 50);
          h.hResYBarrelByStation_[stla] = dir.make<TH1F>(
            ("hResYBarrel_"+suffix).c_str(), ("Y Residual in Barrel "+suffix+";#DeltaY (cm)").c_str(), 500, -50, 50);
          h.hPullXBarrelByStation_[stla] = dir.make<TH1F>(
            ("hPullXBarrel_"+suffix).c_str(), ("X Pull in Barrel "+suffix+";Pull X").c_str(), 200, -10, 10);
          h.hPullYBarrelByStation_[stla] = dir.make<TH1F>(
            ("hPullYBarrel_"+suffix).c_str(), ("Y Pull in Barrel "+suffix+";Pull Y").c_str(), 200, -10, 10);
        }

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
        const int di = detId.region()*detId.station(); // Signed disk number
        const int ri = detId.ring();

        const std::string diStr = Form("Disk%d", di);
        auto dir_disk = dir.mkdir(diStr);

        if ( !h.hXYExpEndcapByDisk_[di] ) {
          h.hXYExpEndcapByDisk_[di] = dir_disk.make<TH2F>("hXYExp", "Expected points;X (cm);Y (cm)", 800, -800, 800, 800, -800, 800);
          h.hXYRecEndcapByDisk_[di] = dir_disk.make<TH2F>("hXYRec", "Expected points matched to RecHit;X (cm);Y (cm)", 800, -800, 800, 800, -800, 800);
          h.hResXEndcapByDisk_[di] = dir_disk.make<TH1F>("hResX", "X Residual;#DeltaX (cm)", 500, -50, 50);
          h.hResYEndcapByDisk_[di] = dir_disk.make<TH1F>("hResY", "Y Residual;#DeltaY (cm)", 500, -50, 50);
          h.hPullXEndcapByDisk_[di] = dir_disk.make<TH1F>("hPullX", "X Pull;Pull X", 200, -10, 10);
          h.hPullYEndcapByDisk_[di] = dir_disk.make<TH1F>("hPullY", "Y Pull;Pull Y", 200, -10, 10);
        }

        const int key = di+10*ri;
        if ( !h.hSubdetExpEndcapByDiskRing_[key] ) {
          const string suffix = Form("Ring%d", ri);
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
      } // Booking endcaps
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

void MuonHitFromTrackerMuonAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  using namespace std;

  auto& h = hists_[doHistByRun_ ? event.id().run() : 0];

  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  edm::Handle<RPCRecHitCollection> rpcHitHandle;
  event.getByToken(rpcHitToken_, rpcHitHandle);

  //edm::Handle<reco::VertexCollection> vertexHandle;
  //event.getByToken(vertexToken_, vertexHandle);
  //b_nPV = vertexHandle->size();
  //const reco::Vertex pv = vertexHandle->at(0);

  edm::Handle<reco::MuonCollection> muonHandle;
  event.getByToken(muonToken_, muonHandle);

  for ( int i=0, n=muonHandle->size(); i<n; ++i ) {
    const auto& mu = muonHandle->at(i);
    const double pt = mu.pt();
  
    // Basic cuts
    if ( pt < minMuonPt_ or std::abs(mu.eta()) > maxMuonAbsEta_ ) continue;
    if ( !mu.isTrackerMuon() ) continue;
    if ( !muon::isGoodMuon(mu, muon::TMOneStationLoose) ) continue;

    for ( auto match : mu.matches() ) {
      if ( match.detector() != 3 ) continue;

      const LocalPoint lPos(match.x, match.y, 0);
      const RPCRoll* roll = rpcGeom->roll(match.id);
      if ( !roll->surface().bounds().inside(lPos) ) continue;

      const auto gp = roll->toGlobal(lPos);
      const RPCDetId detId(match.id);
      const string rollName = RPCGeomServ(detId).name();

      if ( detId.region() == 0 ) {
        const int wh = detId.ring();
        const int st = detId.station();
        const int la = detId.layer();

        const int stla = st*10+la;
        const int key = wh+10*st+100*la;

        const auto& bound = roll->surface().bounds();
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and 
                                   std::abs(lPos.x()) <= bound.width()/2-8 );

        h.hXYExpBarrelByWheel_[wh]->Fill(gp.x(), gp.y());
        h.hZPhiExpBarrelByStation_[stla]->Fill(gp.z(), gp.phi());
        h.hSubdetExpBarrelByWheelStationNoFid_[key]->Fill(h.hSubdetExpBarrelByWheelStationNoFid_[key]->GetXaxis()->FindBin(rollName.c_str()));
        if ( isInFiducial ) h.hSubdetExpBarrelByWheelStation_[key]->Fill(h.hSubdetExpBarrelByWheelStation_[key]->GetXaxis()->FindBin(rollName.c_str()));

        // Find best-matching RPCRecHit
        auto rpcHitRange = rpcHitHandle->get(detId);
        if ( rpcHitRange.first == rpcHitRange.second ) continue;

        auto matchedHit = rpcHitRange.first;
        double minDX = 1e9;
        for ( auto rpcHit = rpcHitRange.first; rpcHit != rpcHitRange.second; ++rpcHit ) {
          //const double dr = std::hypot(segment->localPosition().x(), segment->localPosition().y());
          const double dx = std::abs(rpcHit->localPosition().x()-match.x);
          if ( dx < minDX ) {
            matchedHit = rpcHit;
            minDX = dx;
          }
        }
        const auto hitLPos = matchedHit->localPosition();
        const auto hitLErr = matchedHit->localPositionError();
        h.hXYRecBarrelByWheel_[wh]->Fill(gp.x(), gp.y());
        h.hZPhiRecBarrelByStation_[stla]->Fill(gp.z(), gp.phi());

        h.hResXBarrelByWheel_[wh]->Fill(hitLPos.x()-match.x);
        h.hResYBarrelByWheel_[wh]->Fill(hitLPos.y()-match.y);
        h.hPullXBarrelByWheel_[wh]->Fill((hitLPos.x()-match.x)/std::sqrt(hitLErr.xx()+match.xErr*match.xErr));
        h.hPullYBarrelByWheel_[wh]->Fill((hitLPos.y()-match.y)/std::sqrt(hitLErr.yy()+match.yErr*match.yErr));

        h.hResXBarrelByStation_[stla]->Fill(hitLPos.x()-match.x);
        h.hResYBarrelByStation_[stla]->Fill(hitLPos.y()-match.y);
        h.hPullXBarrelByStation_[stla]->Fill((hitLPos.x()-match.x)/std::sqrt(hitLErr.xx()+match.xErr*match.xErr));
        h.hPullYBarrelByStation_[stla]->Fill((hitLPos.y()-match.y)/std::sqrt(hitLErr.yy()+match.yErr*match.yErr));

        h.hSubdetRecBarrelByWheelStationNoFid_[key]->Fill(h.hSubdetRecBarrelByWheelStation_[key]->GetXaxis()->FindBin(rollName.c_str()));
        if ( isInFiducial ) h.hSubdetRecBarrelByWheelStation_[key]->Fill(h.hSubdetRecBarrelByWheelStation_[key]->GetXaxis()->FindBin(rollName.c_str()));
      }
      else {
        const int di = detId.region()*detId.station();
        const int ri = detId.ring();

        const int key = di+10*ri;

        const auto& bound = roll->surface().bounds();
        const double wT = bound.width(), w0 = bound.widthAtHalfLength();
        const double slope = (wT-w0)/bound.length();
        const double w2AtY = slope*lPos.y() + w0/2;
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= w2AtY-8 );

        h.hXYExpEndcapByDisk_[di]->Fill(gp.x(), gp.y());
        h.hSubdetExpEndcapByDiskRingNoFid_[key]->Fill(h.hSubdetExpEndcapByDiskRing_[key]->GetXaxis()->FindBin(rollName.c_str()));
        if ( isInFiducial ) h.hSubdetExpEndcapByDiskRing_[key]->Fill(h.hSubdetExpEndcapByDiskRing_[key]->GetXaxis()->FindBin(rollName.c_str()));

        // Find best-matching RPCRecHit
        auto rpcHitRange = rpcHitHandle->get(detId);
        if ( rpcHitRange.first == rpcHitRange.second ) continue;

        auto matchedHit = rpcHitRange.first;
        double minDX = 1e9;
        for ( auto hit = rpcHitRange.first; hit != rpcHitRange.second; ++hit ) {
          //const double dr = std::hypot(hit->localPosition().x(), hit->localPosition().y());
          const double dx = std::abs(hit->localPosition().x()-match.x);
          if ( dx < minDX ) {
            matchedHit = hit;
            minDX = dx;
          }
        }
        const auto hitLPos = matchedHit->localPosition();
        const auto hitLErr = matchedHit->localPositionError();
        h.hXYRecEndcapByDisk_[di]->Fill(gp.x(), gp.y());

        h.hResXEndcapByDisk_[di]->Fill(hitLPos.x()-match.x);
        h.hResYEndcapByDisk_[di]->Fill(hitLPos.y()-match.y);
        h.hPullXEndcapByDisk_[di]->Fill((hitLPos.x()-match.x)/std::sqrt(hitLErr.xx()+match.xErr*match.xErr));
        h.hPullYEndcapByDisk_[di]->Fill((hitLPos.y()-match.y)/std::sqrt(hitLErr.yy()+match.yErr*match.yErr));

        h.hSubdetRecEndcapByDiskRingNoFid_[key]->Fill(h.hSubdetRecEndcapByDiskRing_[key]->GetXaxis()->FindBin(rollName.c_str()));
        if ( isInFiducial ) h.hSubdetRecEndcapByDiskRing_[key]->Fill(h.hSubdetRecEndcapByDiskRing_[key]->GetXaxis()->FindBin(rollName.c_str()));
      }
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(MuonHitFromTrackerMuonAnalyzer);
