#!/bin/bash
voms-proxy-init -voms cms
cmsenv
source /cvmfs/cms.cern.ch/common/crab-setup.sh

rpc-crab-submit.py \
    -p ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/test/step1_MakeTnPNanoAOD/muRPCTnPFlatTableProducer_cfg.py \
    -i ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/data/crab/run3.json \
    -s T3_CH_CERNBOX \
    -u ${USER} \
    -n tnp-nanoaod