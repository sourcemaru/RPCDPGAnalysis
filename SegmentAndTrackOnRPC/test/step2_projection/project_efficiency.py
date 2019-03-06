#!/usr/bin/env python

import os, sys
import gzip
if "CMSSW_BASE" in os.environ:
    sys.path.append("%s/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/python" % os.environ["CMSSW_BASE"])
from ROOT import gStyle, TFile
from ProjectTHnSparse import THnSparseSelector
from collections import OrderedDict

def project(fName0, commonSel):
    gStyle.SetOptStat(0)

    print "@@ Opening root file..."
    f = TFile(fName0)
    print "@@ Loading RPC TnP histogram..."
    hInfo = f.Get("rpcExt/hInfo")
    print "@@ Initializing THnSparseSelector..."
    hSel = THnSparseSelector(hInfo)

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
        fName = "data/efficiency/run%d.txt" % run
        if not os.path.exists(fName) and os.path.exists(fName+".gz"):
            with open(fName, 'w') as fout:
                fName.write(gzip.open('.gz', 'rb').read())
            os.remove(fName+".gz")

        effTable = OrderedDict()
        if os.path.exists(fName):
            for line in open(fName).readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#': continue

                name, den, num = line.split()
                den, num = float(den), float(num)
                effTable[name] = [den, num]

        subranges = commonSel.copy()
        subranges.update({'run':[run, run]})
        hDen = hSel.Project1D("rollName", subranges, suffix="_Den")
        subranges.update({'isMatched':(1,1)})
        hNum = hSel.Project1D("rollName", subranges, suffix="_Num")

        for i, name in enumerate(rollNames):
            den = hDen.GetBinContent(i+1)
            num = hNum.GetBinContent(i+1)
            if name not in effTable:
                effTable[name] = [den, num]
            else:
                effTable[name] = [den+effTable[name][0], num+effTable[name][1]]

        hDen.Delete()
        hNum.Delete()

        with open(fName, "w") as fout:
            print>>fout, "#RollName Denominator Numerator"

            for name, [den, num] in effTable.iteritems():
                print>>fout, name, den, num

        print ""

    print "@@ Done."

if __name__ == '__main__':
    commonSel = {
        'isFiducial':(1,1),
        #'mass':(84,97),
    }

    if not os.path.exists("data/efficiency"): os.makedirs("data/efficiency")
    for fName in sys.argv[1:]:
        project(fName, commonSel)
