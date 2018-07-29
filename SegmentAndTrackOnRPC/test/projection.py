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

        subranges = commonSel.copy()
        hDen = hSel.Project1D("rollName", subranges, suffix="_Den")
        subranges.update({'isMatched':(1,1)})
        hNum = hSel.Project1D("rollName", subranges, suffix="_Num")

        for i, name in enumerate(rollNames):
            #### NOTE: There is a shift in the bin labels. Take rollNames with 1 bin shift
            den = hDen.GetBinContent(i+2)
            num = hNum.GetBinContent(i+2)
            print>>fout, name, den, num

    hDen.Delete()
    hNum.Delete()

    print ""

print "@@ Done."
