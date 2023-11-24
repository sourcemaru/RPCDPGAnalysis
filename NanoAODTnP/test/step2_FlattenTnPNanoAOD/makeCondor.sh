#!/bin/bash

cmsenv

#### Need Customize!!!
DATA_TYPE=$1
PERIOD=$2
CERT_FILE=$3

DATA_PATH=/eos/user/j/joshin/RPC_STORE/tnp-nanoaod/*/${DATA_TYPE}/*${DATA_TYPE}__${PERIOD}*/*/*/
CWD=${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/test/step2_FlattenTnPNanoAOD/

## make period, output, error dir
mkdir ${CWD}${DATA_TYPE}__${PERIOD}
mkdir ${CWD}${DATA_TYPE}__${PERIOD}/result


## make condor.dat (output.root data list)
touch ${CWD}${DATA_TYPE}__${PERIOD}/condor.dat
ls ${DATA_PATH} >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.dat

## make condor.sh
touch ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
chmod +x ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo '#!/bin/bash'                                                                                       >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo 'cd '${CMSSW_BASE}'/src'                                                                            >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo 'source /cvmfs/cms.cern.ch/cmsset_default.sh'                                                       >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo 'eval `scram runtime -sh`'                                                                          >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo 'python3 ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/scripts/rpc-tnp-flatten-nanoaod.py \'          >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo '    -i $1 \'                                                                                       >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo '    -c ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/data/cert/'${CERT_FILE}' \'                     >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo '    -g ${CMSSW_BASE}/src/RPCDPGAnalysis/NanoAODTnP/data/geometry/run3.csv \'                       >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh
echo '    -o '${CWD}${DATA_TYPE}__${PERIOD}'/result/flatten_$(basename $1)'                              >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sh


## make condor.sub
touch ${CWD}${DATA_TYPE}__${PERIOD}/condor.sub
echo 'executable = condor.sh'                    >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sub
echo 'arguments  = '${DATA_PATH}'$(FILE)'        >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sub
echo 'log        = condor.log'                   >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sub
echo 'queue FILE from condor.dat'                >> ${CWD}${DATA_TYPE}__${PERIOD}/condor.sub


## submit condor.sub
cd ${CWD}${DATA_TYPE}__${PERIOD}
condor_submit condor.sub
