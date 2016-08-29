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

#include "DataFormats/DTRecHit/interface/DTRecSegment4D.h"
#include "DataFormats/DTRecHit/interface/DTRecSegment4DCollection.h"
#include "DataFormats/CSCRecHit/interface/CSCSegment.h"
#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"
#include "Geometry/DTGeometry/interface/DTGeometry.h"
#include "Geometry/CSCGeometry/interface/CSCGeometry.h"
#include "DataFormats/GeometrySurface/interface/TrapezoidalPlaneBounds.h"

#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class MuonSegmentFromRPCMuonAnalyzer : public edm::one::EDAnalyzer<edm::one::WatchRuns, edm::one::SharedResources>
{
public:
  MuonSegmentFromRPCMuonAnalyzer(const edm::ParameterSet& pset);
  virtual ~MuonSegmentFromRPCMuonAnalyzer() {};
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
  const edm::EDGetTokenT<DTRecSegment4DCollection> dtSegmentToken_;
  const edm::EDGetTokenT<CSCSegmentCollection> cscSegmentToken_;
  //const edm::EDGetTokenT<reco::VertexCollection> vertexToken_;
  const edm::EDGetTokenT<reco::MuonCollection> muonToken_;

  const bool doHistByRun_;
  const double minMuonPt_, maxMuonAbsEta_;

  std::map<unsigned int, Hists> hists_;
};

MuonSegmentFromRPCMuonAnalyzer::MuonSegmentFromRPCMuonAnalyzer(const edm::ParameterSet& pset):
  dtSegmentToken_(consumes<DTRecSegment4DCollection>(pset.getParameter<edm::InputTag>("dtSegments"))),
  cscSegmentToken_(consumes<CSCSegmentCollection>(pset.getParameter<edm::InputTag>("cscSegments"))),
  //vertexToken_(consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"))),
  muonToken_(consumes<reco::MuonCollection>(pset.getParameter<edm::InputTag>("muons"))),
  doHistByRun_(pset.getUntrackedParameter<bool>("doHistByRun")),
  minMuonPt_(pset.getParameter<double>("minMuonPt")),
  maxMuonAbsEta_(pset.getParameter<double>("maxMuonAbsEta"))
{
}

void MuonSegmentFromRPCMuonAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  usesResource("TFileService");
  edm::Service<TFileService> fs;

  const int runNumber = doHistByRun_ ? run.id().run() : 0;
  if ( hists_.count(runNumber) == 0 ) {
    auto dir = fs->mkdir(Form("Run%06d", runNumber));
    auto& h = hists_[runNumber] = Hists();

    // Book histograms for the DTs
    edm::ESHandle<DTGeometry> dtGeom;
    eventSetup.get<MuonGeometryRecord>().get(dtGeom);

    for ( const DTChamber* ch : dtGeom->chambers() ) {
      const auto detId = ch->id();
      const int wh = detId.wheel();
      const int st = detId.station();
      //const int se = detId.sector();

      const string whStr = Form("Wheel%d", wh);
      auto dir_wheel = dir.mkdir(whStr);
      if ( !h.hXYExpBarrelByWheel_[wh] ) {
        h.hXYExpBarrelByWheel_[wh] = dir_wheel.make<TH2F>("hXYExp", ("Expected points "+whStr+";X (cm);Y (cm)").c_str(), 1600, -800, 800, 1600, -800, 800);
        h.hXYRecBarrelByWheel_[wh] = dir_wheel.make<TH2F>("hXYRec", ("Expected points matched to Segment "+whStr+";X (cm);Y (cm)").c_str(), 1600, -800, 800, 1600, -800, 800);
        h.hResXBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hResX", ("X Residual "+whStr+";#DeltaX (cm)").c_str(), 500, -50, 50);
        h.hResYBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hResY", ("Y Residual "+whStr+";#DeltaY (cm)").c_str(), 500, -50, 50);
        h.hPullXBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hPullX", ("X Pull "+whStr+";Pull X").c_str(), 200, -10, 10);
        h.hPullYBarrelByWheel_[wh] = dir_wheel.make<TH1F>("hPullY", ("Y Pull "+whStr+";Pull Y").c_str(), 200, -10, 10);
      }

      if ( !h.hZPhiExpBarrelByStation_[st] ) {
        const string suffix = Form("Station%d", st);
        h.hZPhiExpBarrelByStation_[st] = dir.make<TH2F>(
          ("hZPhiExpBarrel_"+suffix).c_str(), ("Expected points in Barrel "+suffix+";Z (cm);#phi").c_str(),
          1400, -700, 700, 360*3, -3.14159265, 3.14159265);
        h.hZPhiRecBarrelByStation_[st] = dir.make<TH2F>(
          ("hZPhiRecBarrel_"+suffix).c_str(), ("Expected Points matched to Segment in Barrel "+suffix+";Z (cm);#phi").c_str(),
          1400, -700, 700, 360*3, -3.14159265, 3.14159265);
        h.hResXBarrelByStation_[st] = dir.make<TH1F>(
          ("hResXBarrel_"+suffix).c_str(), ("X Residual in Barrel "+suffix+";#DeltaX (cm)").c_str(), 500, -50, 50);
        h.hResYBarrelByStation_[st] = dir.make<TH1F>(
          ("hResYBarrel_"+suffix).c_str(), ("Y Residual in Barrel "+suffix+";#DeltaY (cm)").c_str(), 500, -50, 50);
        h.hPullXBarrelByStation_[st] = dir.make<TH1F>(
          ("hPullXBarrel_"+suffix).c_str(), ("X Pull in Barrel "+suffix+";Pull X").c_str(), 200, -10, 10);
        h.hPullYBarrelByStation_[st] = dir.make<TH1F>(
          ("hPullYBarrel_"+suffix).c_str(), ("Y Pull in Barrel "+suffix+";Pull Y").c_str(), 200, -10, 10);
      }

      const int key = wh+10*st;
      if ( !h.hSubdetExpBarrelByWheelStation_[key] ) {
        const string suffix = Form("Station%d", st);
        h.hSubdetExpBarrelByWheelStation_[key] = dir_wheel.make<TH1F>(
          ("hSubdetExpBarrel_"+suffix).c_str(), ("Expected points in Barrel "+whStr+" "+suffix+";Sector").c_str(), 12, 1, 13);
        h.hSubdetRecBarrelByWheelStation_[key] = dir_wheel.make<TH1F>(
          ("hSubdetRecBarrel_"+suffix).c_str(), ("Expected points matched to Segment in Barrel "+whStr+" "+suffix+";Sector").c_str(), 12, 1, 13);
        h.hSubdetExpBarrelByWheelStationNoFid_[key] = dir_wheel.make<TH1F>(
          ("hSubdetExpBarrel_"+suffix+"_NoFid").c_str(),
          ("Expected points in Barrel "+whStr+" "+suffix+" without fiducial cut;Sector").c_str(), 12, 1, 13);
        h.hSubdetRecBarrelByWheelStationNoFid_[key] = dir_wheel.make<TH1F>(
          ("hSubdetRecBarrel_"+suffix+"_NoFid").c_str(),
          ("Expected points matched to Segment in Barrel "+whStr+" "+suffix+" without fiducial cut;Sector").c_str(), 12, 1, 13);
      }
    } // Booking DT chambers

    // Book histograms for the CSCs
    edm::ESHandle<CSCGeometry> cscGeom;
    eventSetup.get<MuonGeometryRecord>().get(cscGeom);

    for ( const CSCChamber* ch : cscGeom->chambers() ) {
      const auto detId = ch->id();
      const int di = detId.zendcap()*detId.station(); // Signed disk number
      const int ri = detId.ring();

      const std::string diStr = Form("Disk%d", di);
      auto dir_disk = dir.mkdir(diStr);

      if ( !h.hXYExpEndcapByDisk_[di] ) {
        h.hXYExpEndcapByDisk_[di] = dir_disk.make<TH2F>("hXYExp", ("Expected points "+diStr+";X (cm);Y (cm)").c_str(), 1600, -800, 800, 1600, -800, 800);
        h.hXYRecEndcapByDisk_[di] = dir_disk.make<TH2F>("hXYRec", ("Expected points matched to Segment "+diStr+";X (cm);Y (cm)").c_str(), 1600, -800, 800, 1600, -800, 800);
        h.hResXEndcapByDisk_[di] = dir_disk.make<TH1F>("hResX", ("X Residual "+diStr+";#DeltaX (cm)").c_str(), 500, -50, 50);
        h.hResYEndcapByDisk_[di] = dir_disk.make<TH1F>("hResY", ("Y Residual "+diStr+";#DeltaY (cm)").c_str(), 500, -50, 50);
        h.hPullXEndcapByDisk_[di] = dir_disk.make<TH1F>("hPullX", ("X Pull "+diStr+";Pull X").c_str(), 200, -10, 10);
        h.hPullYEndcapByDisk_[di] = dir_disk.make<TH1F>("hPullY", ("Y Pull "+diStr+";Pull Y").c_str(), 200, -10, 10);
      }

      const int key = di+10*ri;
      if ( !h.hSubdetExpEndcapByDiskRing_[key] ) {
        const string suffix = Form("Ring%d", ri);
        h.hSubdetExpEndcapByDiskRing_[key] = dir_disk.make<TH1F>(
          ("hSubdetExpEndcap_"+suffix).c_str(), ("Expected points in Endcap "+diStr+" "+suffix+";Chamber").c_str(), 36, 1, 37);
        h.hSubdetRecEndcapByDiskRing_[key] = dir_disk.make<TH1F>(
          ("hSubdetRecEndcap_"+suffix).c_str(), ("Expected points matched to Segment in Endcap "+diStr+" "+suffix+";Chamber").c_str(), 36, 1, 37);
        h.hSubdetExpEndcapByDiskRingNoFid_[key] = dir_disk.make<TH1F>(
          ("hSubdetExpEndcap_"+suffix+"_NoFid").c_str(),
          ("Expected points in Endcap "+diStr+" "+suffix+" without fiducial cut;Chamber").c_str(), 36, 1, 37);
        h.hSubdetRecEndcapByDiskRingNoFid_[key] = dir_disk.make<TH1F>(
          ("hSubdetRecEndcap_"+suffix+"_NoFid").c_str(),
          ("Expected points matched to Segment in Endcap "+diStr+" "+suffix+" without fiducial cut;Chamber").c_str(), 36, 1, 37);
      }
    } // Booking CSC chambers
  }
}

void MuonSegmentFromRPCMuonAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  using namespace std;

  auto& h = hists_[doHistByRun_ ? event.id().run() : 0];

  edm::ESHandle<DTGeometry> dtGeom;
  eventSetup.get<MuonGeometryRecord>().get(dtGeom);

  edm::ESHandle<CSCGeometry> cscGeom;
  eventSetup.get<MuonGeometryRecord>().get(cscGeom);

  edm::Handle<DTRecSegment4DCollection> dtSegmentHandle;
  event.getByToken(dtSegmentToken_, dtSegmentHandle);

  edm::Handle<CSCSegmentCollection> cscSegmentHandle;
  event.getByToken(cscSegmentToken_, cscSegmentHandle);

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
    if ( !mu.isRPCMuon() ) continue;
    if ( !muon::isGoodMuon(mu, muon::RPCMuLoose) ) continue;

    for ( auto match : mu.matches() ) {
      if ( match.detector() == 3 ) continue;

      const LocalPoint lPos(match.x, match.y, 0);
      if ( match.detector() == 1 ) { // DT matches
        const DTChamber* ch = dtGeom->chamber(match.id);
        if ( !ch->surface().bounds().inside(lPos) ) continue;
        const auto gp = ch->toGlobal(lPos);

        const DTChamberId dtId(match.id);
        const int wh = dtId.wheel();
        const int st = dtId.station();

        const auto& bound = ch->surface().bounds();
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and 
                                   std::abs(lPos.x()) <= bound.width()/2-8 );

        h.hXYExpBarrelByWheel_[wh]->Fill(gp.x(), gp.y());
        h.hZPhiExpBarrelByStation_[st]->Fill(gp.z(), gp.phi());

        h.hSubdetExpBarrelByWheelStationNoFid_[wh+10*st]->Fill(dtId.sector());
        if ( isInFiducial) h.hSubdetExpBarrelByWheelStation_[wh+10*st]->Fill(dtId.sector());

        // Find best-matching DT segment
        auto dtSegmentRange = dtSegmentHandle->get(dtId);
        if ( dtSegmentRange.first == dtSegmentRange.second ) continue;

        auto matchedSegment = dtSegmentRange.first;
        double minDX = 1e9;
        for ( auto segment = dtSegmentRange.first; segment != dtSegmentRange.second; ++segment ) {
          //const double dr = std::hypot(segment->localPosition().x(), segment->localPosition().y());
          const double dx = std::abs(segment->localPosition().x()-match.x);
          if ( dx < minDX ) {
            matchedSegment = segment;
            minDX = dx;
          }
        }
        const auto segLPos = matchedSegment->localPosition();
        const auto segLErr = matchedSegment->localPositionError();
      
        h.hXYRecBarrelByWheel_[wh]->Fill(gp.x(), gp.y());
        h.hZPhiRecBarrelByStation_[st]->Fill(gp.z(), gp.phi());

        h.hResXBarrelByWheel_[wh]->Fill(segLPos.x()-match.x);
        h.hResYBarrelByWheel_[wh]->Fill(segLPos.y()-match.y);
        h.hPullXBarrelByWheel_[wh]->Fill((segLPos.x()-match.x)/std::sqrt(segLErr.xx()+match.xErr*match.xErr));
        h.hPullYBarrelByWheel_[wh]->Fill((segLPos.y()-match.y)/std::sqrt(segLErr.yy()+match.yErr*match.yErr));

        h.hResXBarrelByStation_[st]->Fill(segLPos.x()-match.x);
        h.hResYBarrelByStation_[st]->Fill(segLPos.y()-match.y);
        h.hPullXBarrelByStation_[st]->Fill((segLPos.x()-match.x)/std::sqrt(segLErr.xx()+match.xErr*match.xErr));
        h.hPullYBarrelByStation_[st]->Fill((segLPos.y()-match.y)/std::sqrt(segLErr.yy()+match.yErr*match.yErr));

        h.hSubdetRecBarrelByWheelStationNoFid_[wh+10*st]->Fill(dtId.sector());
        if ( isInFiducial ) h.hSubdetRecBarrelByWheelStation_[wh+10*st]->Fill(dtId.sector());
      }
      else if ( match.detector() == 2 ) { // CSC matches
        const CSCChamber* ch = cscGeom->chamber(match.id);
        if ( !ch->surface().bounds().inside(lPos) ) continue;
        const auto gp = ch->toGlobal(lPos);

        const CSCDetId cscId(match.id);
        const int di = cscId.zendcap()*cscId.station();
        const int ri = cscId.ring();
        const int key = di+10*ri;

        const auto& bound = ch->surface().bounds();
        const double wT = bound.width(), w0 = bound.widthAtHalfLength();
        const double slope = (wT-w0)/bound.length();
        const double w2AtY = slope*lPos.y() + w0/2;
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= w2AtY-8);

        h.hXYExpEndcapByDisk_[di]->Fill(gp.x(), gp.y());
        h.hSubdetExpEndcapByDiskRingNoFid_[key]->Fill(cscId.chamber());
        if ( isInFiducial ) h.hSubdetExpEndcapByDiskRing_[key]->Fill(cscId.chamber());

        // Find best-matching CSC segment
        auto cscSegmentRange = cscSegmentHandle->get(cscId);
        if ( cscSegmentRange.first == cscSegmentRange.second ) continue;

        auto matchedSegment = cscSegmentRange.first;
        double minDX = 1e9;
        for ( auto segment = cscSegmentRange.first; segment != cscSegmentRange.second; ++segment ) {
          //const double dr = std::hypot(segment->localPosition().x(), segment->localPosition().y());
          const double dx = std::abs(segment->localPosition().x()-match.x);
          if ( dx < minDX ) {
            matchedSegment = segment;
            minDX = dx;
          }
        }
        const auto segLPos = matchedSegment->localPosition();
        const auto segLErr = matchedSegment->localPositionError();

        h.hXYRecEndcapByDisk_[di]->Fill(gp.x(), gp.y());

        h.hResXEndcapByDisk_[di]->Fill(segLPos.x()-match.x);
        h.hResYEndcapByDisk_[di]->Fill(segLPos.y()-match.y);
        h.hPullXEndcapByDisk_[di]->Fill((segLPos.x()-match.x)/std::sqrt(segLErr.xx()+match.xErr*match.xErr));
        h.hPullYEndcapByDisk_[di]->Fill((segLPos.y()-match.y)/std::sqrt(segLErr.yy()+match.yErr*match.yErr));

        h.hSubdetRecEndcapByDiskRingNoFid_[key]->Fill(cscId.chamber());
        if ( isInFiducial ) h.hSubdetRecEndcapByDiskRing_[key]->Fill(cscId.chamber());
      }
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(MuonSegmentFromRPCMuonAnalyzer);
