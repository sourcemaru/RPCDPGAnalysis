* RPC Chamber Efficiency using the TrackerMuon

The RPCChamber efficiency can be measured using the TrackerMuon
and the matching information from the RPCMuon reconstruction.

The inner track is extrapolated onto the RPC rolls to reconstruct the RPCMuons
and the extrapolated points are examined to be matched to the RPCRecHits.
Even though there was no matched RPCRecHits, the matching information
including the local position of the extrapolated points are not discarded at this moment.

The muon candidate is kept in the event if it passes TrackerMuon ID or RPCMuon ID.
The TrackerMuon and RPCMuon IDs are independent each other, therefore requiring TrackerMuon
ID does not bias the matching of the RPCs. Since we already have the extrapolation information
to the RPC layers in the muon objects, we can define the denominator of the RPC roll
efficiency without selection bias.

The track extrapolation is done during the standard muon reconstruction step
and there is no need to do this step again by the analyzers. Even more, this matching
information is a part of the AOD dataformat. DQM modules can be written without any
complicated routines to measure the RPC efficiencies.

----

* Installation

The PR for the "Chamber Surface" is not sent for the 80X release. This have to be merged
to get correct per-chamber muography plots. The RPCPointProducer in the CMSSW is little bit
outdated, this should be updated as well (under development yet, but this is not crucial).

```
cmsrel CMSSW_8_0_10
cd CMSSW_8_0_10/src
cmsenv
git-cms-init
git-cms-merge-topic jhgoh:RPCChamberSurface80X
git-cms-merge-topic jhgoh:PortingRPCPointProducerFromRPCDPG
git clone https://:@gitlab.cern.ch:8443/jhgoh/RPCDPGAnalysis.git
scram b -j8
cd RPCDPGAnalysis/SegmentAndTrackOnRPC/test
cmsRun rpcPointFromMuons_cfg.py
```

The crab configuration files are also available to run 2016 datasets,

```
DATASET=Run2016B crab submit
DATASET=Run2016C crab submit
DATASET=Run2016D crab submit
DATASET=Run2016E crab submit
```

----
