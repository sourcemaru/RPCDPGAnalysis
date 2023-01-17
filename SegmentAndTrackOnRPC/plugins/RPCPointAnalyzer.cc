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

#include "THnSparse.h"

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

private:
  edm::ESGetToken<RPCGeometry, MuonGeometryRecord> rpcGeomToken_;

  const edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_;
  std::vector< edm::EDGetTokenT<RPCRecHitCollection>> refHitTokens_;

  const double minMuonPt_, maxMuonAbsEta_;

  THnSparseF* hInfo_;
  enum {
    RUN=0, REGION,
    WHEEL, STATION, LAYER, SECTOR, ROLL, DISK, RING,
    ROLLNAME,
    ISMATCHED, ISFIDUCIAL,
    LX, LY, RESX, RESY, PULLX, PULLY,
    GX, GY, GZ, GPHI,
    CLS, BX,
    MASS, PT, ETA, PHI, TIME,
    NVARS
  };
};

RPCPointAnalyzer::RPCPointAnalyzer(const edm::ParameterSet& pset):
  rpcHitToken_(consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"))),
  minMuonPt_(pset.getParameter<double>("minMuonPt")),
  maxMuonAbsEta_(pset.getParameter<double>("maxMuonAbsEta"))
{
  rpcGeomToken_ = esConsumes<edm::Transition::BeginRun>();

  for ( auto x : pset.getParameter<std::vector<edm::InputTag>>("refPoints") ) {
    refHitTokens_.push_back(consumes<RPCRecHitCollection>(x));
  }

  hInfo_ = nullptr;
}

void RPCPointAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
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
    "cls", "bx",
    "mass", "pt", "eta", "phi", "time",
  };
  const char* varTitles[NVARS] = {
    "run",
    "region", "wheel", "station", "layer", "sector", "roll", "disk", "ring",
    "",
    "isMatched", "isFiducial",
    "Expected local x(cm)", "Expected local y(cm)", "Residual x(cm)", "Residual y(cm)", "Pull x(cm)", "Pull y(cm)",
    "Expected global x(cm)", "Expected global y(cm)", "Expected global z(cm)", "Expected global phi",
    "Cluster size", "Bunch crossing",
    "mass (GeV)", "pt (GeV)", "#eta", "#phi", "time (ns)",
  };
  int nbins[NVARS] = {
    1000000,
    3, 5, 5, 4, 12, 6, 5, 5,
    5000,
    2, 2,
    400, 400, 100, 100, 100, 100,
    1600, 1600, 2400, 360*3,
    10, 13,
    120, 20, 10, 24, 250,
  };
  double xmins[NVARS] = {
    0,
    -1, -2.5, 0, 0, 1, 0, 0, 0,
    0,
    0, 0,
    -200, -200, -50, -50, -5, -5,
    -800, -800, -1200, -3.14159265,
    0, -6.5,
    60, 0, -2.5, -3.14159265, 25*-5,
  };
  double xmaxs[NVARS] = {
    1000000,
    2, 2.5, 5, 3, 13, 6, 5, 5,
    5000,
    2, 2,
    200, 200, 50, 50, 5, 5,
    800, 800, 1200, 3.14159265,
    10, 6.5,
    120, 100, 2.5, 3.14159265, 25*5,
  };
  hInfo_ = fs->make<THnSparseF>("hInfo", "hInfo", NVARS, nbins, xmins, xmaxs);
  for ( int i=0; i<NVARS; ++i ) {
    hInfo_->GetAxis(i)->SetName(varNames[i]);
    hInfo_->GetAxis(i)->SetTitle(varTitles[i]);
  }

  // Set the roll names
  const auto& rpcGeom = eventSetup.getData(rpcGeomToken_);

  int i=0;
  for ( const RPCRoll* roll : rpcGeom.rolls() ) {
    const auto detId = roll->id();
    const string rollName = RPCGeomServ(detId).name();

    hInfo_->GetAxis(ROLLNAME)->SetBinLabel(++i, rollName.c_str());
  }
}

void RPCPointAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  using namespace std;

  double vars[NVARS];
  for ( int i=0; i<NVARS; ++i ) vars[i] = 0;
  vars[RUN] = event.id().run();

  // Default values
  vars[MASS] = 0;
  vars[PT] = vars[ETA] = vars[PHI] = 0; // FIXME: fill them in the next version

  const auto& rpcGeom = eventSetup.getData(rpcGeomToken_);

  edm::Handle<RPCRecHitCollection> rpcHitHandle;
  event.getByToken(rpcHitToken_, rpcHitHandle);

  // Collect extrapolated points from DT
  for ( auto refHitToken : refHitTokens_ ) {
    edm::Handle<RPCRecHitCollection> refHitHandle;
    event.getByToken(refHitToken, refHitHandle);
    for ( auto refItr = refHitHandle->begin(); refItr != refHitHandle->end(); ++refItr ) {
      const auto detId = refItr->rpcId();
      const auto roll = rpcGeom.roll(detId);
      const auto& bound = roll->surface().bounds();
      if ( !bound.inside(LocalPoint(refItr->localPosition().x(), refItr->localPosition().y(), 0)) ) continue;
      const auto gp = roll->toGlobal(refItr->localPosition());
      const auto lPos = rpcGeom.chamber(detId)->toLocal(gp);
      const auto lErr = refItr->localPositionError();
      const string rollName = RPCGeomServ(detId).name();
      const auto axis = hInfo_->GetAxis(ROLLNAME);

      vars[REGION] = vars[WHEEL] = vars[STATION] = vars[DISK] = vars[RING] = 0;
      vars[ISMATCHED] = vars[ISFIDUCIAL] = 0;
      vars[RESX] = vars[RESY] = vars[PULLX] = vars[PULLY] = 0;
      vars[CLS] = vars[BX] = 0;
      vars[TIME] = refItr->time();

      vars[LX] = lPos.x();
      vars[LY] = lPos.y();
      vars[GX] = gp.x();
      vars[GY] = gp.y();
      vars[GZ] = gp.z();
      vars[GPHI] = gp.phi();
      vars[SECTOR] = detId.sector();
      vars[LAYER] = detId.layer();
      vars[ROLL] = detId.roll();
      vars[ROLLNAME] = axis->FindBin(rollName.c_str());

      if ( detId.region() == 0 ) {
        vars[REGION] = 0;
        vars[WHEEL] = detId.ring();
        vars[STATION] = detId.station();

        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= bound.width()/2-8 );
        vars[ISFIDUCIAL] = isInFiducial;

        // Find best-matching RPCRecHit
        auto rpcHitRange = rpcHitHandle->get(detId);
        if ( rpcHitRange.first != rpcHitRange.second ) {
          auto matchedHit = rpcHitRange.first;
          double minDX = 1e9;
          for ( auto rpcHit = rpcHitRange.first; rpcHit != rpcHitRange.second; ++rpcHit ) {
            //const double dr = std::hypot(segment->localPosition().x(), segment->localPosition().y());
            const double dx = std::abs(rpcHit->localPosition().x()-lPos.x());
            if ( dx < minDX ) {
              matchedHit = rpcHit;
              minDX = dx;
            }
          }
          const auto hitLPos = matchedHit->localPosition();
          const auto hitLErr = matchedHit->localPositionError();

          vars[ISMATCHED] = 1;
          vars[RESX] = hitLPos.x()-lPos.x();
          vars[RESY] = hitLPos.y()-lPos.y();
          vars[PULLX] = (hitLPos.x()-lPos.x())/std::sqrt(hitLErr.xx()+lErr.xx());
          vars[PULLY] = (hitLPos.y()-lPos.y())/std::sqrt(hitLErr.yy()+lErr.yy());
          vars[CLS] = matchedHit->clusterSize();
          vars[BX] = matchedHit->BunchX();
        }
      }
      else {
        vars[REGION] = detId.region();
        vars[DISK] = detId.station();
        vars[RING] = detId.ring();

        const double wT = bound.width(), w0 = bound.widthAtHalfLength();
        const double slope = (wT-w0)/bound.length();
        const double w2AtY = slope*lPos.y() + w0/2;
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= w2AtY-8 );
        vars[ISFIDUCIAL] = isInFiducial;

        // Find best-matching RPCRecHit
        auto rpcHitRange = rpcHitHandle->get(detId);
        if ( rpcHitRange.first != rpcHitRange.second ) {
          auto matchedHit = rpcHitRange.first;
          double minDX = 1e9;
          for ( auto hit = rpcHitRange.first; hit != rpcHitRange.second; ++hit ) {
            //const double dr = std::hypot(hit->localPosition().x(), hit->localPosition().y());
            const double dx = std::abs(hit->localPosition().x()-lPos.x());
            if ( dx < minDX ) {
              matchedHit = hit;
              minDX = dx;
            }
          }
          const auto hitLPos = matchedHit->localPosition();
          const auto hitLErr = matchedHit->localPositionError();

          vars[ISMATCHED] = 1;
          vars[RESX] = hitLPos.x()-lPos.x();
          vars[RESY] = hitLPos.y()-lPos.y();
          vars[PULLX] = (hitLPos.x()-lPos.x())/std::sqrt(hitLErr.xx()+lErr.xx());
          vars[PULLY] = (hitLPos.y()-lPos.y())/std::sqrt(hitLErr.yy()+lErr.yy());
          vars[CLS] = matchedHit->clusterSize();
          vars[BX] = matchedHit->BunchX();
        }
      }
      hInfo_->Fill(vars);
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCPointAnalyzer);
