#!/bin/bash

cmsDriver.py step2 --filein /store/relval/CMSSW_8_0_10/RelValSingleMuPt100_UP15/GEN-SIM-DIGI-RAW-HLTDEBUG/80X_mcRun2_asymptotic_v14-v1/00000/42AC15DA-C528-E611-9790-0CC47A78A340.root --fileout step2.root --eventcontent RECOSIM --mc --conditions auto:mc --step RAW2DIGI,L1Reco,RECO,EI,DQM --era Run2_25ns  --python step2_cfg.py -n -1 --no_exec --customise RPCDPGAnalysis/ChamberDegradation/customise_cff.customise_DropMuonHits

cmsRun step2_cfg.py
