#!/usr/bin/env python
from ROOT import *
from array import array
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

chMap = {}
for l in open("RPCMonitor.txt").readlines():
    l = l.strip().split()
    chMap[l[0]] = [float(l[1])]
for l in open("SingleMuon.txt").readlines():
    l = l.strip().split()
    if l[0] not in chMap: chMap[l[0]] = [0.0]
    chMap[l[0]].append(float(l[1]))

blacklist = []
blacklist.extend([x.strip().split()[1] for x in open("blackList_18May.txt").readlines() if x.strip() != ""])
blacklist.extend(["RE+3_R2_CH%02d_C" % (ch+1) for ch in range(36)])
blacklist.extend(["RE-3_R2_CH%02d_C" % (ch+1) for ch in range(36)])
blacklist.extend(["RE+4_R2_CH%02d_B" % (ch+1) for ch in range(36)])
blacklist.extend(["RE-4_R2_CH%02d_B" % (ch+1) for ch in range(36)])
blacklist.extend(["RE+4_R2_CH%02d_C" % (ch+1) for ch in range(36)])
blacklist.extend(["RE-4_R2_CH%02d_C" % (ch+1) for ch in range(36)])
blacklist.extend(["RE+2_R3_CH%02d_A" % (ch+1) for ch in range(36)])
blacklist.extend(["RE-2_R3_CH%02d_A" % (ch+1) for ch in range(36)])

xmin = 70
h2BEff = TH2F("h2BEff", "h2BEff;Efficiency from Segment;Efficiency from Tag and Probe",
              int(2*(100.5-xmin)), xmin, 100.5, int(2*(100.5-xmin)), xmin, 100.5)
h2EEff = TH2F("h2EEff", "h2EEff;Efficiency from Segment;Efficiency from Tad and Probe",
              int(2*(100.5-xmin)), xmin, 100.5, int(2*(100.5-xmin)), xmin, 100.5)
