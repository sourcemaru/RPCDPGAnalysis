#!/usr/bin/env python

#from ROOT import *
import os, sys

sys.path.append("%s/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/python" % os.environ["CMSSW_BASE"])
from ProjectTHnSparse import *
from ROOT import *
gStyle.SetOptStat(0)

f = TFile(sys.argv[1])
hInfo = f.Get("rpcExt/hInfo")
hSel = THnSparseSelector(hInfo)

if not os.path.exists("hists"): os.mkdir("hists")
f = TFile("hists/properties_%s" % (os.path.basename(sys.argv[1])), "RECREATE")

commonSel = {
    #'run':(315257,315420), ## Run2018A, before CCU error fix
    #'run':(315488,999999),
    #'mass':(84,97),
}

plots = {
    'mass':[['mass'], {}],

    'residual':[['resX'], {}],
    'residual_Barrel' :[['resX'], {'region':( 0, 0)}],
    'residual_EndcapP':[['resX'], {'region':( 1, 1)}],
    'residual_EndcapN':[['resX'], {'region':(-1,-1)}],

    'bx':[['bx'], {}],
    'bxVsTime':[['bx', 'time'], {}],
    'time':[['time'], {}],

    'cls':[['cls'], {}],
    'cls_Barrel' :[['cls'], {'region':( 0, 0)}],
    'cls_EndcapP':[['cls'], {'region':( 1, 1)}],
    'cls_EndcapN':[['cls'], {'region':(-1,-1)}],

    'timeAtBx-2':[['time'], {'bx':(-2,-2)}],
    'timeAtBx-1':[['time'], {'bx':(-1,-1)}],
    'timeAtBx0':[['time'], {'bx':( 0, 0)}],
    'timeAtBx1':[['time'], {'bx':( 1, 1)}],
    'timeAtBx2':[['time'], {'bx':( 2, 2)}],
    'timeAtBx3':[['time'], {'bx':( 3, 3)}],

    'rollNames':[['rollName'], {}],

    'cls_rollNames':[['rollName', 'cls'], {}],
    'pt_rollNames':[['rollName', 'pt'], {}],
    'bx_rollNames':[['rollName', 'bx'], {}],
    'time_rollNames':[['rollName', 'time'], {}],
}

for name, (variables, ranges) in plots.iteritems():
    subranges = {'isMatched':(1,1),}
    subranges.update(ranges)
    subranges.update(commonSel)
    h = None
    if len(variables) == 1:
        xVar = variables[0]
        if name == 'rollNames':
            h = hSel.Project1D(xVar, subranges, copyAxisLabel=True)
        else:
            h = hSel.Project1D(xVar, subranges)
    elif len(variables) == 2:
        xVar, yVar = variables
        h = hSel.Project2D(xVar, yVar, subranges)
    if h == None: continue
    h.SetName(name)
    h.Write()

## per station plots
plots = {
    'mass':[['mass'], {}],
    'residual':[['resX'], {}],
    'cls':[['cls'], {}],
    'bx':[['bx'], {}],
    'time':[['time'], {}],
}
regionCuts = {'Barrel':(0,0), 'EndcapP':(1,1), 'EndcapN':(-1,-1)}
for name, (variables, ranges) in plots.iteritems():
    for regionName, regionCut in regionCuts.iteritems():
        if regionName == 'Barrel':
            for station in range(1, 5):
                subranges = {'isMatched':(1,1), 'station':(station,station)}
                subranges.update(ranges)
                subranges.update(commonSel)
                subranges['region'] = regionCut
                h = None
                if len(variables) == 1:
                    xVar = variables[0]
                    h = hSel.Project1D(xVar, subranges)
                elif len(variables) == 2:
                    xVar, yVar = variables
                    h = hSel.Project2D(xVar, yVar, subranges)
                if h == None: continue
                h.SetName("%s_%s_Station%d" % (name, regionName, station))
                h.Write()
        else:
            for disk in range(1,5):
                subranges = {'isMatched':(1,1), 'disk':(disk,disk)}
                subranges.update(ranges)
                subranges.update(commonSel)
                subranges['region'] = regionCut
                h = None
                if len(variables) == 1:
                    xVar = variables[0]
                    h = hSel.Project1D(xVar, subranges)
                elif len(variables) == 2:
                    xVar, yVar = variables
                    h = hSel.Project2D(xVar, yVar, subranges)
                if h == None: continue
                h.SetName("%s_%s_Disk%d" % (name, regionName, disk))
                h.Write()

