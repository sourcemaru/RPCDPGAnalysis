#!/usr/bin/env python

from ROOT import *
import os, sys
gStyle.SetOptStat(0)

sys.path.append("%s/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/python" % os.environ["CMSSW_BASE"])
from ProjectTHnSparse import *

print "@@ Opening root file..."
f = TFile(sys.argv[1])
print "@@ Loading RPC TnP histogram..."
hInfo = f.Get("rpcExt/hInfo")
print "@@ Initializing THnSparseSelector..."
hSel = THnSparseSelector(hInfo)

if not os.path.exists("hists"): os.mkdir("hists")

commonSel = {
    'isFiducial':(1,1),
    #'mass':(84,97),
}

variables = ['resX', 'bx', 'cls']

print "@@ Extracting runs..."
hRuns = hSel.Project1D("run", commonSel)
#runs = [i+2 for i in range(hRuns.GetNbinsX()) if hRuns.GetBinContent(i+2) != 0]
runs = [hRuns.GetXaxis().GetBinLowEdge(i+1) for i in range(hRuns.GetNbinsX()) if hRuns.GetBinContent(i+1) != 0]
print "@@ Extracting roll names..."
hRolls = hSel.Project1D("rollName", {}, copyAxisLabel=True)
axisRolls = hRolls.GetXaxis()
rollNames = [axisRolls.GetBinLabel(i) for i in range(hRolls.GetNbinsX()+2) if axisRolls.GetBinLabel(i) != ""]

nRun = len(runs)
for iRun, run in enumerate(runs):
    print "@@ Analyzing run %d (%d/%d)..." % (run, iRun+1, nRun),
    fName = "hists/run%d.txt" % run
    if os.path.exists(fName):
        print " already exists. skip."
        continue

    with open(fName, "w") as fout:
        print>>fout, "#RollName Denominator Numerator"

        h = hSel.Project1D("rollName", commonSel)
        for i, name in enumerate(rollNames):
            #### NOTE: There is a shift in the bin labels. Take rollNames with 1 bin shift
            den = hDen.GetBinContent(i+2)
            num = hNum.GetBinContent(i+2)
            print>>fout, name, den, num

        h.Delete()

    print ""


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

