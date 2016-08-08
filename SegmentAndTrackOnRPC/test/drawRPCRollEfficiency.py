#!/usr/bin/env python

run = 0#274442
padW = 500
#mode = "tmPoint"
mode = "tpPoint"
#mode = "rpcPoint"

from ROOT import *
from array import array
import os
gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()
gStyle.SetOptStat(0)

f = TFile("20160806/SingleMuon_Run2016BCD.root")

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

objs = []
hEffs = [
    TH1F("hEffBarrel", "Barrel;Efficiency [%];RPC rolls per 1%", 101, -0.5, 100.5),
    TH1F("hEffEndcap+", "Endcap+;Efficiency [%];RPC rolls per 1%", 101, -0.5, 100.5),
    TH1F("hEffEndcap-", "Endcap-;Efficiency [%];RPC rolls per 1%", 101, -0.5, 100.5),
]
canvs = [
    TCanvas("cBarrel", "cBarrel", 500, 500),
    TCanvas("cEndcap+", "cBarrel", 500, 500),
    TCanvas("cEndcap-", "cBarrel", 500, 500),
]
for i in range(3):
    effs = [100*nRPC/nExp for nExp, nRPC in zip(nExps[i], nRPCs[i]) if nExp > 100]
    effs.sort(reverse=True)

    for eff in effs: hEffs[i].Fill(eff)

    peak = hEffs[i].GetBinCenter(hEffs[i].GetMaximumBin())
    if effs[-1] != 0.0: effsNoZero = effs[:]
    else: effsNoZero = effs[:effs.index(0.0)]
    median = 0
    if len(effsNoZero)%2 == 1: median = effsNoZero[len(effsNoZero)/2]
    else: median = (effsNoZero[len(effsNoZero)/2]+effsNoZero[len(effsNoZero)/2+1])/2

    stats = []
    stats.append(hEffs[i].GetTitle())
    stats.append("Average (include zero) = %.1f" % (sum(effs)/len(effs)))
    stats.append("Average (without zero) = %.1f" % (sum(effsNoZero)/len(effsNoZero)))
    stats.append("Median  (without zero) = %.1f" % median)
    stats.append("Peak at                = %.1f" % hEffs[i].GetBinCenter(hEffs[i].GetMaximumBin()))

    statPanel = TPaveText(gStyle.GetPadLeftMargin()+0.04, 1-gStyle.GetPadTopMargin()-6*0.06,
                          0.7, 1-gStyle.GetPadTopMargin()-0.06, "NDC")
    statPanel.SetTextAlign(11)
    for s in stats: statPanel.AddText(s)

    canvs[i].cd()
    hEffs[i].Draw()
    statPanel.Draw()
    statPanel.SetBorderSize(0)
    fixOverlay()

    objs.append(statPanel)

