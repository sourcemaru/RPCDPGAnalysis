#!/usr/bin/env python

import sys, os
from ROOT import *

from RPCDPGAnalysis.SegmentAndTrackOnRPC.tdrstyle import set_tdr_style
set_tdr_style()

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.16)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)

fName1 = sys.argv[1]
fName2 = sys.argv[2]

Comp = [TGraphAsymmErrors() for i in range(3)]
n = [0., 0., 0.]

hFrame = TH1F("Comp","Comp;Cls;Eff",10,1.5,3.5)
hFrame.SetMaximum(100.5)
hFrame.SetMinimum(60)
hFrame.Draw()

hFrame.GetXaxis().SetLabelSize(0.05)
hFrame.GetXaxis().SetLabelOffset(0.03)
hFrame.GetXaxis().SetTitle("Cluster size")
hFrame.GetXaxis().SetTitleSize(0.04)
hFrame.GetXaxis().SetNdivisions(505)
hFrame.GetXaxis().SetTitleOffset(1.35)

hFrame.GetYaxis().SetLabelSize(0.05)
hFrame.GetYaxis().SetTitle("Efficiency [%]")
hFrame.GetYaxis().SetNdivisions(505)
hFrame.GetYaxis().SetTitleSize(0.04)
hFrame.GetYaxis().SetTitleOffset(1.8)

Cls_Endcap = {}
Cls_Barrel = {}
Cls_RE4 = {}
Eff_Endcap = {}
Eff_Barrel = {}
Eff_RE4 = {}

for line in open(fName1).readlines():
    name, a, b, RollCls = line.strip().split()
    if name.startswith("RE+4") or name.startswith("RE-4"): Cls_RE4[name] = RollCls
    elif name.startswith("R"): Cls_Endcap[name] = RollCls
    else : Cls_Barrel[name] = RollCls

for line in open(fName2).readlines():
    name, c, d, RollEff = line.strip().split()
    if name.startswith("RE+4") or name.startswith("RE-4"): Eff_RE4[name] = RollEff
    elif name.startswith("R"): Eff_Endcap[name] = RollEff
    else : Eff_Barrel[name] = RollEff

for name in Cls_Endcap:
    if name not in Eff_Endcap : continue
    n[0] = Comp[0].GetN()
    Comp[0].SetPoint(n[0], float(Cls_Endcap[name]), float(Eff_Endcap[name]))
for name in Cls_Barrel:
    if name not in Eff_Barrel : continue
    n[1] = Comp[1].GetN()
    Comp[1].SetPoint(n[1], float(Cls_Barrel[name]), float(Eff_Barrel[name]))
for name in Cls_RE4:
    if name not in Eff_RE4 : continue
    n[2] = Comp[2].GetN()
    Comp[2].SetPoint(n[2], float(Cls_RE4[name]), float(Eff_RE4[name]))

Comp[0].SetMarkerColor(kBlue)
Comp[1].SetMarkerColor(kRed)
Comp[2].SetMarkerColor(kGreen)

for num in range(3):            
    Comp[num].SetMarkerSize(0.4)
    Comp[num].SetMarkerStyle(24)
    Comp[num].Draw("Psame")

AllTitlename1 = TLatex(0.2,0.82,"#splitline{CMS}{#bf{#it{Preliminary}}}")
AllTitlename1.SetNDC()
AllTitlename1.SetTextFont(62)
AllTitlename1.SetTextAlign(11)
AllTitlename1.SetTextSize(0.05)
AllTitlename1.Draw("same")

DataTitlename = TLatex(0.95,0.94,"2018 data, 59.97 fb^{-1} (13TeV)")
DataTitlename.SetNDC()
DataTitlename.SetTextFont(42)
DataTitlename.SetTextAlign(31)
DataTitlename.SetTextSize(0.04)
DataTitlename.Draw("same")

leg = TLegend(0.7, 0.2, 0.9, 0.5)
#leg.SetNColumns(3)
leg.SetFillStyle(0)
leg.SetBorderSize(0)

leg.AddEntry(Comp[0], "Endcap", "p")
leg.AddEntry(Comp[1], "Barrel", "p")
leg.AddEntry(Comp[2], "RE4", "p")

leg.Draw("same")

