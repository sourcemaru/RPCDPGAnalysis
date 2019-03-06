#!/usr/bin/env python

import sys, os
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadTopMargin(0.13)
gStyle.SetPadRightMargin(0.1)
gStyle.SetPadLeftMargin(0.05)

runs = []
for line in open(sys.argv[1]).readlines():
    line = line.strip()
    if len(line) == 0 or line.startswith('#'): continue
    name = line.split()[0]

    #hist[name] = TH1F("%s" % name, ";Efficiency;", 100, 0, 1)

for fName in sys.argv[1:]:
    runs.append(int(os.path.basename(fName).split('.')[0][3:]))
nRun = len(runs)
runs.sort()

DenSEP = TH1F("DENsep", "DENsep", 300, 0, 300)
DenAVG = TH1F("DENsvg", "DENsvg", 300, 0, 300)
DenAVG1 = TH1F("DENsvg1", "DENsvg1", 300, 0, 300)
DenAVG2 = TH1F("DENsvg2", "DENsvg2", 300, 0, 300)
DenAVG3 = TH1F("DENsvg3", "DENsvg3", 300, 0, 300)

DenZero = TH1F("DZ", "DZ", nRun, 0, nRun)
Eff100 = TH1F("Eff100", "Eff100", nRun, 0, nRun)
Good1Eff = TH1F("GE1", "GE1", nRun, 0, nRun)
Good2Eff = TH1F("GE2", "GE2", nRun, 0, nRun)
Good3Eff = TH1F("GE3", "GE3", nRun, 0, nRun)
LowEff = TH1F("LE", "LE", nRun, 0, nRun)
ZeroEff = TH1F("ZE", "ZE", nRun, 0, nRun)

GGrat = TH1F("GG", "GG", nRun, 0, nRun)
Good1rat = TH1F("GR1", "GR1", nRun, 0, nRun)
Good2rat = TH1F("GR2", "GR2", nRun, 0, nRun)
Good3rat = TH1F("GR3", "GR3", nRun, 0, nRun)
Lowrat = TH1F("LR", "LR", nRun, 0, nRun)
Zerorat = TH1F("ZR", "ZR", nRun, 0, nRun)

EffStack = THStack("hs","hs")
EffStack2 = THStack("hs2","hs2")

runinx = 0

for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    densum = 0
    densum1 = 0
    densum2 = 0
    densum3 = 0
    linenum = 0
    linenum1 = 0
    linenum2 = 0
    linenum3 = 0

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)
        
        DenSEP.Fill(den)

        densum += den
        linenum += 1

        if name.startswith("RE+4") or name.startswith("RE-4"):
            densum3 += den
            linenum3 += 1
        elif name.startswith("R"):
            densum2 += den
            linenum2 += 1
        else:
            densum1 += den
            linenum1 += 1
     
    DenAVG.Fill(densum/linenum)
    DenAVG1.Fill(densum1/linenum1)
    DenAVG2.Fill(densum2/linenum2)
    DenAVG3.Fill(densum3/linenum3)

    if densum/linenum < 0:
        runinx += 1   
        continue

    Eff100n = 0.
    GE1n = 0.
    GE2n = 0.
    GE3n = 0.
    LEn = 0.
    ZEn = 0.

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if den == 0:
            DenZero.Fill(runinx)
            continue
	    
        avg = 100*num/den
        
        if den < 0 and avg == 100:
	    Eff100.Fill(runinx)
            Eff100n += 1
	elif avg >= 95:
            Good1Eff.Fill(runinx)
            GE1n += 1
        elif avg >= 90:
            Good2Eff.Fill(runinx)
            GE2n += 1
        elif avg >= 70:
            Good3Eff.Fill(runinx)
            GE3n += 1
        elif avg >= 1:
            LowEff.Fill(runinx)
            LEn += 1
        else:
            ZeroEff.Fill(runinx)
            ZEn += 1

    ## Set 105 not 100, because of half-up problem            
    GLZsum = GE1n + GE2n + GE3n + LEn + ZEn
    if GLZsum == 0: 
        GG = 105
        for i4 in range(105):
            GGrat.Fill(runinx)
    else:
        GE1r = GE1n / GLZsum * 105
        GE2r = GE2n / GLZsum * 105
        GE3r = GE3n / GLZsum * 105
        LEr = LEn / GLZsum * 105
        ZEr = ZEn / GLZsum * 105

        for i1 in range(int(round(GE1r, 1))):
            Good1rat.Fill(runinx)
        for i2 in range(int(round(GE2r, 1))):
            Good2rat.Fill(runinx)
        for i3 in range(int(round(GE3r, 1))):
            Good3rat.Fill(runinx)
        for j in range(int(round(LEr, 1))):
            Lowrat.Fill(runinx)
        for k in range(int(round(ZEr, 1))):
            Zerorat.Fill(runinx)       

    runinx += 1

