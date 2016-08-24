#!/usr/bin/env python

run = 0#274442
#mode = "tmPoint"
mode = "tpPoint"
#mode = "tvPoint"
#mode = "rpcPoint"

from ROOT import *
from array import array
import os
gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()
gStyle.SetOptStat(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.12)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleSize(0.06, "X");
gStyle.SetTitleSize(0.06, "Y");

f = TFile("SingleMuon_Run2016BCDE.root")

rollNames = [[], [], []]
nExps = [[], [], []]
nRPCs = [[], [], []]

for s in [x.GetName() for x in f.Get("%s/Run%06d/Barrel" % (mode, run)).GetListOfKeys()]:
    if not s.startswith("Wheel_"): continue
    wheeldir = f.Get("%s/Run%06d/Barrel/%s" % (mode, run, s))

    for s in [x.GetName() for x in wheeldir.GetListOfKeys()]:
        if not s.startswith("sector_"): continue
        sectordir = wheeldir.Get(s)

        for s in [x.GetName() for x in sectordir.GetListOfKeys()]:
            if not s.startswith("station_"): continue
            stationdir = sectordir.Get(s)

            for s in [x.GetName() for x in stationdir.GetListOfKeys()]:
                h = stationdir.Get(s)
                n = [h.GetBinContent(i+1) for i in range(h.GetNbinsX())]
                if s.startswith("RollExp_"): nExps[0].extend(n)
                if s.startswith("RollRPC_"): nRPCs[0].extend(n)
                if s.startswith("RollExp_"): rollNames[0].extend([h.GetXaxis().GetBinLabel(i+1) for i in range(h.GetNbinsX())])

for s in [x.GetName() for x in f.Get("%s/Run%06d/Endcap+" % (mode, run)).GetListOfKeys()]:
    if not s.startswith("Disk_"): continue
    diskdir = f.Get("%s/Run%06d/Endcap+/%s" % (mode, run, s))

    for s in [x.GetName() for x in diskdir.GetListOfKeys()]:
        if not s.startswith("ring_"): continue
        ringdir = diskdir.Get(s)

        for s in [x.GetName() for x in ringdir.GetListOfKeys()]:
            if not s.startswith("sector_"): continue
            sectordir = ringdir.Get(s)

            for s in [x.GetName() for x in sectordir.GetListOfKeys()]:
                h = sectordir.Get(s)
                n = [h.GetBinContent(i+1) for i in range(h.GetNbinsX())]
                if s.startswith("RollExp_"): nExps[1].extend(n)
                if s.startswith("RollRPC_"): nRPCs[1].extend(n)
                if s.startswith("RollExp_"): rollNames[1].extend([h.GetXaxis().GetBinLabel(i+1) for i in range(h.GetNbinsX())])

for s in [x.GetName() for x in f.Get("%s/Run%06d/Endcap-" % (mode, run)).GetListOfKeys()]:
    if not s.startswith("Disk_"): continue
    diskdir = f.Get("%s/Run%06d/Endcap-/%s" % (mode, run, s))

    for s in [x.GetName() for x in diskdir.GetListOfKeys()]:
        if not s.startswith("ring_"): continue
        ringdir = diskdir.Get(s)

        for s in [x.GetName() for x in ringdir.GetListOfKeys()]:
            if not s.startswith("sector_"): continue
            sectordir = ringdir.Get(s)

            for s in [x.GetName() for x in sectordir.GetListOfKeys()]:
                h = sectordir.Get(s)
                n = [h.GetBinContent(i+1) for i in range(h.GetNbinsX())]
                if s.startswith("RollExp_"): nExps[2].extend(n)
                if s.startswith("RollRPC_"): nRPCs[2].extend(n)
                if s.startswith("RollExp_"): rollNames[2].extend([h.GetXaxis().GetBinLabel(i+1) for i in range(h.GetNbinsX())])

binW, xmin, xmax = 0.5, 70.5, 100
nbin = int((xmax-xmin)/binW)
objs = []
hEffs = [
    TH1F("hEffBarrel", "Barrel;Efficiency [%];Number of Rolls", nbin+1, xmin, xmax+binW),
    TH1F("hEffEndcapP", "Endcap+;Efficiency [%];Number of Rolls", nbin+1, xmin, xmax+binW),
    TH1F("hEffEndcapN", "Endcap-;Efficiency [%];Number of Rolls", nbin+1, xmin, xmax+binW),
]
canvs = [
    TCanvas("cBarrel", "cBarrel", 800, 585),
    TCanvas("cEndcapP", "cEndcapP", 800, 585),
    TCanvas("cEndcapN", "cEndcapN", 800, 585),
]
for i in range(3):
    effs = [(name, 100*nRPC/nExp) for name, nExp, nRPC in zip(rollNames[i], nExps[i], nRPCs[i]) if nExp > 100]
    effs.sort(reverse=True, key=lambda x : x[1])

    hEffs[i].GetYaxis().SetNdivisions(505)
    hEffs[i].GetYaxis().SetTitleOffset(1.0)

    for eff in effs: hEffs[i].Fill(eff[1])

    peak = hEffs[i].GetBinCenter(hEffs[i].GetMaximumBin())
    effsNoZero = [x for x in effs if x[1] != 0.0]
    median = 0
    if len(effsNoZero)%2 == 1: median = effsNoZero[len(effsNoZero)/2][1]
    else: median = (effsNoZero[len(effsNoZero)/2]+effsNoZero[len(effsNoZero)/2+1])/2

    header = TLatex(gStyle.GetPadLeftMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                    "RPC Overall Efficiency - %s" % hEffs[i].GetTitle())
    header.SetNDC()
    header.SetTextAlign(11)
    header.SetTextFont(42)

    stats = []
    stats.append("Average (include zero) = %.1f" % (sum([x[1] for x in effs])/len(effs)))
    stats.append("Average (without zero) = %.1f" % (sum([x[1] for x in effsNoZero])/len(effsNoZero)))
    stats.append("Median  (without zero) = %.1f" % median)
    stats.append("Peak at                = %.1f" % hEffs[i].GetBinCenter(hEffs[i].GetMaximumBin()))

    statPanel = TPaveText(1-gStyle.GetPadRightMargin()-0.5, 1-gStyle.GetPadTopMargin()-len(stats)*0.06,
                          1-gStyle.GetPadRightMargin()-0.1, 1-gStyle.GetPadTopMargin()-0.06, "NDC")
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
                                 "%.1f fb^{-1} (13 TeV)" % 16.094782029242)
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
