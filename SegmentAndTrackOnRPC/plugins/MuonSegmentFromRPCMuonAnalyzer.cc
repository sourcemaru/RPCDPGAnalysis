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
#include "THnSparse.h"

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

private:
  const edm::EDGetTokenT<DTRecSegment4DCollection> dtSegmentToken_;
  const edm::EDGetTokenT<CSCSegmentCollection> cscSegmentToken_;
  //const edm::EDGetTokenT<reco::VertexCollection> vertexToken_;
  const edm::EDGetTokenT<reco::MuonCollection> muonToken_;

  const double minMuonPt_, maxMuonAbsEta_;

  THnSparseF* hInfo_;
  enum {
    RUN=0, REGION,
    WHEEL, STATION, SECTOR, ROLL, DISK, RING, TRSECTOR,
    //ROLLNAME,
    ISMATCHED, ISFIDUCIAL,
    LX, LY, RESX, RESY, PULLX, PULLY,
    GX, GY, GZ, GPHI,
    MASS, PT, ETA, PHI,
    NVARS
  };

};

MuonSegmentFromRPCMuonAnalyzer::MuonSegmentFromRPCMuonAnalyzer(const edm::ParameterSet& pset):
  dtSegmentToken_(consumes<DTRecSegment4DCollection>(pset.getParameter<edm::InputTag>("dtSegments"))),
  cscSegmentToken_(consumes<CSCSegmentCollection>(pset.getParameter<edm::InputTag>("cscSegments"))),
  //vertexToken_(consumes<reco::VertexCollection>(pset.getParameter<edm::InputTag>("vertex"))),
  muonToken_(consumes<reco::MuonCollection>(pset.getParameter<edm::InputTag>("muons"))),
  minMuonPt_(pset.getParameter<double>("minMuonPt")),
  maxMuonAbsEta_(pset.getParameter<double>("maxMuonAbsEta"))
{
  hInfo_ = 0;
}

void MuonSegmentFromRPCMuonAnalyzer::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  if ( hInfo_ ) return;

  usesResource("TFileService");
  edm::Service<TFileService> fs;

  const char* varNames[NVARS] = {
    "run",
    "region", "wheel", "station", "sector", "roll", "disk", "ring", "trigsector",
    //"rollName",
    "isMatched", "isFiducial",
    "lX", "lY", "resX", "resY", "pullX", "pullY",
    "gX", "gY", "gZ", "gPhi",
    "mass", "pt", "eta", "phi",
  };
  const char* varTitles[NVARS] = {
    "run",
    "region", "wheel", "station", "sector", "roll", "disk", "ring", "trigsector",
    //"",
    "isMatched", "isFiducial",
    "Expected local x(cm)", "Expected local y(cm)", "Residual x(cm)", "Residual y(cm)", "Pull x(cm)", "Pull y(cm)",
    "Expected global x(cm)", "Expected global y(cm)", "Expected global z(cm)", "Expected global phi",
    "mass (GeV)", "pt (GeV)", "#eta", "#phi",
  };
  int nbins[NVARS] = {
    1000000,
    3, 5, 5, 12, 6, 9, 5, 36,
    //5000,
    2, 2,
    400, 400, 100, 100, 100, 100,
    1600, 1600, 2400, 360*3,
    120, 20, 10, 24,
  };
  double xmins[NVARS] = {
    0,
    -1, -2.5, 0, 1, 0, 0, 0, 1,
    //0,
    0, 0,
    -200, -200, -50, -50, -5, -5,
    -800, -800, -1200, -3.14159265,
    60, 0, -2.5, -3.14159265,
  };
  double xmaxs[NVARS] = {
    1000000,
    2, 2.5, 5, 13, 6, 5, 5, 37,
    //5000,
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

}

void MuonSegmentFromRPCMuonAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  using namespace std;

  double vars[NVARS];
  for ( int i=0; i<NVARS; ++i ) vars[i] = 0;
  vars[RUN] = event.id().run();

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
    if ( mu.track()->originalAlgo() == reco::TrackBase::muonSeededStepOutIn ) continue; // To avoid bias from muon seeded one

    vars[PT] = pt;
    vars[ETA] = mu.eta();
    vars[PHI] = mu.phi();

    for ( auto match : mu.matches() ) {
      if ( match.detector() == 3 ) continue;

      vars[REGION] = vars[WHEEL] = vars[DISK] = vars[RING] = vars[TRSECTOR] = 0;
      vars[ISMATCHED] = vars[ISFIDUCIAL] = 0;
      vars[RESX] = vars[RESY] = vars[PULLX] = vars[PULLY] = 0;

      const LocalPoint lPos(match.x, match.y, 0);
      if ( match.detector() == 1 ) { // DT matches
        const DTChamber* ch = dtGeom->chamber(match.id);
        if ( !ch->surface().bounds().inside(lPos) ) continue;
        const auto gp = ch->toGlobal(lPos);

        const DTChamberId dtId(match.id);
        vars[REGION] = 0;
        vars[LX] = lPos.x();
        vars[LY] = lPos.y();
        vars[GX] = gp.x();
        vars[GY] = gp.y();
        vars[GZ] = gp.z();
        vars[GPHI] = gp.phi();
        vars[WHEEL] = dtId.wheel();
        vars[STATION] = dtId.station();
        vars[SECTOR] = dtId.sector();

        const auto& bound = ch->surface().bounds();
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and 
                                   std::abs(lPos.x()) <= bound.width()/2-8 );
        vars[ISFIDUCIAL] = isInFiducial;

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

        vars[ISMATCHED] = 1;
        vars[RESX] = segLPos.x()-match.x;
        vars[RESY] = segLPos.y()-match.y;
        vars[PULLX] = (segLPos.x()-match.x)/std::sqrt(segLErr.xx()+match.xErr*match.xErr);
        vars[PULLY] = (segLPos.y()-match.y)/std::sqrt(segLErr.yy()+match.yErr*match.yErr);
      }
      else if ( match.detector() == 2 ) { // CSC matches
        const CSCChamber* ch = cscGeom->chamber(match.id);
        if ( !ch->surface().bounds().inside(lPos) ) continue;
        const auto gp = ch->toGlobal(lPos);

        const CSCDetId cscId(match.id);
        vars[REGION] = cscId.endcap();
        vars[LX] = lPos.x();
        vars[LY] = lPos.y();
        vars[GX] = gp.x();
        vars[GY] = gp.y();
        vars[GZ] = gp.z();
        vars[GPHI] = gp.phi();
        vars[DISK] = cscId.station();
        vars[RING] = cscId.ring();
        vars[TRSECTOR] = cscId.triggerSector();

        const auto& bound = ch->surface().bounds();
        const double wT = bound.width(), w0 = bound.widthAtHalfLength();
        const double slope = (wT-w0)/bound.length();
        const double w2AtY = slope*lPos.y() + w0/2;
        const bool isInFiducial = (std::abs(lPos.y()) <= bound.length()/2-8 and
                                   std::abs(lPos.x()) <= w2AtY-8);
        vars[ISFIDUCIAL] = isInFiducial;

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

        vars[ISMATCHED] = 1;
        vars[RESX] = segLPos.x()-match.x;
        vars[RESY] = segLPos.y()-match.y;
        vars[PULLX] = (segLPos.x()-match.x)/std::sqrt(segLErr.xx()+match.xErr*match.xErr);
        vars[PULLY] = (segLPos.y()-match.y)/std::sqrt(segLErr.yy()+match.yErr*match.yErr);
      }
      hInfo_->Fill(vars);
    }
  }
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(MuonSegmentFromRPCMuonAnalyzer);
