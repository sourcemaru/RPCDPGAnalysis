#include "RPCDPGAnalysis/SegmentAndTrackOnRPC/interface/RPCPointData.h"
#include <vector>

namespace dummy {

struct dictionary {
  RPCBarrelData rbd;
  RPCEndcapData red;
  std::vector<RPCBarrelData> vrbd;
  std::vector<RPCEndcapData> vred;
};

}