cHistories = [TCanvas("cHistory%d" % i) for i in range(4)]
cHistories[0].SetCanvasSize(3300,900)
cHistories[0].SetWindowSize(3300,900)
cHistories[1].SetCanvasSize(3300,900)
cHistories[1].SetWindowSize(3300,900)
hHistoryFrame1 = TH1F("hHistoryFrame1", "hHistoryFrame1", nRun, 0, nRun)
hHistoryFrame2 = TH1F("hHistoryFrame2", "hHistoryFrame2", nRun, 0, nRun)
hHistoryFrame1.SetMaximum(2800)
hHistoryFrame2.SetMaximum(100)

for i, run in enumerate(runs):
    #if i % 20 == 0:
        #hHistoryFrame1.GetXaxis().SetBinLabel(i+1, "%d" % run)
        #hHistoryFrame2.GetXaxis().SetBinLabel(i+1, "%d" % run)

    for Framename in [hHistoryFrame1, hHistoryFrame2]:
        # For 2015
        if run == 251168 : Framename.GetXaxis().SetBinLabel(i+1, "Run2015")
        if run == 254277 : Framename.GetXaxis().SetBinLabel(i+1, "MD1")
        if run == 257969 : Framename.GetXaxis().SetBinLabel(i+1, "MD2")
        if run == 258287 : Framename.GetXaxis().SetBinLabel(i+1, "TS2")

        # For 2016
        if run == 273150 : Framename.GetXaxis().SetBinLabel(i+1, "Run2016")
        if run == 274954 : Framename.GetXaxis().SetBinLabel(i+1, "TS1")
        if run == 277981 : Framename.GetXaxis().SetBinLabel(i+1, "MD1")
        if run == 279588 : Framename.GetXaxis().SetBinLabel(i+1, "MD2")
        if run == 281613 : Framename.GetXaxis().SetBinLabel(i+1, "MD3, TS2")
        if run == 282708 : Framename.GetXaxis().SetBinLabel(i+1, "MD4")

        # For 2017
        if run == 297050 : Framename.GetXaxis().SetBinLabel(i+1, "Run2017")
        if run == 298996 : Framename.GetXaxis().SetBinLabel(i+1, "MD1, TS1")
        if run == 300087 : Framename.GetXaxis().SetBinLabel(i+1, "MD2")
        if run == 303824 : Framename.GetXaxis().SetBinLabel(i+1, "MD3, TS2")
    
        # For 2018 
        if run == 315488 : Framename.GetXaxis().SetBinLabel(i+1, "Run2018")
        if run == 318733 : Framename.GetXaxis().SetBinLabel(i+1, "MD1, TS1")
        if run == 321887 : Framename.GetXaxis().SetBinLabel(i+1, "MD2")
        if run == 323414 : Framename.GetXaxis().SetBinLabel(i+1, "MD3, TS2")

for Fname in [hHistoryFrame1, hHistoryFrame2]:
    Fname.GetXaxis().SetLabelSize(0.05)
    Fname.GetXaxis().SetLabelOffset(0.005)
    Fname.GetYaxis().SetLabelSize(0.04)
    if Fname == hHistoryFrame1 : Fname.GetYaxis().SetTitle("Number of Rolls")
    else : Fname.GetYaxis().SetTitle("Rolls ratio [%]")
    Fname.GetYaxis().SetNdivisions(505)
    Fname.GetYaxis().SetTitleSize(0.06)
    Fname.GetYaxis().SetTitleOffset(0.38)

hHistoryFrame1.GetYaxis().SetLabelSize(0.04)

'''
DenZero.Draw()
GoodEff.Draw("same")
LowEff.Draw("same")
ZeroEff.Draw("same")
'''

Eff100.SetFillColor(13)
Eff100.SetLineColor(13)
DenZero.SetFillColor(1)
DenZero.SetLineColor(1)
#DenZero.SetFillStyle(3002)
Good1Eff.SetFillColor(4)
Good1Eff.SetLineColor(4)
#Good1Eff.SetFillStyle(3002)
Good2Eff.SetFillColor(9)
Good2Eff.SetLineColor(9)
#Good2Eff.SetFillStyle(3002)
Good3Eff.SetFillColor(7)
Good3Eff.SetLineColor(7)
#Good3Eff.SetFillStyle(3002)
LowEff.SetFillColor(8)
LowEff.SetLineColor(8)
#LowEff.SetFillStyle(3002)
ZeroEff.SetFillColor(2)
ZeroEff.SetLineColor(2)
#ZeroEff.SetFillStyle(3002)

