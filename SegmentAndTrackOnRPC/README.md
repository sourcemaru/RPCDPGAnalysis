# RPC Chamber Efficiency using the TrackerMuon and Tag and Probe method

The RPCChamber efficiency can be measured using the matching information stored 
in the reco::Muon dataformat during the RPCMuon reconstruction.
Selection bias on the RPC chamber efficiency can be removed by requiring a TrackerMuon identification.

The RPCMuon reconstruction is based on the same algorithm of the TrackerMuons. 
The inner track is extrapolated onto the RPC rolls accounting
various effects in the detector using the SteppingHelixPropagator algorithm. 
The calculation requires hard computing resources, but once the
extrapolation is done and the matching to the recHits are done, the information 
are stored in the muon object. 

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

## Installation

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
```

There are cfg files to be tested. The configuration file for the tag and probe method can be found from 
RPCDPGAnalysis/SegmentAndTrackOnRPC/test. 

```
cd RPCDPGAnalysis/SegmentAndTrackOnRPC/test
cmsRun analyzeRPCwithTnP_cfg.py
```

Please modify the cfg file to change the input root file and JSON file.

The crab configuration files are also available to run 2016 datasets, modify the crabConfig.py file to process interested datasets.
Of course you have to change the output directory, lumiMask.

```
DATASET=SingleMuon ERA=Run2016B crab submit
```

To submit all dataset, you can do something like
```
for J in Run2016{B..E}; do
    DATASET=SingleMuon ERA=$J crab submit
done
```
Files will be stored in /eos/cms/store/user/YOURUSERNAME/RPCChamberEfficiency/SUBMITDATE\_1/ by default. Please modify the crabConfig.py if you want to set different destination.

When jobs are finished, simply add all output root files with hadd command. 
The x-y and z-phi view of efficiency plots can be obtained by running the drawMuographySummary.py.
Please modify this pyROOT script if necessary.

```
python -i drawMuongraphySummary.py
```

The roll efficiency distributions can be obtained using the drawEfficiency.py,

```
python -i drawEfficiency.py
```
