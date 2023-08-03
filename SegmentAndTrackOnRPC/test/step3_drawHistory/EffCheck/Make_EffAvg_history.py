#!/usr/bin/env python3

# Version to make nominal efficiency history run by run
# First, set average = num/den
# Second, calculate average of average
# Use rms of average to set error bar

import sys, os
from ROOT import *
from math import sqrt
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadBottomMargin(0.15)
gStyle.SetPadTopMargin(0.13)
gStyle.SetPadRightMargin(0.03)
gStyle.SetPadLeftMargin(0.05)

hist = {}
grps = {}
cat4history = {}

nZeroEff = {}
nNonZeroEff = {}
nHighEff = {}

Endcap_hist = TGraphErrors()
Barrel_hist = TGraphErrors()
NRE4_hist = TGraphErrors()

runs = []
for line in open(sys.argv[1]).readlines():
    line = line.strip()
    if len(line) == 0 or line.startswith('#'): continue
    name = line.split()[0]

    hist[name] = TH1F("%s" % name, ";Efficiency;", 100, 0, 1)

for fName in sys.argv[1:]:
    runs.append(int(os.path.basename(fName).split('.')[0][3:]))
nRun = len(runs)
runs.sort()

ED_sum = 0
EN_sum = 0
BD_sum = 0
BN_sum = 0

f = TFile("hist.root", "recreate")
for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    Endcap_avgsum = 0
    Endcap_avg2sum = 0
    Endcap_number = 0
    Endcap_densum = 0
    Barrel_avgsum = 0
    Barrel_avg2sum = 0
    Barrel_number = 0
    Barrel_densum = 0
    RE_avgsum = 0
    RE_avg2sum = 0
    RE_number = 0
    RE_densum = 0

    zeros = 0

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if den == 0: continue

	avg = 100*num/den
        avg2 = avg**2
	if avg == 0: continue

#       if name.startswith('R'):
#           Endcap_DenSum += den
#           Endcap_NumSum += num
#           ED_sum += den
#           EN_sum += num
        if name.startswith('RE-4') or name.startswith('RE+4'):
            RE_avgsum += avg
            RE_avg2sum += avg2
	    RE_number += 1
            RE_densum += den
        elif name.startswith('R'):
            Endcap_avgsum += avg
            Endcap_avg2sum += avg2
            Endcap_number += 1
            Endcap_densum += den
        elif name.startswith('W'):
            Barrel_avgsum += avg
            Barrel_avg2sum += avg2
            Barrel_number += 1
            Barrel_densum += den

    if Endcap_densum == 0 : Endcap_eff = -1
    else : 
        Endcap_eff = Endcap_avgsum / Endcap_number
        Endcap_err = sqrt(Endcap_avg2sum/Endcap_number - Endcap_eff**2)
        
    if Barrel_densum == 0 : Barrel_eff = -1
    else : 
        Barrel_eff = Barrel_avgsum / Barrel_number
        Barrel_err = sqrt(Barrel_avg2sum/Barrel_number - Barrel_eff**2)

    if RE_densum == 0 : RE_eff = -1
    else :
        RE_eff = RE_avgsum / RE_number
        RE_err = sqrt(RE_avg2sum/RE_number - RE_eff**2)

    ne = Endcap_hist.GetN()
    Endcap_hist.SetPoint(ne, irun+0.5, Endcap_eff)
    #Endcap_hist.SetPointError(ne, 0, Endcap_err)

    nb = Barrel_hist.GetN()
    Barrel_hist.SetPoint(nb, irun+0.5, Barrel_eff)
    #Barrel_hist.SetPointError(ne, 0, Barrel_err)

    nRE4 = NRE4_hist.GetN()
    NRE4_hist.SetPoint(nRE4, irun+0.5, RE_eff)
    #nRE4_hist.SetPointError(ne, 0, RE_err)

cHistories = [TCanvas("cHistory%d" % i) for i in range(3)]
cHistories[2].SetCanvasSize(3300,900)
cHistories[2].SetWindowSize(3200,900)
hHistoryFrame = TH1F("hHistoryFrame", "hHistoryFrame", nRun, 0, nRun)
hHistoryFrame.SetMaximum(100.5)
hHistoryFrame.SetMinimum(80)

