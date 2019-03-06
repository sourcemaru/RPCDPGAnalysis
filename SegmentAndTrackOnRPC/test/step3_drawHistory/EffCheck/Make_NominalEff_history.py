#!/usr/bin/env python

# Version to make nominal efficiency history run by run
# First, set sum all den & num
# Second, calculate average use sum_num/sum_den
# Use Clopper-Pearson to set error bar

import sys, os
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadBottomMargin(0.4)
gStyle.SetPadTopMargin(0.1)
gStyle.SetPadRightMargin(0.03)
gStyle.SetPadLeftMargin(0.04)

hist = {}
grps = {}
cat4history = {}

nZeroEff = {}
nNonZeroEff = {}
nHighEff = {}

Endcap_hist = TGraphAsymmErrors()
Barrel_hist = TGraphAsymmErrors()
NRE4_hist = TGraphAsymmErrors()

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

    Endcap_DenSum = 0
    Endcap_NumSum = 0
    Barrel_DenSum = 0
    Barrel_NumSum = 0
    RE_DenSum = 0
    RE_NumSum = 0

    zeros = 0

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if den == 0: continue

        effLo = TEfficiency.ClopperPearson(den, num, 0.683, False)

        if effLo < 0.01: continue

#        if name.startswith('R'):
#            Endcap_DenSum += den
#            Endcap_NumSum += num
#            ED_sum += den
#            EN_sum += num
        if name.startswith('RE-4') or name.startswith('RE+4'):
            RE_DenSum += den
            RE_NumSum += num
        elif name.startswith('R'):
            Endcap_DenSum += den
            Endcap_NumSum += num
            ED_sum += den
            EN_sum += num
        elif name.startswith('W'):
            Barrel_DenSum += den
            Barrel_NumSum += num
            BD_sum += den
            BN_sum += num

    if Endcap_DenSum == 0 : Endcap_eff = -1
    else : 
        Endcap_eff = Endcap_NumSum / Endcap_DenSum
        Endcap_effHi = TEfficiency.ClopperPearson(Endcap_DenSum, Endcap_NumSum, 0.683, True)
        Endcap_effLo = TEfficiency.ClopperPearson(Endcap_DenSum, Endcap_NumSum, 0.683, False)
        Endcap_errLo = abs(Endcap_eff - Endcap_effLo)
        Endcap_errHi = abs(Endcap_effHi - Endcap_eff)
        
    if Barrel_DenSum == 0 : Barrel_eff = -1
    else : 
        Barrel_eff = Barrel_NumSum / Barrel_DenSum
        Barrel_effHi = TEfficiency.ClopperPearson(Barrel_DenSum, Barrel_NumSum, 0.683, True)
        Barrel_effLo = TEfficiency.ClopperPearson(Barrel_DenSum, Barrel_NumSum, 0.683, False)
        Barrel_errLo = abs(Barrel_eff - Barrel_effLo)
        Barrel_errHi = abs(Barrel_effHi - Barrel_eff)

    if RE_DenSum == 0 : RE_eff = -1
    else :
        RE_eff = RE_NumSum / RE_DenSum
        RE_effHi = TEfficiency.ClopperPearson(RE_DenSum, RE_NumSum, 0.683, True)
        RE_effLo = TEfficiency.ClopperPearson(RE_DenSum, RE_NumSum, 0.683, False)
        RE_errLo = abs(RE_eff - RE_effLo)
        RE_errHi = abs(RE_effHi - RE_eff)


    ne = Endcap_hist.GetN()
    Endcap_hist.SetPoint(ne, irun+0.5, Endcap_eff*100)
    Endcap_hist.SetPointError(ne, 0, 0, Endcap_errLo*100, Endcap_errHi*100)

    nb = Barrel_hist.GetN()
    Barrel_hist.SetPoint(nb, irun+0.5, Barrel_eff*100)
    Barrel_hist.SetPointError(nb, 0, 0, Barrel_errLo*100, Barrel_errHi*100)

    nRE4 = NRE4_hist.GetN()
    NRE4_hist.SetPoint(nRE4, irun+0.5, RE_eff*100)
    NRE4_hist.SetPointError(nRE4, 0, 0, RE_errLo*100, RE_errHi*100)