hBEff1 = TH1F("hBEff1", "hBEff1;Barrel Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
hBEff2 = TH1F("hBEff2", "hBEff2;Barrel Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
hEEff1 = TH1F("hEEff1", "hEEff1;Endcap Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
hEEff2 = TH1F("hEEff2", "hEEff2;Endcap Efficiency", int(2*(100.5-xmin)), xmin, 100.5)
hWDEffDiff = TH2F("hWDEffDiff", "hWDEffDiff;;Segment eff. - TnP eff.", 13, 0, 13, 82, -20.5, 20.5)
hWDEffDiffProf = TProfile2D("hWDEffDiffProf", "hWDEffDiffProf;;Station/Ring", 13, 0, 13, 4, 0.5, 4.5)
hWDEffProf0 = TProfile2D("hWDEffProf0", "hWDEffProf0;;Station/Ring", 13, 0, 13, 4, 0.5, 4.5)
hWDEffProf1 = TProfile2D("hWDEffProf1", "hWDEffProf1;;Station/Ring", 13, 0, 13, 4, 0.5, 4.5)
for i, label in enumerate(["RE%+d" % d for d in range(-4, 0)]
                         +["W%+d" % w for w in range(-2, 3)]
                         +["RE%+d" % d for d in range(1, 5)]):
    hWDEffDiff.GetXaxis().SetBinLabel(i+1, label)
    hWDEffDiffProf.GetXaxis().SetBinLabel(i+1, label)
    hWDEffProf0.GetXaxis().SetBinLabel(i+1, label)
    hWDEffProf1.GetXaxis().SetBinLabel(i+1, label)
for ch in chMap:
    if ch in blacklist: continue

    eff0 = max(xmin+0.25, chMap[ch][0])
    eff1 = max(xmin+0.25, chMap[ch][1])
    if ch.startswith("W"):
        wheelStr = ch.split('_')[0]
        station = ch.split('_')[1][2:].replace("in","").replace("out","")
        if station[-1] in "+-": station = station[:-1]
        if station[-1] in "+-": station = station[:-1]
        station = float(station)
        h2BEff.Fill(eff0, eff1)
        hBEff1.Fill(eff0)
        hBEff2.Fill(eff1)
        hWDEffDiff.Fill(wheelStr, min(20.5-1e-9, max(-20.5, eff0-eff1)), 1)
        hWDEffDiffProf.Fill(wheelStr, station, eff0-eff1)
        hWDEffProf0.Fill(wheelStr, station, eff0)
        hWDEffProf1.Fill(wheelStr, station, eff1)
    else:
        diskStr = ch.split('_')[0]
        ring  = float(ch.split('_')[1][1:])
        h2EEff.Fill(eff0, eff1)
        hEEff1.Fill(eff0)
        hEEff2.Fill(eff1)
        hWDEffDiff.Fill(diskStr, min(20.5-1e-9, max(-20.5, eff0-eff1)), 1)
        hWDEffDiffProf.Fill(diskStr, ring, eff0-eff1)
        hWDEffProf0.Fill(diskStr, ring, eff0)
        hWDEffProf1.Fill(diskStr, ring, eff1)

cEff_B2 = TCanvas("cEff_B2", "cEff_B2", 500, 500)
h2BEff.Draw("COLZ")
f = TF1("f", "x", xmin, 100.5)
f.SetLineColor(kBlack)
f.Draw("same")
cEff_B2.Print("%s.png" % cEff_B2.GetName())
cEff_B2.Print("%s.pdf" % cEff_B2.GetName())
cEff_B2.Print("%s.C" % cEff_B2.GetName())

cEff_E2 = TCanvas("cEff_E2", "cEff_E2", 500, 500)
h2EEff.Draw("COLZ")
f.Draw("same")
cEff_E2.Print("%s.png" % cEff_E2.GetName())
cEff_E2.Print("%s.pdf" % cEff_E2.GetName())
cEff_E2.Print("%s.C" % cEff_E2.GetName())

cEff_B = TCanvas("cEff_B", "cEff_B", 500, 500)
legB = TLegend(0.15, 0.65, 0.4, 0.85)
legB.SetBorderSize(0)
legB.SetFillStyle(0)
legB.AddEntry(hBEff1, "RPCMonitor")
legB.AddEntry(hBEff2, "SingleMuon")
hBEff1.SetLineColor(kRed)
hBEff2.SetLineColor(kBlue)
hsBEff = THStack("hsBEff", ";%s;%s" % (hBEff1.GetXaxis().GetTitle(), hBEff1.GetYaxis().GetTitle()))
hsBEff.Add(hBEff1)
hsBEff.Add(hBEff2)
hsBEff.Draw("nostack")
legB.Draw()
cEff_B.Print("%s.png" % cEff_B.GetName())
cEff_B.Print("%s.pdf" % cEff_B.GetName())
cEff_B.Print("%s.C" % cEff_B.GetName())

cEff_E = TCanvas("cEff_E", "cEff_E", 500, 500)
legE = TLegend(0.15, 0.65, 0.4, 0.85)
legE.SetBorderSize(0)
legE.SetFillStyle(0)
legE.AddEntry(hEEff1, "RPCMonitor")
legE.AddEntry(hEEff2, "SingleMuon")
hEEff1.SetLineColor(kRed)
hEEff2.SetLineColor(kBlue)
hsEEff = THStack("hsEEff", ";%s;%s" % (hEEff1.GetXaxis().GetTitle(), hEEff1.GetYaxis().GetTitle()))
hsEEff.Add(hEEff1)
hsEEff.Add(hEEff2)
hsEEff.Draw("nostack")
legE.Draw()
cEff_E.Print("%s.png" % cEff_E.GetName())
cEff_E.Print("%s.pdf" % cEff_E.GetName())
cEff_E.Print("%s.C" % cEff_E.GetName())

cWDEffDiff = TCanvas("cWDEffDiff", "cWDEffDiff", 1300/2, 500)
hWDEffDiff.Draw("COLZ")
cWDEffDiff.Print("%s.png" % cWDEffDiff.GetName())
cWDEffDiff.Print("%s.pdf" % cWDEffDiff.GetName())
cWDEffDiff.Print("%s.C" % cWDEffDiff.GetName())

gStyle.SetPaintTextFormat(".3g")
hWDEffDiffProf.SetMarkerSize(1.5)
cWDEffDiffProf = TCanvas("cWDEffDiffProf", "cWDEffDiffProf", 1300/2, 400)
hWDEffDiffProf.Draw("COLZtext45")
cWDEffDiffProf.Print("%s.png" % cWDEffDiffProf.GetName())
cWDEffDiffProf.Print("%s.pdf" % cWDEffDiffProf.GetName())
cWDEffDiffProf.Print("%s.C" % cWDEffDiffProf.GetName())

hWDEffProf0.SetMarkerSize(1.5)
hWDEffProf0.SetMaximum(100)
hWDEffProf0.SetMinimum(90)
cWDEffProf0 = TCanvas("cWDEffProf0", "cWDEffProf0", 1300/2, 400)
hWDEffProf0.Draw("COLZtext45")
cWDEffProf0.Print("%s.png" % cWDEffProf0.GetName())
cWDEffProf0.Print("%s.pdf" % cWDEffProf0.GetName())
cWDEffProf0.Print("%s.C" % cWDEffProf0.GetName())

hWDEffProf1.SetMarkerSize(1.5)
hWDEffProf1.SetMaximum(100)
hWDEffProf1.SetMinimum(90)
cWDEffProf1 = TCanvas("cWDEffProf1", "cWDEffProf1", 1300/2, 400)
hWDEffProf1.Draw("COLZtext45")
cWDEffProf1.Print("%s.png" % cWDEffProf1.GetName())
cWDEffProf1.Print("%s.pdf" % cWDEffProf1.GetName())
cWDEffProf1.Print("%s.C" % cWDEffProf1.GetName())