for i, run in enumerate(runs):
    #hHistoryFrame.GetXaxis().SetBinLabel(i+1, "%d" % run)
    if run >= 284066 and run <= 285366 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "HV SCAN")
    '''
    # For 2015
    if run == 251168 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "Run2015")
    if run == 254277 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD1")
    if run == 257969 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD2")
    if run == 258287 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "TS2")

    # For 2016
    if run == 273150 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "Run2016")
    if run == 274954 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "TS1")
    if run == 277981 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD1")
    if run == 279588 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD2")
    if run == 281613 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD3, TS2")
    if run == 282708 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD4")

    # For 2017
    if run == 297050 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "Run2017")
    if run == 298996 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD1, TS1")
    if run == 300087 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD2")
    if run == 303824 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD3, TS2")
   
    # For 2018 
    if run == 315488 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "Run2018")
    if run == 318733 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD1, TS1")
    if run == 321887 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD2")
    if run == 323414 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "MD3, TS2")
    '''
hHistoryFrame.GetXaxis().SetLabelSize(0.05)
hHistoryFrame.GetXaxis().SetLabelOffset(0.005)

hHistoryFrame.GetYaxis().SetLabelSize(0.04)
hHistoryFrame.GetYaxis().SetTitle("Efficiency [%]")
hHistoryFrame.GetYaxis().SetNdivisions(505)
hHistoryFrame.GetYaxis().SetTitleSize(0.06)
hHistoryFrame.GetYaxis().SetTitleOffset(0.38)

for c in cHistories:
    c.cd()
    hHistoryFrame.Draw()

# Endcap Efficiency History Setting
cHistories[0].cd()
cHistories[0].SetName("Endcap_history")
hHistoryFrame.SetTitle("Endcap_history")

Endcap_hist.SetMinimum(0)
Endcap_hist.SetMarkerStyle(20)
Endcap_hist.SetMarkerColor(kBlue+1)
Endcap_hist.SetMarkerSize(.5)
Endcap_hist.Draw("Psame")

ETitlename = TLatex(0.5,0.945,"RPC Endcap : Run2 Efficiency History")
ETitlename.SetNDC()
ETitlename.SetTextFont(52)
ETitlename.SetTextAlign(21)
ETitlename.SetTextSize(0.05)
ETitlename.Draw("same")

# Barrel Efficiency History Setting
cHistories[1].cd()
cHistories[1].SetName("Barrel_history")
hHistoryFrame.SetTitle("Barrel_history")

Barrel_hist.SetMinimum(0)
Barrel_hist.SetMarkerStyle(20)
Barrel_hist.SetMarkerColor(kGreen+1)
Barrel_hist.SetMarkerSize(.5)
Barrel_hist.Draw("Psame")

BTitlename = TLatex(0.5,0.945,"RPC Barrel : Run2 Efficiency History")
BTitlename.SetNDC()
BTitlename.SetTextFont(52)
BTitlename.SetTextAlign(21)
BTitlename.SetTextSize(0.05)
BTitlename.Draw("same")

# Endcap + Barrel Efficiency History Setting
cHistories[2].cd()
cHistories[2].SetName("Efficiency History")
hHistoryFrame.SetTitle("Efficiency History")

Endcap_hist.SetMinimum(0)
Endcap_hist.SetMarkerStyle(20)
Endcap_hist.SetMarkerColorAlpha(4, 0.5)
Endcap_hist.SetMarkerSize(1.5)
Endcap_hist.Draw("Psame")

Barrel_hist.SetMinimum(0)
Barrel_hist.SetMarkerStyle(22)
Barrel_hist.SetMarkerColorAlpha(2, 0.5)
Barrel_hist.SetMarkerSize(1.5)
Barrel_hist.Draw("Psame")

NRE4_hist.SetMinimum(0)
NRE4_hist.SetMarkerStyle(21)
NRE4_hist.SetMarkerColorAlpha(8,0.5)
NRE4_hist.SetMarkerSize(1.5)
NRE4_hist.Draw("Psame")

AllTitlename1 = TLatex(0.05,0.9,"CMS #bf{#it{Preliminary}}")
AllTitlename1.SetNDC()
AllTitlename1.SetTextFont(62)
AllTitlename1.SetTextAlign(11)
AllTitlename1.SetTextSize(0.1)
AllTitlename1.Draw("same")

DataTitlename = TLatex(0.76,0.9,"Run2 data, 141.23 fb^{-1} (13TeV)")
DataTitlename.SetNDC()
DataTitlename.SetTextFont(42)
DataTitlename.SetTextAlign(11)
DataTitlename.SetTextSize(0.06)
DataTitlename.Draw("same")

leg = TLegend(0.1, 0.25, 0.3, 0.3)
leg.SetNColumns(3)
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.AddEntry(Barrel_hist, "Barrel", "p")
leg.AddEntry(Endcap_hist, "Endcap", "p")
leg.AddEntry(NRE4_hist, "RE4", "p")
#leg.SetTextSize(0.01)
leg.Draw("same")

c.Modified()
c.Update()
c.Write()
