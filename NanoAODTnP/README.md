# RPCDPGAnalysis/NanoAODTnP

## Recipes
### Setup
```sh
CMSSW_VERSION=CMSSW_13_3_0_pre2
SCRAM_ARCH=slc7_amd64_gcc11 cmsrel ${CMSSW_VERSION}
cd ./${CMSSW_VERSION}/src
cmsenv
git-cms-merge-topic slowmoyang:rpc-tnp-nanoaod_from-${CMSSW_VERSION}
git clone https://github.com/slowmoyang/RPCDPGAnalysis.git
scram b
```