Endcap_totalmean = EN_sum/ED_sum * 100
Barrel_totalmean = BN_sum/BD_sum * 100

cHistories = [TCanvas("cHistory%d" % i) for i in range(3)]
cHistories[2].SetCanvasSize(3300,400)
cHistories[2].SetWindowSize(3200,400)
hHistoryFrame = TH1F("hHistoryFrame", "hHistoryFrame", nRun, 0, nRun)
hHistoryFrame.SetMaximum(100.02)
hHistoryFrame.SetMinimum(80)

for i, run in enumerate(runs):
    #hHistoryFrame.GetXaxis().SetBinLabel(i+1, "%d" % run)
    
    if run == 273150 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "11 May (16B)")
    if run == 275657 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "24 Jun (16C)")
    if run == 276315 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "04 Jul (16D)")
    if run == 276831 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "16 Jul (16E)")
    if run == 277981 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "01 Aug (16F)")
    if run == 278820 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "14 Aug (16G)")
    if run == 281613 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "25 Sep (16H)")
    
    if run == 297050 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "16 Jun (17B)") 
    if run == 299368 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "18 Jul (17C)") 
    if run == 302031 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "30 Aug (17D)")
    if run == 303824 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "24 Sep (17E)")
    if run == 305044 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "13 Oct (17F)")
   
    if run == 315488 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "30 Apr (18A)")
    if run == 317080 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "28 May (18B)")
    if run == 319337 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "08 Jul (18C)")
    if run == 321475 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "20 Aug (18D)")

    hHistoryFrame.GetXaxis().SetLabelSize(0.1)

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
Endcap_hist.SetMarkerStyle(24)
Endcap_hist.SetMarkerColor(kBlue+1)
Endcap_hist.SetMarkerSize(.7)
Endcap_hist.Draw("Psame")

Barrel_hist.SetMinimum(0)
Barrel_hist.SetMarkerStyle(26)
Barrel_hist.SetMarkerColor(kRed)
Barrel_hist.SetMarkerSize(.7)
Barrel_hist.Draw("Psame")

NRE4_hist.SetMinimum(0)
NRE4_hist.SetMarkerStyle(25)
NRE4_hist.SetMarkerColor(kGreen)
NRE4_hist.SetMarkerSize(.7)
NRE4_hist.Draw("Psame")

AllTitlename = TLatex(0.5,0.945,"RPC Run2 Efficiency History")
AllTitlename.SetNDC()
AllTitlename.SetTextFont(52)
AllTitlename.SetTextAlign(21)
AllTitlename.SetTextSize(0.05)
AllTitlename.Draw("same")

leg = TLegend(0.065, 0.5, 0.16, 0.63)
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.AddEntry(Endcap_hist, "Endcap, Mean = %.2f%%" %Endcap_totalmean, "p")
leg.AddEntry(Barrel_hist, "Barrel, Mean = %.2f%%" %Barrel_totalmean, "p")
leg.AddEntry(NRE4_hist, "RE4", "p")
leg.Draw("same")

c.Modified()
c.Update()
c.Write()

'''    
f.Close()
#f.Write()
'''
'''
Barrel_eff = 0
Barrel_effHi = TEfficiency.ClopperPearson(17, 0, 0.683, True)
Barrel_errLo = abs(Barrel_eff - TEfficiency.ClopperPearson(17, 0, 0.683, False))
Barrel_errHi = abs(Barrel_effHi - Barrel_eff)

print Barrel_eff, Barrel_effHi, Barrel_errLo, Barrel_errHi
'''
