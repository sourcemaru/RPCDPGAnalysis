#!/usr/bin/env python

import sys, os
from ROOT import *

gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.05)
gStyle.SetPadRightMargin(0.05)
gStyle.SetPadBottomMargin(0.2333)

hist = {}

rum = 1

runs = []
for line in open(sys.argv[1]).readlines():
    line = line.strip()
    if len(line) == 0 or line.startswith('#'): continue
    name = line.split()[0]

    hist[name] = TH1F("%s" % name, ";Efficiency;", 100, 0, 1)

for fName in sys.argv[1:]:
    runs.append(int(os.path.basename(fName).split('.')[0][3:]))
nRun = len(runs)
runs.sort()

h2d = TH2F("cls","ClusterSize;Run;Cls",len(runs),1,len(runs)+1,5,0,5)

f = TFile("hist.root", "recreate")
for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, Nentries, mean, err2 = line.split()

        Nentries, mean = float(Nentries), float(mean)

        h2d.Fill(rum, mean)

    rum += 1

cHistories = TCanvas("cHistory")
cHistories.SetCanvasSize(3300,500)
cHistories.SetWindowSize(3300,500)
#hHistoryFrame = TH1F("hHistoryFrame", "hHistoryFrame", nRun, 0, nRun)
#hHistoryFrame.SetMaximum(4.0)
#hHistoryFrame.SetMinimum(0)

for i, run in enumerate(runs):
    if i%10 == 0:
        h2d.GetXaxis().SetBinLabel(i+1, "%d" % run)

cHistories.cd()
h2d.Draw("COLZ")

#cHistories.Modified()
#cHistories.Update()

#cHistories.Print("runbyrun2018Cls.png")
