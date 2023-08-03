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

Comp = [TGraphAsymmErrors() for i in range(12)]
n = [0,0,0,0,0,0,0,0,0,0,0,0]

hFrame = TH1F("Comp","Comp;Cls;Eff",10,1.5,3.5)
hFrame.SetMaximum(100.2)
hFrame.SetMinimum(90)

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

hFrame.Draw()

Cls = {}
Eff = {}

for line in open(fName1).readlines():
    run, EndcapCls, BarrelCls, RE4Cls = line.strip().split()
    run = int(run)
    Cls[run] = [EndcapCls, BarrelCls, RE4Cls]

for line in open(fName2).readlines():
    run, EndcapEff, BarrelEff, RE4Eff = line.strip().split()
    run = int(run)
    Eff[run] = [EndcapEff, BarrelEff, RE4Eff]

for run in Cls:
    if run not in Eff : continue

    if run>=251168 and run<=260627:
        for k in range(0,3):
    	    n[k] = Comp[k].GetN()
            Comp[k].SetPoint(n[k], float(Cls[run][k]), float(Eff[run][k]))
    elif run>=273150 and run<=284044:
        for k in range(3,6):
            n[k] = Comp[k].GetN()
            Comp[k].SetPoint(n[k], float(Cls[run][k%3]), float(Eff[run][k%3]))
    elif run>=297050 and run<=306460:
        for k in range(6,9):
            n[k] = Comp[k].GetN()
            Comp[k].SetPoint(n[k], float(Cls[run][k%3]), float(Eff[run][k%3]))
    elif run>=315257 and run<=325172:
        for k in range(9,12):
            n[k] = Comp[k].GetN()
            Comp[k].SetPoint(n[k], float(Cls[run][k%3]), float(Eff[run][k%3]))
            
for color in range(12):
    Comp[color].SetMarkerColor(color+1)

Comp[9].SetMarkerColor(kBlue)
Comp[10].SetMarkerColor(kRed)
Comp[11].SetMarkerColor(kGreen)

'''
for color in range(12):
    if color%3 == 0: Comp[color].SetMarkerColor(kRed)
    if color%3 == 1: Comp[color].SetMarkerColor(kBlue)
    if color%3 == 2: Comp[color].SetMarkerColor(kGreen)
'''

for num in range(9,12):
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

leg = TLegend(0.7, 0.2, 0.9, 0.4)
#leg.SetNColumns(3)
leg.SetFillStyle(0)
leg.SetBorderSize(0)

#leg.AddEntry(Comp[0], "2015 Endcap", "p")
#leg.AddEntry(Comp[1], "2015 Barrel", "p")
#leg.AddEntry(Comp[2], "2015 RE4", "p")
#leg.AddEntry(Comp[3], "2016 Endcap", "p")
#leg.AddEntry(Comp[4], "2016 Barrel", "p")
#leg.AddEntry(Comp[5], "2016 RE4", "p")
#leg.AddEntry(Comp[6], "2017 Endcap", "p")
#leg.AddEntry(Comp[7], "2017 Barrel", "p")
#leg.AddEntry(Comp[8], "2017 RE4", "p")
leg.AddEntry(Comp[9], "2018 Endcap", "p")
leg.AddEntry(Comp[10], "2018 Barrel", "p")
leg.AddEntry(Comp[11], "2018 RE4", "p")

leg.Draw("same")

