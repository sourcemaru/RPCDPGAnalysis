#!/usr/bin/env python

import sys, os
from ROOT import *

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadTopMargin(0.07)
gStyle.SetPadRightMargin(0.08)
gStyle.SetPadLeftMargin(0.16)

RunLumi = {}
runs = []

LR2D_15 = TGraphAsymmErrors()
LR2D_16 = TGraphAsymmErrors()
LR2D_17 = TGraphAsymmErrors()
LR2D_18 = TGraphAsymmErrors()

LR2D_Endcap = TGraphAsymmErrors()
LR2D_Barrel = TGraphAsymmErrors()
LR2D_RE4 = TGraphAsymmErrors()

for line in open(sys.argv[1]).readlines():
    line = line.strip()
    run, lumi = line.split()
    run, lumi = int(run), float(lumi)
    RunLumi[run] = [lumi]

for fName in sys.argv[2:]:
    runs.append(int(os.path.basename(fName).split('.')[0][3:]))
nRun = len(runs)
runs.sort()

for fName in sys.argv[2:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    densum = 0
    linenumb = 0
    denavg = 0

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        densum += den
        linenumb += 1

    denavg = densum/linenumb

    if denavg < 10: continue

    setnum = 0
    avgsum = 0
    
    setnum_Endcap = 0
    setnum_Barrel = 0
    setnum_RE4 = 0
    avgsum_Endcap = 0
    avgsum_Barrel = 0
    avgsum_RE4 = 0

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if den == 0: continue

        avg = 100*num/den
        if avg == 0: continue

#        if name.startswith("RE+4") or name.startswith("RE-4"):
#            avgsum_RE4 += avg
#            setnum_RE4 += 1
        if name.startswith("R"):
            avgsum_Endcap += avg
            setnum_Endcap += 1
        else:
            avgsum_Barrel += avg
            setnum_Barrel += 1
	    
        avgsum += avg
	setnum += 1

    runavg = avgsum/setnum
    if setnum_Endcap == 0 : Endcapavg = -1
    else : Endcapavg = avgsum_Endcap/setnum_Endcap
    if setnum_Barrel == 0 : Barrelavg = -1
    else : Barrelavg = avgsum_Barrel/setnum_Barrel
    if setnum_RE4 == 0 : RE4avg = -1
    else : RE4avg = avgsum_RE4/setnum_RE4

    if run in RunLumi :
        RunLumi[run].append(runavg)
        RunLumi[run].append(Endcapavg)
        RunLumi[run].append(Barrelavg)
        RunLumi[run].append(RE4avg)

    
for run in RunLumi:
    if len(RunLumi[run]) < 2 : continue
    if run >= 251168 and run <= 260627:
        n15 = LR2D_15.GetN()
        LR2D_15.SetPoint(n15, RunLumi[run][0], RunLumi[run][1])
    elif run >= 273150 and run <= 284044:
        n16 = LR2D_16.GetN()
        LR2D_16.SetPoint(n16, RunLumi[run][0], RunLumi[run][1])
    elif run >= 297050 and run <= 306460:
        n17 = LR2D_17.GetN()
        LR2D_17.SetPoint(n17, RunLumi[run][0], RunLumi[run][1])
    elif run >= 315257 and run <= 325172:
        if RunLumi[run][1] < 91 : continue  ## For Fitting
        n18 = LR2D_18.GetN()
        LR2D_18.SetPoint(n18, RunLumi[run][0], RunLumi[run][1])

'''
for run in RunLumi:
    if len(RunLumi[run]) < 2 : continue
    nEndcap = LR2D_Endcap.GetN()
    nBarrel = LR2D_Barrel.GetN()
    nRE4 = LR2D_RE4.GetN()
    LR2D_Endcap.SetPoint(nEndcap, RunLumi[run][0], RunLumi[run][2])
    LR2D_Barrel.SetPoint(nBarrel, RunLumi[run][0], RunLumi[run][3])
    LR2D_RE4.SetPoint(nRE4, RunLumi[run][0], RunLumi[run][4])
'''
c = TCanvas("Lumi_Eff","Lumi_Eff",900,600)

FrameMax = 2.0*10**34

hFrame = TH1F("Comp","Comp;Lumi;Eff",1000000,0,FrameMax)
hFrame.SetMaximum(100)
hFrame.SetMinimum(85)
hFrame.Draw()

hFrame.GetXaxis().SetLabelSize(0.05)
hFrame.GetXaxis().SetLabelOffset(0.03)
hFrame.GetXaxis().SetTitle("Luminosity [cm^{-2}s^{-1}]")
hFrame.GetXaxis().SetTitleSize(0.05)
hFrame.GetXaxis().SetNdivisions(505)
hFrame.GetXaxis().SetTitleOffset(1.2)

hFrame.GetYaxis().SetLabelSize(0.05)
hFrame.GetYaxis().SetTitle("Efficiency [%]")
hFrame.GetYaxis().SetNdivisions(505)
hFrame.GetYaxis().SetTitleSize(0.05)
hFrame.GetYaxis().SetTitleOffset(1.1)

LR2D_15.SetMarkerSize(0.5)
LR2D_15.SetMarkerColor(kRed)
LR2D_15.SetMarkerStyle(24)
LR2D_16.SetMarkerSize(0.5)
LR2D_16.SetMarkerColor(kGreen)
LR2D_16.SetMarkerStyle(25)
LR2D_17.SetMarkerSize(0.5)
LR2D_17.SetMarkerColor(kBlue)
LR2D_17.SetMarkerStyle(26)
LR2D_18.SetMarkerSize(0.5)
LR2D_18.SetMarkerColor(kBlack)
LR2D_18.SetMarkerStyle(30)

LR2D_17.Draw("Psame")
LR2D_16.Draw("Psame")
LR2D_15.Draw("Psame")
LR2D_18.Draw("Psame")

AllTitlename1 = TLatex(0.2,0.82,"#splitline{CMS}{#bf{#it{Preliminary}}}")
AllTitlename1.SetNDC()
AllTitlename1.SetTextFont(62)
AllTitlename1.SetTextAlign(11)
AllTitlename1.SetTextSize(0.05)
AllTitlename1.Draw("same")

DataTitlename = TLatex(0.70,0.94,"141.23 fb^{-1} (13TeV)")
DataTitlename.SetNDC()
DataTitlename.SetTextFont(42)
DataTitlename.SetTextAlign(11)
DataTitlename.SetTextSize(0.04)
DataTitlename.Draw("same")

leg = TLegend(0.65, 0.25, 0.90, 0.47)
#leg.SetNColumns(3)
leg.SetFillStyle(0)
leg.SetBorderSize(0)

leg.AddEntry(LR2D_15, "2015 Data", "p")
leg.AddEntry(LR2D_16, "2016 Data", "p")
leg.AddEntry(LR2D_17, "2017 Data", "p")
leg.AddEntry(LR2D_18, "2018 Data", "p")

leg.Draw("same")
'''
#Fitting = TLatex(0.2,0.22,"#splitline{#splitline{Slope of 2018 data : -1.09 x 10^{-34}}{Luminosity at Eff 0 : 8.90 x 10^{35}}}{Expected Eff of HL LHC : 87.95%}")
Fitting = TLatex(0.2,0.32,"Slope of 2018 data : -1.09 x 10^{-34}")
Fitting.SetNDC()
Fitting.SetTextFont(42)
Fitting.SetTextAlign(11)
Fitting.SetTextSize(0.04)
Fitting.Draw("same")
'''

c.Print("Lumi_Eff.png")
c.Print("Lumi_Eff.pdf")
c.Print("Lumi_Eff.C")

