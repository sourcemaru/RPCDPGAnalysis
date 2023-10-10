# RPCDPGAnalysis/NanoAODTnP

## Recipes
### Setup
```sh
CMSSW_VERSION=CMSSW_13_3_0_pre2
SCRAM_ARCH=slc7_amd64_gcc11 cmsrel ${CMSSW_VERSION}
cd ./${CMSSW_VERSION}/src
cmsenv
git-cms-merge-topic slowmoyang:rpc-tnp-nanoaod_from-${CMSSW_VERSION}
git clone https://github.com/slowmoyang/RPCDPGAnalysis.git -b tnp-nanoaod
scram b
```

### Test
```sh
cmsRun \
    ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/test/muRPCTnPFlatTableProducer_cfg.py \
    inputFiles=root://cmsdcadisk.fnal.gov//dcache/uscmsdisk/store/data/Run2023D/Muon1/AOD/PromptReco-v2/000/371/225/00000/5f3efe8c-de70-43e0-a8c7-a532844ca6c3.root
```

### CRAB job
```sh
rpc-crab-submit.py \
    -p ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/test/muRPCTnPFlatTableProducer_cfg.py \
    -i ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/data/crab/run3.json \
    -s T3_CH_CERNBOX \
    -u <YOUR_CERN_USER_ACCOUNT> \
    -n tnp-nanoaod
```
