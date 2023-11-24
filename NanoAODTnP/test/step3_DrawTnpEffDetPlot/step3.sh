cmsenv

#python3 ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/scripts/rpc-tnp-plot-eff-detector.py -h
mkdir Run2022C
python3 ../../scripts/rpc-tnp-plot-eff-detector.py -i ../step2_FlattenTnPNanoAOD/Muon__Run2022C.root -g ../../data/geometry/run3.csv -s 13.6 -y 2022C -o ./Run2022C/
