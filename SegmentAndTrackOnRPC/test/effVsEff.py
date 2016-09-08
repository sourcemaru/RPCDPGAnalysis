#!/usr/bin/env python
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

chMap = {}
for l in open("effs_RPCMonitor_273730.txt").readlines():
    l = l.strip().split()
    chMap[l[0]] = [float(l[1])*100]
for l in open("effs_SingleMu_273730.txt").readlines():
#for l in open("effs_SingleMuNoTnP_273730.txt").readlines():
    l = l.strip().split()
    chMap[l[0]].append(float(l[1]))

xmin = 70
h2BEff = TH2F("h2BEff", "h2BEff;Efficiency from RPCMonitor;Efficiency from SingleMuon TnP",
              int(2*(100.5-xmin)), xmin, 100.5, int(2*(100.5-xmin)), xmin, 100.5)
h2EEff = TH2F("h2EEff", "h2EEff;Efficiency from RPCMonitor;Efficiency from SingleMuon TnP",
              int(2*(100.5-xmin)), xmin, 100.5, int(2*(100.5-xmin)), xmin, 100.5)
hBEff1 = TH1F("hBEff1", "hBEff1;Barrel Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
hBEff2 = TH1F("hBEff2", "hBEff2;Barrel Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
hEEff1 = TH1F("hEEff1", "hEEff1;Endcap Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
hEEff2 = TH1F("hEEff2", "hEEff2;Endcap Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
for ch in chMap:
    if ch.startswith("W"):
        h2BEff.Fill(max(xmin, chMap[ch][0]), max(xmin, chMap[ch][1]))
        hBEff1.Fill(max(xmin, chMap[ch][0]))
        hBEff2.Fill(max(xmin, chMap[ch][1]))
    else:
        h2EEff.Fill(max(xmin, chMap[ch][0]), max(xmin, chMap[ch][1]))
        hEEff1.Fill(max(xmin, chMap[ch][0]))
        hEEff2.Fill(max(xmin, chMap[ch][1]))

cB2 = TCanvas("cB2", "cB2", 500, 500)
h2BEff.Draw("COLZ")
f = TF1("f", "x", xmin, 100.5)
f.SetLineColor(kBlack)
f.Draw("same")
cB2.Print("%s.png" % cB2.GetName())

cE2 = TCanvas("cE2", "cE2", 500, 500)
h2EEff.Draw("COLZ")
f.Draw("same")
cE2.Print("%s.png" % cE2.GetName())

cB = TCanvas("cB", "cB", 500, 500)
legB = TLegend(0.15, 0.65, 0.4, 0.85)
legB.SetBorderSize(0)
legB.SetFillStyle(0)
legB.AddEntry(hBEff1, "RPCMonitor")
legB.AddEntry(hBEff2, "SingleMuon")
hBEff1.SetLineColor(kRed)
hBEff2.SetLineColor(kBlue)
hBEff1.Draw("")
hBEff2.Draw("same")
legB.Draw()
cB.Print("%s.png" % cB.GetName())

cE = TCanvas("cE", "cE", 500, 500)
legE = TLegend(0.15, 0.65, 0.4, 0.85)
legE.SetBorderSize(0)
legE.SetFillStyle(0)
legE.AddEntry(hEEff1, "RPCMonitor")
legE.AddEntry(hEEff2, "SingleMuon")
hEEff1.SetLineColor(kRed)
hEEff2.SetLineColor(kBlue)
hEEff1.Draw("")
hEEff2.Draw("same")
legE.Draw()
cE.Print("%s.png" % cE.GetName())