Good1rat.SetFillColor(4)
Good1rat.SetLineColor(4)
#Good1rat.SetFillStyle(3002)
Good2rat.SetFillColor(9)
Good2rat.SetLineColor(9)
#Good2rat.SetFillStyle(3002)
Good3rat.SetFillColor(7)
Good3rat.SetLineColor(7)
#Good3rat.SetFillStyle(3002)
Lowrat.SetFillColor(8)
Lowrat.SetLineColor(8)
#Lowrat.SetFillStyle(3002)
Zerorat.SetFillColor(2)
Zerorat.SetLineColor(2)
#Zerorat.SetFillStyle(3002)
GGrat.SetFillColor(1)
GGrat.SetLineColor(1)

AllTitlename1 = TLatex(0.05,0.9,"CMS #bf{#it{Preliminary}}")
AllTitlename1.SetNDC()
AllTitlename1.SetTextFont(62)
AllTitlename1.SetTextAlign(11)
AllTitlename1.SetTextSize(0.1)

DataTitlename = TLatex(0.69,0.9,"Run2 data, 141.23 fb^{-1} (13TeV)")
DataTitlename.SetNDC()
DataTitlename.SetTextFont(42)
DataTitlename.SetTextAlign(11)
DataTitlename.SetTextSize(0.06)

leg1 = TLegend(0.9, 0.27, 0.995, 0.79)
leg1.SetFillStyle(0)
leg1.SetBorderSize(0)
leg1.SetHeader("Efficiency", "C")
#leg1.AddEntry(Eff100, "100%(Stat.)", "f")
leg1.AddEntry(Good1Eff, "95 ~ 100%", "f")
leg1.AddEntry(Good2Eff, "90 ~ 95%", "f")
leg1.AddEntry(Good3Eff, "70 ~ 90%", "f")
leg1.AddEntry(LowEff, "1 ~ 70%", "f")
leg1.AddEntry(ZeroEff, "0 ~ 1%", "f")
leg1.AddEntry(DenZero, "Not Available", "f")
leg1.SetTextSize(0.045)

leg2 = TLegend(0.9, 0.27, 0.995, 0.79)
leg2.SetFillStyle(0)
leg2.SetBorderSize(0)
leg2.SetHeader("Efficiency", "C")
leg2.AddEntry(Good1rat, "95 ~ 100%", "f")
leg2.AddEntry(Good2rat, "90 ~ 95%", "f")
leg2.AddEntry(Good3rat, "70 ~ 90%", "f")
leg2.AddEntry(Lowrat, "1 ~ 70%", "f")
leg2.AddEntry(Zerorat, "0 ~ 1%", "f")
#leg2.AddEntry(GGrat, "Lack of Stat.", "f")
leg2.SetTextSize(0.045)

cHistories[0].cd()
hHistoryFrame1.Draw()
EffStack.Add(DenZero)
EffStack.Add(ZeroEff)
EffStack.Add(LowEff)
EffStack.Add(Good3Eff)
EffStack.Add(Good2Eff)
EffStack.Add(Good1Eff)
EffStack.Add(Eff100)
EffStack.Draw("same")
AllTitlename1.Draw("same")
DataTitlename.Draw("same")
leg1.Draw("same")

cHistories[1].cd()
hHistoryFrame2.Draw()
EffStack2.Add(GGrat)
EffStack2.Add(Zerorat)
EffStack2.Add(Lowrat)
EffStack2.Add(Good3rat)
EffStack2.Add(Good2rat)
EffStack2.Add(Good1rat)
EffStack2.Draw("same")
AllTitlename1.Draw("same")
DataTitlename.Draw("same")
leg2.Draw("same")

cHistories[2].cd()
DenAVG.SetFillColor(kBlack)
DenAVG.SetLineColor(kBlack)
#DenAVG.SetFillStyle(3020)
DenAVG.Draw()
DenAVG1.SetFillColor(kRed)
DenAVG1.SetLineColor(kRed)
DenAVG1.SetFillStyle(3002)
DenAVG1.Draw("same")
DenAVG2.SetFillColor(kBlue)
DenAVG2.SetLineColor(kBlue)
DenAVG2.SetFillStyle(3002)
DenAVG2.Draw("same")
DenAVG3.SetFillColor(kGreen)
DenAVG3.SetLineColor(kGreen)
DenAVG3.SetFillStyle(3002)
DenAVG3.Draw("same")

cHistories[3].cd()
DenSEP.SetFillColor(kRed)
DenSEP.SetFillStyle(3002)
DenSEP.Draw()
