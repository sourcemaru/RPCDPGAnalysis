#!/usr/bin/env python3
import os, sys
import gzip
if "CMSSW_BASE" in os.environ:
    sys.path.append("%s/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/python" % os.environ["CMSSW_BASE"])
from ROOT import gStyle, TFile
from ProjectTHnSparse import THnSparseSelector
from collections import OrderedDict

def project(fName0, varName, commonSel):
    gStyle.SetOptStat(0)

    print("@@ Opening root file...")
    f = TFile(fName0)
    print("@@ Loading RPC TnP histogram...")
    hInfo = f.Get("muonHitFromTrackerMuonAnalyzer/hInfo")
    print("@@ Initializing THnSparseSelector...")
    hSel = THnSparseSelector(hInfo)

    print("@@ Extracting runs...")
    hRuns = hSel.Project1D("run", commonSel)
    #runs = [i+2 for i in range(hRuns.GetNbinsX()) if hRuns.GetBinContent(i+2) != 0]
    runs = [hRuns.GetXaxis().GetBinLowEdge(i+1) for i in range(hRuns.GetNbinsX()) if hRuns.GetBinContent(i+1) != 0]
    print("@@ Extracting roll names...")
    hRolls = hSel.Project1D("rollName", {}, copyAxisLabel=True)
    axisRolls = hRolls.GetXaxis()
    rollNames = [axisRolls.GetBinLabel(i) for i in range(hRolls.GetNbinsX()+2) if axisRolls.GetBinLabel(i) != ""]

    nRun = len(runs)
    for iRun, run in enumerate(runs):
        print("@@ Analyzing variable %s in run %d (%d/%d)..." % (varName, run, iRun+1, nRun), end=' ')
        fName = "data/%s/run%d.txt" % (varName, run)
        if not os.path.exists(fName) and os.path.exists(fName+".gz"):
            with open(fName, 'w') as fout:
                fName.write(gzip.open('.gz', 'rb').read())
            os.remove(fName+".gz")

        statTable = OrderedDict()
        if os.path.exists(fName):
            for line in open(fName).readlines():
                line = line.strip()
                if len(line) == 0 or line[0] == '#': continue

                name, nEvent, mean, err2 = line.split()
                nEvent, mean, err2 = float(nEvent), float(mean), float(err2)
                statTable[name] = [nEvent, mean, err2]

        subranges = commonSel.copy()
        subranges.update({'run':[run, run]})
        h = hSel.Project2D("rollName", varName, subranges)
        h.Sumw2()
        prf = h.ProfileX()

        for i, name in enumerate(rollNames):
            nA = prf.GetBinEffectiveEntries(i+1)
            mA = prf.GetBinContent(i+1)
            e2A = prf.GetBinError(i+1)
            if name not in statTable:
                statTable[name] = [nA, mA, e2A]
            else:
                nB, mB, e2B = statTable[name]
                n = nA+nB
                if n == 0: ## Just a default values
                    statTable[name] = [0, mA*mB, e2A+e2B]
                else: ## Weighted average and RMS by their division
                    m = (nA*mA+nB*mB)/n
                    e2 = nA/n*e2A + nB/n*e2B + nA*nB*( ((mA-mB)/n)**2 ) ## <= you can derive this yourself
                    statTable[name] = [n, m, e2]

        prf.Delete()
        h.Delete()

        with open(fName, "w") as fout:
            print("#RollName nEntries mean err2", file=fout)

            for name, [nEntries, sumW, sumErr2] in statTable.items():
                print(name, nEntries, sumW, sumErr2, file=fout) 

        print("")

    print("@@ Done.")

if __name__ == '__main__':
    commonSel = {
        'isFiducial':(1,1),
        'isMatched':(1,1),
        #'mass':(84,97),
    }

    for varName in ["cls", "resX", "bx",]:
        for fName in sys.argv[1:]:
            if not os.path.exists("data/%s" % varName): os.makedirs("data/%s" % varName)
            project(fName, varName, commonSel)
