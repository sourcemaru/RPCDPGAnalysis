#!/bin/bash
cmsenv
for dir in ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/test/step2_FlattenTnPNanoAOD/*
do
    if [ -d ${dir} ]
    then
        hadd $(basename ${dir}).root ${dir}/result/*.root
    fi
done