#!/usr/bin/env python

from ROOT import *
import os, sys
gStyle.SetOptStat(0)

sys.path.append("%s/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/python" % os.environ["CMSSW_BASE"])
from ProjectTHnSparse import *

f = TFile(sys.argv[1])
hInfo = f.Get("rpcExt/hInfo")
hSel = THnSparseSelector(hInfo)

if not os.path.exists("hists"): os.mkdir("hists")
f = TFile("hists/efficiency_%s" % (os.path.basename(sys.argv[1])), "RECREATE")

commonSel = {
    #'run':(315257,315420),
    #'run':(315420,315420),
    #'run':(315488,315488),
    'run':(315488,315974),
}

## Overall efficiency distribution
plots = {
    'Barrel_detId':[['rollName'], {'region':(0,0), 'isFiducial':(1,1)}],
    'EndcapP_detId':[['rollName'], {'region':(1,1), 'isFiducial':(1,1)}],
    'EndcapN_detId':[['rollName'], {'region':(-1,-1), 'isFiducial':(1,1)}],
}

for name, (variables, ranges) in plots.iteritems():
    subranges = ranges.copy()
    subranges.update(commonSel)
    print subranges
    xVar = variables[0]
    hDen = hSel.Project1D(xVar, subranges, suffix=name+"_Den", copyAxisLabel=True)
    subranges.update({'isMatched':(1,1)})
    hNum = hSel.Project1D(xVar, subranges, suffix=name+"_Num", copyAxislabel=True)
    hDen.Write()
    hNum.Write()

## Effciency map on global coordinates
plots = {
    'Barrel_ZPhi':[['gZ', 'gPhi'], {'region':(0,0), 'gZ':(-700, 700), 'isFiducial':(1,1)}],
    'EndcapP_XY':[['gX', 'gY'], {'region':(1,1), 'isFiducial':(1,1)}],
    'EndcapN_XY':[['gX', 'gY'], {'region':(-1,-1), 'isFiducial':(1,1)}],
#    'lX_lY':['lX', 'lY', {'isFiducial':(1,1)}],
}
for name, (variables, ranges) in plots.iteritems():
    subsels = []
    if name.startswith("Barrel"):
        for station in range(1,5):
            nLayer = 2
            if station > 2: nLayer = 1
            for layer in range(1,nLayer+1):
                subsels.append({'station':(station,station), 'layer':(layer,layer)})
    elif name.startswith("Endcap"):
        for disk in range(1,5):
            subsels.append({'disk':(disk,disk)})
    else:
        subsels = [{'region':(-1,1)}] ## just put a dummy selection

    for subsel in subsels:
        subranges = ranges.copy()
        subranges.update(commonSel)
        subname = name + '_' + ('_'.join("%s%d" % (n, r[0]) for n, r in subsel.iteritems()))

        subranges.update(subsel)
        if len(variables) == 1:
            xVar = variables[0]
            hDen = hSel.Project1D(xVar, subranges, suffix=subname+"_Den")

            subranges.update({'isMatched':(1,1)})
            hNum = hSel.Project1D(xVar, subranges, suffix=subname+"_Num")
        elif len(variables) == 2:
            xVar, yVar = variables
            hDen = hSel.Project2D(xVar, yVar, subranges, suffix=subname+"_Den")

            subranges.update({'isMatched':(1,1)})
            hNum = hSel.Project2D(xVar, yVar, subranges, suffix=subname+"_Num")

        hDen.SetTitle(subname)
        hNum.SetTitle(subname)
        hDen.Write()
        hNum.Write()

