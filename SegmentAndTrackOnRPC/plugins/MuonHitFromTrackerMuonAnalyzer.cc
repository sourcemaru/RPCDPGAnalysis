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

#include "DataFormats/CSCRecHit/interface/CSCSegmentCollection.h"
#include "DataFormats/DTRecHit/interface/DTRecSegment4DCollection.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"
#include "Geometry/RPCGeometry/interface/RPCGeometry.h"
#include "Geometry/RPCGeometry/interface/RPCGeomServ.h"
#include "Geometry/DTGeometry/interface/DTGeometry.h"
#include "Geometry/CSCGeometry/interface/CSCGeometry.h"
#include "DataFormats/GeometrySurface/interface/TrapezoidalPlaneBounds.h"
#include "TrackingTools/GeomPropagators/interface/StraightLinePlaneCrossing.h"

#include "DataFormats/Math/interface/deltaPhi.h"
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
  const bool doHybrid_;
  const edm::EDGetTokenT<RPCRecHitCollection> rpcHitToken_;
  const edm::EDGetTokenT<DTRecSegment4DCollection> dtSegmentToken_;
  const edm::EDGetTokenT<CSCSegmentCollection> cscSegmentToken_;
  //const edm::EDGetTokenT<reco::VertexCollection> vertexToken_;
  const edm::EDGetTokenT<reco::MuonCollection> muonToken_;
  const edm::EDGetTokenT<double> tpMassToken_;

  const double minMuonPt_, maxMuonAbsEta_;
  enum class ResonanceType { Z0, Jpsi, Upsilon } resonanceType_;

  THnSparseF* hInfo_;
  enum {
    RUN=0,
    REGION, WHEEL, STATION, LAYER, SEGMENT, ROLL, DISK, RING,
    ROLLNAME,
    ISMATCHED, ISFIDUCIAL, HASNEARBYSGMT,
    LX, LY, RESX, RESY, PULLX, PULLY,
    DXDZ, DYDZ,
    GX, GY, GZ, GPHI,
    CLS, BX,
    MASS, PT, ETA, PHI, TIME,
    NVARS
  };
};

MuonHitFromTrackerMuonAnalyzer::MuonHitFromTrackerMuonAnalyzer(const edm::ParameterSet& pset):
  doHybrid_(pset.getUntrackedParameter<bool>("doHybrid")),
  rpcHitToken_(consumes<RPCRecHitCollection>(pset.getParameter<edm::InputTag>("rpcRecHits"))),
  dtSegmentToken_(consumes<DTRecSegment4DCollection>(pset.getParameter<edm::InputTag>("dtSegments"))),
  cscSegmentToken_(consumes<CSCSegmentCollection>(pset.getParameter<edm::InputTag>("cscSegments"))),
  //vertexToken_(consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"))),
  muonToken_(consumes<reco::MuonCollection>(pset.getParameter<edm::InputTag>("muons"))),
  tpMassToken_(consumes<double>(pset.getParameter<edm::InputTag>("tpMass"))),
  minMuonPt_(pset.getParameter<double>("minMuonPt")),
  maxMuonAbsEta_(pset.getParameter<double>("maxMuonAbsEta"))
{
  std::string s = pset.getParameter<string>("resonanceType");
  std::transform(s.begin(), s.end(), s.begin(), ::toupper);
  if ( s == "Z" or s == "Z0" ) resonanceType_ = ResonanceType::Z0;
  else if ( s == "JPSI" ) resonanceType_ = ResonanceType::Jpsi;
  else if ( s == "UPSILON" ) resonanceType_ = ResonanceType::Upsilon;

  hInfo_ = nullptr;
}

void MuonHitFromTrackerMuonAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  if ( hInfo_ ) return; 

  usesResource("TFileService");
  edm::Service<TFileService> fs;

  const char* varNames[NVARS] = {
    "run",
    "region", "wheel", "station", "layer", "segment", "roll", "disk", "ring",
    "rollName",
    "isMatched", "isFiducial", "hasNearbySgmt",
    "lX", "lY", "resX", "resY", "pullX", "pullY",
    "dxdz", "dydz",
    "gX", "gY", "gZ", "gPhi",
    "cls", "bx",
    "mass", "pt", "eta", "phi", "time",
  };
  const char* varTitles[NVARS] = {
    "run",
    "region", "wheel", "station", "layer", "segment", "roll", "disk", "ring",
    "",
    "isMatched", "isFiducial", "hasNearbySgmt",
    "Local x (cm)", "Local y (cm)", "Residual x (cm)", "Residual y (cm)", "Pull x", "Pull y",
    "Incidence angle dx/dz", "Incidence angle dy/dz",
    "x (cm)", "y (cm)", "z (cm)", "#phi (radian)",
    "Cluster size", "Bunch crossing",
    "Mass (GeV)", "p_{T} (GeV)", "#eta", "#phi (radian)", "time (ns)",
  };
  int nbins[NVARS] = {
    1000000, //RUN
    3, 5, 5, 3, 49, 6, 5, 5, //REGION, WHEEL, STATION, LAYER, SEGMENT, ROLL, DISK, RING
    5000, //ROLLNAME
    2, 2, 2, //ISMATCHED, ISFIDUCIAL, HASNEARBYSGMT
    400, 400, 120, 120, 100, 100, //LX, LY, RESX, RESY, PULLX, PULLY
    100, 100, //DXDZ, DYDZ
    3200, 3200, 4800, 100, // GX, GY, GZ, GPHI
    10, 13, //CLS, BX
    120, 50, 20, 24, 250 //MASS, PT, ETA, PHI, TIME
  };
  double xmins[NVARS] = {
    0, //RUN
    -1, -2.5, 0, 0, 0, 0, 0, 0, //REGION, WHEEL, STATION, LAYER, SEGMENT, ROLL, DISK, RING
    1, //ROLLNAME
    0, 0, 0, //ISMATCHED, ISFIDUCIAL, HASNEARBYSGMT
    -200, -200, -20, -20, -5, -5, //LX, LY, RESX, RESY, PULLX, PULLY
    -1.5, -1.5, //DXDZ, DYDZ
    -800, -800, -1200, -3.14159265, //GX, GY, GZ, GPHI
    0, -6.5, //CLS, BX
    60, 0, -2.5, -3.14159265, 25*-5 //MASS, PT, ETA, PHI, TIME
  };
  double xmaxs[NVARS] = {
    1000000, //RUN
    2, 2.5, 5, 3, 49, 6, 5, 5, //REGION, WHEEL, STATION, LAYER, SEGMENT, ROLL, DISK, RING
    5001, //ROLLNAME
    2, 2, 2, //ISMATCHED, ISFIDUCIAL, HASNEARBYSGMT
    200, 200, 20, 20, 5, 5, //LX, LY, RESX, RESY, PULLX, PULLY
    1.5, 1.5, //DXDZ, DYDZ
    800, 800, 1200, 3.14159265, //GX, GY, GZ, GPHI
    10, 6.5, //CLS, BX
    120, 100, 2.5, 3.14159265, 25*5 //MASS, PT, ETA, PHI, TIME
  };
  // Modify binning for the Onia's
  if ( resonanceType_ == ResonanceType::Jpsi ) {
    nbins[MASS] = 100;
    xmins[MASS] = 2.95;
    xmaxs[MASS] = 3.25;
  }
  else if ( resonanceType_ == ResonanceType::Upsilon ) {
    nbins[MASS] = 120;
    xmins[MASS] = 8.5;
    xmaxs[MASS] = 11.5;
  }

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
    vars[TIME] = mu.time().timeAtIpInOut;

    std::map<DetId, std::pair<LocalPoint, LocalVector>> segMatches;
    if ( doHybrid_ ) {
      for ( auto match : mu.matches() ) {
        // select one nearest to the track extrapolation...
        if ( match.detector() == MuonSubdetId::DT ) {
          auto range = dtSegmentHandle->get(match.id);
          auto bestSegment = range.second;
          double bestDR = 1e9;
          for ( auto segment = range.first; segment != range.second; ++segment ) {
            if ( !segment->hasPhi() or !segment->hasZed() ) continue;
            const double dR = hypot(match.x-segment->localPosition().x(), match.y-segment->localPosition().y());
            if ( bestSegment == range.second or dR < bestDR ) {
              bestDR = dR;
              bestSegment = segment;
            }
          }
          if ( bestSegment != range.second ) {
            segMatches.insert(std::make_pair(match.id, std::make_pair(bestSegment->localPosition(), bestSegment->localDirection())));
          }
        }
        else if ( match.detector() == MuonSubdetId::CSC ) {
          auto range = cscSegmentHandle->get(match.id);
          auto bestSegment = range.second;
          double bestDR = 1e9;
          for ( auto segment = range.first; segment != range.second; ++segment ) {
            const double dR = hypot(match.x-segment->localPosition().x(), match.y-segment->localPosition().y());
            if ( bestSegment == range.second or dR < bestDR ) {
              bestDR = dR;
              bestSegment = segment;
            }
          }
          if ( bestSegment != range.second ) {
            segMatches.insert(std::make_pair(match.id, std::make_pair(bestSegment->localPosition(), bestSegment->localDirection())));
          }
        }
      }
    }

    for ( auto match : mu.matches() ) {
      if ( match.detector() != MuonSubdetId::RPC ) continue;

      bool hasNearbySgmt = false;

      const RPCDetId rpcId(match.id);
      const RPCRoll* roll = rpcGeom->roll(match.id);
      const auto& bound = roll->surface().bounds();
      const GlobalPoint gPos0 = roll->toGlobal(LocalPoint(0,0,0));

      LocalPoint lPos(match.x, match.y, 0);
      // replace local postion by the segment extrapolation if available.
      std::map<double, std::pair<GlobalPoint, GlobalVector> > segMatchesNearRPC;
      for ( auto segMatchItr = segMatches.begin(); segMatchItr != segMatches.end(); ++segMatchItr ) {
        auto detId = segMatchItr->first;
        if ( detId.det() != DetId::Muon ) continue; // this never happens

        auto segPos = segMatchItr->second.first;
        auto segDir = segMatchItr->second.second;

        if ( detId.subdetId() == MuonSubdetId::DT ) {
          const DTChamberId dtId(detId);
          const auto dtChamber = dtGeom->chamber(detId);
          //if ( dtId.station() != rpcId.station() or dtId.wheel() != rpcId.ring() ) continue;
          if ( dtId.station() != rpcId.station() ) continue;
          const GlobalPoint gRefPos0 = dtChamber->toGlobal(LocalPoint(0,0,0));
          const double dphi = std::abs(deltaPhi(gPos0.barePhi(), gRefPos0.barePhi()));
          auto posDir = std::make_pair(dtChamber->toGlobal(segPos), dtChamber->toGlobal(segDir));
          //if ( dphi < 3.14/8 ) segMatchesNearRPC.insert(std::make_pair(dphi, posDir));
          segMatchesNearRPC.insert(std::make_pair(dphi, posDir));
        }
        else if ( detId.subdetId() == MuonSubdetId::CSC ) {
          const CSCDetId cscId(detId);
          const auto cscChamber = cscGeom->chamber(cscId);
          if ( cscId.zendcap()*cscId.station() != rpcId.region()*rpcId.station() ) continue;
          const GlobalPoint gRefPos0 = cscChamber->toGlobal(LocalPoint(0,0,0));
          const double dphi = std::abs(deltaPhi(gPos0.barePhi(), gRefPos0.barePhi()));
          auto posDir = std::make_pair(cscChamber->toGlobal(segPos), cscChamber->toGlobal(segDir));
          //if ( dphi < 3.14/8 ) segMatchesNearRPC.insert(std::make_pair(dphi, posDir));
          segMatchesNearRPC.insert(std::make_pair(dphi, posDir));
        }
      }
      if ( !segMatchesNearRPC.empty() ) {
        auto segMatch = segMatchesNearRPC.begin();
        const StraightLinePlaneCrossing segPlane(segMatch->second.first.basicVector(),
                                                 segMatch->second.second.basicVector(), anyDirection);
        auto extResult = segPlane.position(roll->surface());
        if ( extResult.first ) {
          lPos = roll->toLocal(GlobalPoint(extResult.second));
          hasNearbySgmt = true;
        }
      }

      if ( !bound.inside(lPos) ) continue;

      const double match_x0 = roll->centreOfStrip(roll->strip(lPos)).x();

      const auto gp = roll->toGlobal(lPos);
      const RPCDetId detId(match.id);
      const string rollName = RPCGeomServ(detId).name();
      const auto axis = hInfo_->GetAxis(ROLLNAME);

      vars[REGION] = vars[WHEEL] = vars[STATION] = vars[DISK] = vars[RING] = 0;
      vars[ISMATCHED] = vars[ISFIDUCIAL] = 0;
      vars[HASNEARBYSGMT] = hasNearbySgmt;
      vars[RESX] = vars[RESY] = vars[PULLX] = vars[PULLY] = 0;
      vars[CLS] = vars[BX] = 0;

      vars[LX] = lPos.x();
      vars[LY] = lPos.y();
      vars[GX] = gp.x();
      vars[GY] = gp.y();
      vars[GZ] = gp.z();
      vars[GPHI] = gp.phi();
      vars[LAYER] = detId.layer();
      vars[ROLL] = detId.roll();
      vars[ROLLNAME] = axis->FindBin(rollName.c_str());
      vars[DXDZ] = match.dXdZ;
      vars[DYDZ] = match.dYdZ;

      if ( detId.region() == 0 ) {
        vars[REGION] = 0;
        vars[WHEEL] = detId.ring();
        vars[STATION] = detId.station();
        vars[SEGMENT] = (detId.sector()-1)*4 + detId.subsector();

        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= bound.width()/2-8 );
        vars[ISFIDUCIAL] = isInFiducial;

        // Find best-matching RPCRecHit
        auto rpcHitRange = rpcHitHandle->get(detId);
        if ( rpcHitRange.first != rpcHitRange.second ) {
          auto matchedHit = rpcHitRange.first;
          double minDX = 1e9;
          for ( auto rpcHit = rpcHitRange.first; rpcHit != rpcHitRange.second; ++rpcHit ) {
            const double dx = std::abs(rpcHit->localPosition().x()-match_x0);
            if ( dx < minDX ) {
              matchedHit = rpcHit;
              minDX = dx;
            }
          }
          const auto hitLPos = matchedHit->localPosition();
          const auto hitLErr = matchedHit->localPositionError();

          vars[ISMATCHED] = 1;
          const auto dp = hitLPos - lPos;
          vars[RESX] = dp.x();
          vars[RESY] = dp.y();
          vars[PULLX] = dp.x()/std::sqrt(hitLErr.xx());
          vars[PULLY] = dp.y()/std::sqrt(hitLErr.yy());
          vars[CLS] = matchedHit->clusterSize();
          vars[BX] = matchedHit->BunchX();
        }
      }
      else {
        vars[REGION] = detId.region();
        vars[DISK] = detId.station();
        vars[RING] = detId.ring();
        vars[SEGMENT] = (detId.sector()-1)*6 + detId.subsector();

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
            const double dx = std::abs(hit->localPosition().x()-match_x0);
            if ( dx < minDX ) {
              matchedHit = hit;
              minDX = dx;
            }
          }
          const auto hitLPos = matchedHit->localPosition();
          const auto hitLErr = matchedHit->localPositionError();

          vars[ISMATCHED] = 1;
          const auto dp = hitLPos - lPos;
          vars[RESX] = dp.x();
          vars[RESY] = dp.y();
          vars[PULLX] = dp.x()/std::sqrt(hitLErr.xx());
          vars[PULLY] = dp.y()/std::sqrt(hitLErr.yy());
          vars[CLS] = matchedHit->clusterSize();
          vars[BX] = matchedHit->BunchX();
        }
      }
      hInfo_->Fill(vars);
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(MuonHitFromTrackerMuonAnalyzer);
