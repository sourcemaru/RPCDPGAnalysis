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
#include "THnSparse.h"

#include <iostream>
#include <cmath>
#include <vector>

using namespace std;

class MuonHitFromTrackerMuonAnalyzer : public edm::one::EDAnalyzer<edm::one::WatchRuns, edm::one::SharedResources>
{
public:
  MuonHitFromTrackerMuonAnalyzer(const edm::ParameterSet& pset);
  virtual ~MuonHitFromTrackerMuonAnalyzer() {};
  void analyze(const edm::Event& event, const edm::EventSetup& eventSetup) override;
  void beginRun(const edm::Run& run, const edm::EventSetup& eventSetup) override;
  void endRun(const edm::Run& run, const edm::EventSetup&) override {};

private:
  const edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_;
  //const edm::EDGetTokenT<reco::VertexCollection> vertexToken_;
  const edm::EDGetTokenT<reco::MuonCollection> muonToken_;
  const edm::EDGetTokenT<double> tpMassToken_;

  const double minMuonPt_, maxMuonAbsEta_;

  THnSparseF* hInfo_;
  enum {
    RUN=0, REGION,
    WHEEL, STATION, LAYER, SECTOR, ROLL, DISK, RING,
    ROLLNAME,
    ISMATCHED, ISFIDUCIAL,
    LX, LY, RESX, RESY, PULLX, PULLY,
    GX, GY, GZ, GPHI,
    MASS, PT, ETA, PHI,
    NVARS
  };
};

MuonHitFromTrackerMuonAnalyzer::MuonHitFromTrackerMuonAnalyzer(const edm::ParameterSet& pset):
  rpcHitToken_(consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"))),
  //vertexToken_(consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"))),
  muonToken_(consumes<reco::MuonCollection>(pset.getParameter<edm::InputTag>("muons"))),
  tpMassToken_(consumes<double>(pset.getParameter<edm::InputTag>("tpMass"))),
  minMuonPt_(pset.getParameter<double>("minMuonPt")),
  maxMuonAbsEta_(pset.getParameter<double>("maxMuonAbsEta"))
{
  hInfo_ = 0;
}

void MuonHitFromTrackerMuonAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  if ( hInfo_ ) return; 

  usesResource("TFileService");
  edm::Service<TFileService> fs;

  const char* varNames[NVARS] = {
    "run",
    "region", "wheel", "station", "layer", "sector", "roll", "disk", "ring",
    "rollName",
    "isMatched", "isFiducial",
    "lX", "lY", "resX", "resY", "pullX", "pullY",
    "gX", "gY", "gZ", "gPhi", 
    "mass", "pt", "eta", "phi",
  };
  const char* varTitles[NVARS] = {
    "run",
    "region", "wheel", "station", "layer", "sector", "roll", "disk", "ring",
    "",
    "isMatched", "isFiducial",
    "Expected local x(cm)", "Expected local y(cm)", "Residual x(cm)", "Residual y(cm)", "Pull x(cm)", "Pull y(cm)",
    "Expected global x(cm)", "Expected global y(cm)", "Expected global z(cm)", "Expected global phi",
    "mass (GeV)", "pt (GeV)", "#eta", "#phi",
  };
  int nbins[NVARS] = {
    1000000,
    2, 5, 5, 4, 12, 6, 9, 5,
    5000,
    2, 2,
    400, 400, 100, 100, 100, 100,
    1600, 1600, 2400, 360*3,
    120, 20, 10, 24,
  };
  double xmins[NVARS] = {
    0,
    0, -2.5, 0, 0, 1, 0, -4.5, 0,
    0,
    0, 0,
    -200, -200, -50, -50, -5, -5,
    -800, -800, -1200, -3.14159265,
    60, 0, -2.5, -3.14159265,
  };
  double xmaxs[NVARS] = {
    1000000,
    2, 2.5, 5, 3, 13, 6, 4.5, 5,
    5000,
    2, 2,
    200, 200, 50, 50, 5, 5,
    800, 800, 1200, 3.14159265,
    120, 100, 2.5, 3.14159265,
  };
  hInfo_ = fs->make<THnSparseF>("hInfo", "hInfo", NVARS, nbins, xmins, xmaxs);
  for ( int i=0; i<NVARS; ++i ) {
    hInfo_->GetAxis(i)->SetName(varNames[i]);
    hInfo_->GetAxis(i)->SetTitle(varTitles[i]);
  }

  // Set the roll names
  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  int i=0;
  for ( const RPCRoll* roll : rpcGeom->rolls() ) {
    const auto detId = roll->id();
    const string rollName = RPCGeomServ(detId).name();

    hInfo_->GetAxis(ROLLNAME)->SetBinLabel(++i, rollName.c_str());
  }
}

void MuonHitFromTrackerMuonAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  using namespace std;

  double vars[NVARS];
  for ( int i=0; i<NVARS; ++i ) vars[i] = 0;
  vars[RUN] = event.id().run();

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

  edm::Handle<double> tpMassHandle;
  if ( event.getByToken(tpMassToken_, tpMassHandle) ) {
    vars[MASS] = *tpMassHandle;
  }

  for ( int i=0, n=muonHandle->size(); i<n; ++i ) {
    const auto& mu = muonHandle->at(i);
    const double pt = mu.pt();

    // Basic cuts
    if ( pt < minMuonPt_ or std::abs(mu.eta()) > maxMuonAbsEta_ ) continue;
    if ( !mu.isTrackerMuon() ) continue;
    if ( !muon::isGoodMuon(mu, muon::TMOneStationLoose) ) continue;
    if ( mu.track()->originalAlgo() == reco::TrackBase::muonSeededStepOutIn ) continue; // To avoid bias from muon seeded one

    vars[PT] = pt;
    vars[ETA] = mu.eta();
    vars[PHI] = mu.phi();

    for ( auto match : mu.matches() ) {
      if ( match.detector() != 3 ) continue;

      const LocalPoint lPos(match.x, match.y, 0);
      const RPCRoll* roll = rpcGeom->roll(match.id);
      if ( !roll->surface().bounds().inside(lPos) ) continue;

      const auto gp = roll->toGlobal(lPos);
      const RPCDetId detId(match.id);
      const string rollName = RPCGeomServ(detId).name();
      const auto axis = hInfo_->GetAxis(ROLLNAME);

      vars[LX] = lPos.x();
      vars[LY] = lPos.y();
      vars[GX] = gp.x();
      vars[GY] = gp.y();
      vars[GZ] = gp.z();
      vars[GPHI] = gp.phi();
      vars[STATION] = detId.station();
      vars[SECTOR] = detId.sector();
      vars[LAYER] = detId.layer();
      vars[ROLLNAME] = axis->FindBin(rollName.c_str());

      if ( detId.region() == 0 ) {
        vars[REGION] = 0;
        vars[WHEEL] = detId.ring();

        const auto& bound = roll->surface().bounds();
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= bound.width()/2-8 );
        vars[ISFIDUCIAL] = isInFiducial;

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

        vars[ISMATCHED] = 1;
        vars[RESX] = hitLPos.x()-match.x;
        vars[RESY] = hitLPos.y()-match.y;
        vars[PULLX] = (hitLPos.x()-match.x)/std::sqrt(hitLErr.xx()+match.xErr*match.xErr);
        vars[PULLY] = (hitLPos.y()-match.y)/std::sqrt(hitLErr.yy()+match.yErr*match.yErr);
      }
      else {
        vars[REGION] = 1;
        vars[DISK] = detId.region()*detId.station();
        vars[RING] = detId.ring();

        const auto& bound = roll->surface().bounds();
        const double wT = bound.width(), w0 = bound.widthAtHalfLength();
        const double slope = (wT-w0)/bound.length();
        const double w2AtY = slope*lPos.y() + w0/2;
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= w2AtY-8 );
        vars[ISFIDUCIAL] = isInFiducial;

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

        vars[ISMATCHED] = 1;
        vars[RESX] = hitLPos.x()-match.x;
        vars[RESY] = hitLPos.y()-match.y;
        vars[PULLX] = (hitLPos.x()-match.x)/std::sqrt(hitLErr.xx()+match.xErr*match.xErr);
        vars[PULLY] = (hitLPos.y()-match.y)/std::sqrt(hitLErr.yy()+match.yErr*match.yErr);
      }
    }
    hInfo_->Fill(vars);
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(MuonHitFromTrackerMuonAnalyzer);
