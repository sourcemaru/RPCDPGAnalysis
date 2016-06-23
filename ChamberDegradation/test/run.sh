#!/bin/bash

cmsDriver.py step2 --conditions auto:run2_mc --era Run2_25ns --mc --magField 38T_PostLS1 \
  --step RAW2DIGI,L1Reco,RECO,EI,DQM -n -1 \
  --fileout step2.root --eventcontent RECOSIM \
  --filein /store/relval/CMSSW_8_0_10/RelValSingleMuPt100_UP15/GEN-SIM-DIGI-RAW-HLTDEBUG/80X_mcRun2_asymptotic_v14-v1/00000/42AC15DA-C528-E611-9790-0CC47A78A340.root \
  --customise RPCDPGAnalysis/ChamberDegradation/customise_cff.customise_DropMuonHits \
  --no_exec --python step2_cfg.py 

cmsRun step2_cfg.py
