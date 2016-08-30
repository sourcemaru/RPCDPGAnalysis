#!/usr/bin/env python

mode = "RPC"
#mode = "DTCSC"
dataset = "SingleMuon"
era = "Run2016BCDE"
#era = "273730"

if mode == "RPC":
    #module = "rpcPoint"
    module = "tpPoint"
    #module = "tvPoint"
    #module = "tmPoint"
    chTitle = "Rolls"
else:
    module = "efficiencySegment"
    chTitle = "Chambers"

if era == "Run2016BCDE": lumi = 16.094782029242 
elif era == "273730":    lumi = 0.112

run = 0#274442
binW, xmin, xmax = 0.5, 70.5, 100
#binW, xmin, xmax = 1, -0.5, 100

from ROOT import *
from array import array
import os
from math import sqrt

gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()
gStyle.SetOptStat(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.12)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleSize(0.06, "X");
gStyle.SetTitleSize(0.06, "Y");

f = TFile("%s_%s.root" % (dataset, era))

rollNames = [[], []]
nExps = [[], []]
nRecs = [[], []]

for s in [x.GetName() for x in f.Get("%s/Run%06d" % (module, run)).GetListOfKeys()]:
    if s.startswith("Wheel"): category = 0
    elif s.startswith("Disk"): category = 1
    else: continue

    d = f.Get("%s/Run%06d/%s" % (module, run, s))

    for s in [x.GetName() for x in d.GetListOfKeys()]:
        if not s.startswith("hSubdet"): continue
        if s.endswith("NoFid"): continue

        h = d.Get(s)
        n = [h.GetBinContent(i+1) for i in range(h.GetNbinsX())]
        if s.startswith("hSubdetExp"): nExps[category].extend(n)
        if s.startswith("hSubdetRec"): nRecs[category].extend(n)
        if s.startswith("hSubdetExp"): rollNames[category].extend([h.GetXaxis().GetBinLabel(i+1) for i in range(h.GetNbinsX())])

nbin = int((xmax-xmin)/binW)
objs = []
hEffs = [
    TH1F("hEffBarrel", "Barrel;Efficiency [%];Number of "+chTitle, nbin+1, xmin, xmax+binW),
    TH1F("hEffEndcap", "Endcap;Efficiency [%];Number of "+chTitle, nbin+1, xmin, xmax+binW),
]
canvs = [
    TCanvas("cBarrel", "cBarrel", 800, 585),
    TCanvas("cEndcap", "cEndcap", 800, 585),
]
for i in range(2):
    effs = [(name, 100*nRec/nExp) for name, nExp, nRec in zip(rollNames[i], nExps[i], nRecs[i]) if nExp > 0]
    #effs = [(name, 100*nRec/nExp) for name, nExp, nRec in zip(rollNames[i], nExps[i], nRecs[i]) if nExp > 100]
    effs.sort(reverse=True, key=lambda x : x[1])

    hEffs[i].GetYaxis().SetNdivisions(505)
    hEffs[i].GetYaxis().SetTitleOffset(1.0)

    for eff in effs: hEffs[i].Fill(eff[1])

    peak = hEffs[i].GetBinCenter(hEffs[i].GetMaximumBin())
    effsNoZero = [x[1] for x in effs if x[1] != 0.0]
    median = 0
    if len(effsNoZero)%2 == 1: median = effsNoZero[len(effsNoZero)/2]
    else: median = (effsNoZero[len(effsNoZero)/2]+effsNoZero[len(effsNoZero)/2+1])/2

    header = TLatex(gStyle.GetPadLeftMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                    "Overall Efficiency - %s" % hEffs[i].GetTitle())
    header.SetNDC()
    header.SetTextAlign(11)
    header.SetTextFont(42)

    stats = []
    stats.append("Entries %d" % hEffs[i].GetEntries())
    stats.append("Mean   (w/o zero)  = %.1f" % (sum([x for x in effsNoZero])/len(effsNoZero)))
    stats.append("RMS    (w/o zero)  = %.2f" % sqrt(sum([x**2 for x in effsNoZero])/len(effsNoZero) - (sum([x for x in effsNoZero])/len(effsNoZero))**2))
    stats.append("Mean   (with zero) = %.1f" % (sum([x[1] for x in effs])/len(effs)))
    stats.append("Median (w/o zero)  = %.1f" % median)
    stats.append("Peak at            = %.1f" % hEffs[i].GetBinCenter(hEffs[i].GetMaximumBin()))

    statPanel = TPaveText(gStyle.GetPadLeftMargin()+0.05, 1-gStyle.GetPadTopMargin()-len(stats)*0.06,
                          gStyle.GetPadLeftMargin()+0.5, 1-gStyle.GetPadTopMargin()-0.06, "NDC")
    #statPanel = TPaveText(1-gStyle.GetPadRightMargin()-0.5, 1-gStyle.GetPadTopMargin()-len(stats)*0.06,
    #                      1-gStyle.GetPadRightMargin()-0.1, 1-gStyle.GetPadTopMargin()-0.06, "NDC")
    statPanel.SetFillStyle(0)
    statPanel.SetTextAlign(11)
    statPanel.SetBorderSize(0)
    statPanel.SetTextFont(102)
    for s in stats: statPanel.AddText(s)

    canvs[i].cd()
    hEffs[i].Draw()
    statPanel.Draw()
    header.Draw()

    lumi = TLatex().DrawLatexNDC(1-gStyle.GetPadRightMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                                 "%.1f fb^{-1} (13 TeV)" % lumi)
    lumi.SetTextAlign(31)
    lumi.SetTextFont(42)

    fixOverlay()

    objs.extend([header, lumi, statPanel])

    for l in effs:
        print l[0], l[1]

for c in canvs:
    c.Update()
    c.Print(c.GetName()+".png")
    c.Print(c.GetName()+".C")
