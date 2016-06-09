#ifndef RPCDPGAnalysis_SegmentAndTrackOnRPC_RPCPointData_H
#define RPCDPGAnalysis_SegmentAndTrackOnRPC_RPCPointData_H

#include "DataFormats/MuonDetId/interface/RPCDetId.h"
#include <vector>

struct RPCBarrelData
{
  RPCBarrelData() {};
  RPCBarrelData(const RPCDetId id)
  {
    if ( id.region() != 0 ) return;
    wheel = id.ring();
    sector = id.sector();
    station = id.station();
    layer = id.layer();
    roll = id.roll();
  };

  char wheel, sector, station, layer, roll;
  std::vector<float> rpcLx, rpcLex, expLx, expLy;
  std::vector<float> rpcGx, rpcGy, rpcGz;
  std::vector<float> expGx, expGy, expGz; 
};

struct RPCEndcapData
{
  RPCEndcapData() {};
  RPCEndcapData(const RPCDetId id)
  {
    if ( id.region() == 0 ) return;
    disk = id.station();
    sector = id.sector();
    ring = id.ring();
    layer = id.layer();
    roll = id.roll();
  };

  char disk, sector, ring, layer, roll;
  std::vector<float> rpcLx, rpcLex, expLx, expLy;
  std::vector<float> rpcGx, rpcGy, rpcGz;
  std::vector<float> expGx, expGy, expGz; 
};

#endif
