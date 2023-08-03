#!/usr/bin/env python3

import sys, os
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadBottomMargin(0.2)

hist = {}
grps = {}
cat4history = {}

nZeroEff = {}
nNonZeroEff = {}
nHighEff = {}

Endcap_hist = TGraphAsymmErrors()
Barrel_hist = TGraphAsymmErrors()
Zeros_hist = TGraphAsymmErrors()

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

f = TFile("hist.root", "recreate")
for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)

    Endcap_DenSum = 0
    Endcap_NumSum = 0
    Barrel_DenSum = 0
    Barrel_NumSum = 0

    zeros = 0

    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if den == 0: continue

        if name.startswith('R'):
            Endcap_DenSum += den
            Endcap_NumSum += num
        elif name.startswith('W'):
	#elif name[4:7] == 'RB1':
            Barrel_DenSum += den
            Barrel_NumSum += num
        if den > 17 and num == 0 : zeros += 1

    if Endcap_DenSum == 0 : Endcap_eff = -1
    else : 
        Endcap_eff = Endcap_NumSum / Endcap_DenSum
        Endcap_effHi = TEfficiency.ClopperPearson(Endcap_DenSum, Endcap_NumSum, 0.683, True)
        Endcap_errLo = abs(Endcap_eff - TEfficiency.ClopperPearson(Endcap_DenSum, Endcap_NumSum, 0.683, False))
        Endcap_errHi = abs(Endcap_effHi - Endcap_eff)

    if Barrel_DenSum == 0 : Barrel_eff = -1
    else : 
        Barrel_eff = Barrel_NumSum / Barrel_DenSum
        Barrel_effHi = TEfficiency.ClopperPearson(Barrel_DenSum, Barrel_NumSum, 0.683, True)
        Barrel_errLo = abs(Barrel_eff - TEfficiency.ClopperPearson(Barrel_DenSum, Barrel_NumSum, 0.683, False))
        Barrel_errHi = abs(Barrel_effHi - Barrel_eff)

    ne = Endcap_hist.GetN()
    Endcap_hist.SetPoint(ne, irun+0.5, Endcap_eff)
    Endcap_hist.SetPointError(ne, 0, 0, Endcap_errLo, Endcap_errHi)

    nb = Barrel_hist.GetN()
    Barrel_hist.SetPoint(nb, irun+0.5, Barrel_eff)
    Barrel_hist.SetPointError(nb, 0, 0, Barrel_errLo, Barrel_errHi)

    nz = Zeros_hist.GetN()
    Zeros_hist.SetPoint(nz, irun+0.5, zeros)

cHistories = [TCanvas("cHistory%d" % i) for i in range(3)]
hHistoryFrame = TH1F("hHistoryFrame", "hHistoryFrame", nRun, 0, nRun)



for i, run in enumerate(runs):
    #hHistoryFrame.GetXaxis().SetBinLabel(i+1, "%d" % run)
    
    if run == 274954 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "11Jun2016 (16TS1)")
    if run == 281613 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "25Sep2016 (16TS2)")
    if run == 297050 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "16Jun2017 (16TS3, 17B)")
    if run == 298996 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "14Jul2017 (17TS1)")
    if run == 303824 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "24Sep2017 (17TS2, 17E)")
    if run == 318733 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "26Jun2018 (18TS1)")
     
    if run == 281613 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "25Sep2016 (16TS1, WP, 16F)")
 
    if run == 273150 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "11May2016 (16B)")
    if run == 275657 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "24Jun2016 (16C)")
    if run == 276315 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "04Jul2016 (16D)")
    if run == 276831 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "16Jul2016 (16E)")
    if run == 277981 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "01Aug2016 (16F)")
    if run == 278820 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "14Aug2016 (16G)")
    #if run == 281613 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "25Sep2016 (16F)")
     
    #if run == 297050 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "16Jun2017 (17B)")
    if run == 299368 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "18Jul2017 (17C)") 
    if run == 302031 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "30Aug2017 (17D)")
    #if run == 303824 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "24Sep2017 (17E)")
    if run == 305044 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "13Oct2017 (17F)")
  
    if run == 315257 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "26Apr2018 (18A)")
    if run == 317080 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "28May2018 (18B)")
    if run == 319337 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "08Jul2018 (18C)")
    

for c in cHistories:
    c.cd()
    hHistoryFrame.Draw()

cHistories[0].cd()
cHistories[0].SetName("Endcap_history")
hHistoryFrame.SetTitle("Endcap_history")

Endcap_hist.SetMinimum(0)
Endcap_hist.SetMarkerStyle(20)
Endcap_hist.SetMarkerColor(kBlue+1)
Endcap_hist.SetMarkerSize(.5)
Endcap_hist.Draw("Psame")

cHistories[1].cd()
cHistories[1].SetName("Barrel_history")
hHistoryFrame.SetTitle("Barrel_history")

Barrel_hist.SetMinimum(0)
Barrel_hist.SetMarkerStyle(20)
Barrel_hist.SetMarkerColor(kGreen+1)
Barrel_hist.SetMarkerSize(.5)
Barrel_hist.Draw("Psame")
'''
cHistories[2].cd()
cHistories[2].SetName("Number of Zeros")
hHistoryFrame.SetMaximum(500)
hHistoryFrame.Draw()
Zeros_hist.SetMaximum(500)
Zeros_hist.SetMarkerStyle(20)
Zeros_hist.SetMarkerColor(kBlack)
Zeros_hist.SetMarkerSize(.5)
Zeros_hist.Draw("Psame")
'''
'''
c.Modified()
c.Update()
c.Write()
    


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
