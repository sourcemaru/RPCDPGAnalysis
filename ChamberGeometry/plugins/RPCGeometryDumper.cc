#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/Framework/interface/Run.h"
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "Geometry/Records/interface/MuonGeometryRecord.h"
#include "Geometry/RPCGeometry/interface/RPCRollSpecs.h"
#include "Geometry/RPCGeometry/interface/RPCGeometry.h"
#include "Geometry/RPCGeometry/interface/RPCGeomServ.h"
#include "DataFormats/GeometrySurface/interface/TrapezoidalPlaneBounds.h"
#include "TrackingTools/GeomPropagators/interface/StraightLinePlaneCrossing.h"

#include <iostream>
#include <fstream>

using namespace std;

class RPCGeometryDumper : public edm::one::EDAnalyzer<edm::one::WatchRuns>
{
public:
  RPCGeometryDumper(const edm::ParameterSet& pset);
  ~RPCGeometryDumper() = default;
  void analyze(const edm::Event& event, const edm::EventSetup& eventSetup) override;
  void beginRun(const edm::Run& run, const edm::EventSetup& eventSetup) override;
  void endRun(const edm::Run& run, const edm::EventSetup&) override {};

private:
  const std::string outFileName_;

};

RPCGeometryDumper::RPCGeometryDumper(const edm::ParameterSet& pset):
  outFileName_(pset.getUntrackedParameter<std::string>("outFileName"))
{
}

void RPCGeometryDumper::beginRun(const edm::Run& run, const edm::EventSetup& eventSetup)
{
  // Set the roll names
  edm::ESHandle<RPCGeometry> rpcGeom;
  eventSetup.get<MuonGeometryRecord>().get(rpcGeom);

  std::ofstream fout(outFileName_);
  fout << "#RollName DetId Area x1 y1 z1 x2 y2 z2 x3 y3 z3 x4 y4 z4\n";
  for ( const RPCRoll* roll : rpcGeom->rolls() ) {
    const auto detId = roll->id();
    const string rollName = RPCGeomServ(detId).name();

    const auto& bound = roll->surface().bounds();
    const double h = bound.length(), w = bound.width();
    const double area = w*h;
    fout << rollName << ' ' << detId.rawId() << ' ' << area << ' ';
    if ( roll->isBarrel() ) {
      const auto gp1 = roll->toGlobal(LocalPoint(-w/2,+h/2,0));
      const auto gp2 = roll->toGlobal(LocalPoint(+w/2,+h/2,0));
      const auto gp3 = roll->toGlobal(LocalPoint(+w/2,-h/2,0));
      const auto gp4 = roll->toGlobal(LocalPoint(-w/2,-h/2,0));
      fout << gp1.x() << ' ' << gp1.y() << ' ' << gp1.z() << ' ';
      fout << gp2.x() << ' ' << gp2.y() << ' ' << gp2.z() << ' ';
      fout << gp3.x() << ' ' << gp3.y() << ' ' << gp3.z() << ' ';
      fout << gp4.x() << ' ' << gp4.y() << ' ' << gp4.z() << ' ';
    }
    else {
      const double w_dn = 2*bound.widthAtHalfLength() - w;
      const auto gp1 = roll->toGlobal(LocalPoint(-w/2,h/2,0));
      const auto gp2 = roll->toGlobal(LocalPoint(+w/2,h/2,0));
      const auto gp3 = roll->toGlobal(LocalPoint(+w_dn/2,-h/2,0));
      const auto gp4 = roll->toGlobal(LocalPoint(-w_dn/2,-h/2,0));
      fout << gp1.x() << ' ' << gp1.y() << ' ' << gp1.z() << ' ';
      fout << gp2.x() << ' ' << gp2.y() << ' ' << gp2.z() << ' ';
      fout << gp3.x() << ' ' << gp3.y() << ' ' << gp3.z() << ' ';
      fout << gp4.x() << ' ' << gp4.y() << ' ' << gp4.z() << ' ';
    }
    fout << endl;

  }
}

void RPCGeometryDumper::analyze(const edm::Event& event, const edm::EventSetup& eventSetup)
{
  return;
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(RPCGeometryDumper);
