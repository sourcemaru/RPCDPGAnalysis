cmsenv

REPO=${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP
TYPE=SingleMuon
ERA=Run2022B

rpc-tnp-plot-stat-detector.py -i ${REPO}/test/step2_FlattenTnPNanoAOD/${TYPE}__${ERA}.root \
    -g ${REPO}/data/geometry/run3.csv \
    -s 13.6 -y ${ERA:3:8} \
    -o ${REPO}/test/step3_DrawTnPPlot/StatDetUnit/${TYPE}__${ERA}/