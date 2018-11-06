#!/usr/bin/env python
import os, sys
if "CMSSW_BASE" in os.environ:
    sys.path.append("%s/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/python" % os.environ["CMSSW_BASE"])
from ROOT import gStyle, TFile
from ProjectTHnSparse import THnSparseSelector
from collections import OrderedDict

def project(fName0, varName, commonSel):
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
        print "@@ Analyzing variable %s in run %d (%d/%d)..." % (varName, run, iRun+1, nRun),
        fName = "data/%s/run%d.txt" % (varName, run)
        statTable = OrderedDict()
        if os.path.exists(fName):
            for line in open(fName).readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#': continue

                name, nEvent, sumW, sumErr2 = line.split()
                nEvent, sumW, sumErr2 = float(nEvent), float(sumW), float(sumErr2)
                statTable[name] = [nEvent, sumW, sumErr2]

        subranges = commonSel.copy()
        subranges.update({'run':[run, run]})
        h = hSel.Project2D("rollName", varName, subranges)
        h.Sumw2()
        prf = h.ProfileX()

        for i, name in enumerate(rollNames):
            nEntries = prf.GetBinEffectiveEntries(i+1)
            sumW = nEntries*prf.GetBinContent(i+1)
            sumErr2 = nEntries*prf.GetBinError(i+1)
            if name not in statTable:
                statTable[name] = [nEntries, sumW, sumErr2]
            else:
                statTable[name] = [nEntries+statTable[name][0], sumW+statTable[name][1], sumErr2+statTable[name][2]]

        prf.Delete()
        h.Delete()

        with open(fName, "w") as fout:
            print>>fout, "#RollName nEntries sumW sumErr2"

            for name, [nEntries, sumW, sumErr2] in statTable.iteritems():
                print>>fout, name, nEntries, sumW, sumErr2 

        print ""

    print "@@ Done."

if __name__ == '__main__':
    commonSel = {
        'isFiducial':(1,1),
        'isMatched':(1,1),
        #'mass':(84,97),
    }

    for varName in ["resX", "bx", "cls"]:
        for fName in sys.argv[1:]:
            if not os.path.exists("data/%s" % varName): os.makedirs("data/%s" % varName)
            project(fName, varName, commonSel)
