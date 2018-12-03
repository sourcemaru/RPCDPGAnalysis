#!/usr/bin/env python

binW, xmin, xmax = 0.5, 70.5, 100.5
nbin = int((xmax-xmin)/binW)

from ROOT import *
import os, sys
from RPCDPGAnalysis.SegmentAndTrackOnRPC.buildLabels import *

gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()
gStyle.SetOptStat(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.12)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleSize(0.06, "X");
gStyle.SetTitleSize(0.06, "Y");

eras = [
    ("Run2018", 30, 38, 1001),
    ("Run2017", 30, 38, 3001),
    ("Run2016", TColor.GetColor("#007700"), TColor.GetColor("#000099"), 3005),
    ("Run2015", 1, 1, 0),
]

resultDir = "results/efficiency_overall"
if not os.path.exists(resultDir):
    print "Please make a directory %s and put efficiency_*.txt under this directory." % resultDir
    os.exit(1)

objs = {}
for region in ["Barrel", "Endcap"]:
    c = TCanvas("cEffOverlay%s" % region, "c%s" % region, 485, 176, 800, 600)
    hs = THStack("hs%s" % region, "Overall efficiency - %s;Efficiency [%%];Number of Rolls" % region)

    leg = TLegend(0.2, 0.4, 0.4, 0.4+0.07*len(eras))
    leg.SetBorderSize(0)

    labels = []

    header = TLatex(gStyle.GetPadLeftMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                    "RPC Overall Efficiency - %s" % region)
    header.SetNDC()
    header.SetTextAlign(11)
    header.SetTextFont(42)

    labels.append(header)

    lls = buildLabel("RunRun-2", "inset")
    labels.extend(lls)

    statPanelOver70 = TPaveText(0.5, 0.4, 0.75, 0.4+0.07*len(eras), "brNDC")
    statPanelOver70.SetBorderSize(0)
    statPanelOver70.SetFillStyle(0)
    statPanelOver70.SetTextAlign(11)
    t = statPanelOver70.AddText("Mean (>70%)")
    t.SetTextSize(0.045)
    t.SetTextFont(62)

    labels.append(statPanelOver70)

    objs[region] = [c, hs, leg, labels, []]

hVioB = TH2F("hVioB", "hVioB;;Efficiency [%]", len(eras), 1, len(eras)+1, nbin, xmin, xmax)
hVioE = TH2F("hVioE", "hVioE;;Efficiency [%]", len(eras), 1, len(eras)+1, nbin, xmin, xmax)
#hVioB.SetLineColor(TColor.GetColor("#007700"))
#hVioE.SetLineColor(TColor.GetColor("#000099"))
hVioB.SetLineWidth(0)
hVioB.SetFillColor(30)
hVioE.SetFillColor(38)
hVioB.GetYaxis().SetTitleOffset(1.0)
hVioE.GetYaxis().SetTitleOffset(1.0)
for i, (era, colorB, colorE, pattern) in enumerate(sorted(eras, key=lambda x: x[0])):
    hVioB.GetXaxis().SetBinLabel(i+1, era)
    hVioE.GetXaxis().SetBinLabel(i+1, era)

for era, colorB, colorE, pattern in eras:
    lumi = eraToLumi(era)

    hB = TH1F("hBEff_%s" % era, "Overall efficiency - Barrel;Efficiency [%%];Number of Rolls", nbin, xmin, xmax)
    hE = TH1F("hEEff_%s" % era, "Overall efficiency - Endcap;Efficiency [%%];Number of Rolls", nbin, xmin, xmax)
    if pattern == 0:
        hB.SetLineColor(colorB)
        hE.SetLineColor(colorE)
    else:
        hB.SetFillColor(colorB)
        hE.SetFillColor(colorE)
        hB.SetLineColor(TColor.GetColor("#007700"))
        hE.SetLineColor(TColor.GetColor("#000099"))
    hB.SetFillStyle(pattern)
    hE.SetFillStyle(pattern)
    hB.GetYaxis().SetNdivisions(505)
    hE.GetYaxis().SetNdivisions(505)
    hB.GetYaxis().SetTitleOffset(1.0)
    hE.GetYaxis().SetTitleOffset(1.0)

    effOver70B, effOver70E = [], []
    with open("%s/efficiency_%s.txt" % (resultDir, era)) as f:
        for l in f.readlines():
            l = l.strip()
            if len(l) == 0 or l[0] == '#': continue

            name, eff, errLo, errHi, den = l.split()
            eff, errLo, errHi, den = 100*float(eff), 100*float(errLo), 100*float(errHi), float(den)
            if name.startswith('W'):
                hB.Fill(eff)
                hVioB.Fill(hVioB.GetXaxis().FindBin(era), eff)
                if eff > 70: effOver70B.append(eff)
            elif name.startswith("RE"):
                hE.Fill(eff)
                hVioE.Fill(hVioE.GetXaxis().FindBin(era), eff)
                if eff > 70: effOver70E.append(eff)

  
    objs["Barrel"][-1].append(hB)
    objs["Endcap"][-1].append(hE)

    objs["Barrel"][1].Add(hB)
    objs["Endcap"][1].Add(hE)

    objs["Barrel"][2].AddEntry(hB, "%s (%.2f fb^{-1})" % (era[3:], lumi), "f")
    objs["Endcap"][2].AddEntry(hE, "%s (%.2f fb^{-1})" % (era[3:], lumi), "f")

    tB = objs["Barrel"][3][-1].AddText("%s   %.2f%%" % (era[3:], sum(effOver70B)/len(effOver70B)))
    tE = objs["Endcap"][3][-1].AddText("%s   %.2f%%" % (era[3:], sum(effOver70E)/len(effOver70E)))
    tB.SetTextSize(0.035)
    tB.SetTextFont(41)
    tE.SetTextSize(0.035)
    tE.SetTextFont(41)

for c, hs, leg, labels, hists in objs.itervalues():
    c.cd()
    hs.Draw("nostack")
    hs.GetYaxis().SetNdivisions(505)
    hs.GetYaxis().SetTitleOffset(1)
    leg.Draw()
    for l in labels: l.Draw()
    c.Modified()
    c.Update()

    c.Print("%s/%s.png" % (resultDir, c.GetName()))
    c.Print("%s/%s.pdf" % (resultDir, c.GetName()))
    c.Print("%s/%s.C" % (resultDir, c.GetName()))
    c.Modified()
    c.Update()

cVioB = TCanvas("cVioB", "cVioB", 700, 600)
hVioB.Draw("violin")
llVioB = buildLabel("RunRun-2", "outset")
for l in llVioB: l.Draw()
cVioB.Print("%s/%s.png" % (resultDir, cVioB.GetName()))

cVioE = TCanvas("cVioE", "cVioE", 700, 600)
hVioE.Draw("violin")
llVioE = buildLabel("RunRun-2", "outset")
for l in llVioE: l.Draw()
cVioE.Print("%s/%s.png" % (resultDir, cVioE.GetName()))
