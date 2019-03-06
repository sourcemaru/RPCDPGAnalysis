#!/usr/bin/env python

import sys, os
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadBottomMargin(0.15)

hist = {}
grps = {}
cat4history = {}

nZeroEff = {}
nNonZeroEff = {}
nHighEff = {}

runs = []
for line in open(sys.argv[1]).readlines():
    line = line.strip()
    if len(line) == 0 or line.startswith('#'): continue
    name = line.split()[0]

    hist[name] = TH1F("%s" % name, ";Efficiency;", 100, 0, 1)
    grps[name] = TGraphAsymmErrors()
    grps[name].SetTitle(name)
    grps[name].SetMarkerStyle(kFullCircle)
    grps[name].SetMarkerSize(0.5)
    grps[name].SetEditable(False)
    nZeroEff[name] = 0
    nNonZeroEff[name] = 0
    nHighEff[name] = 0

for fName in sys.argv[1:]:
    runs.append(int(os.path.basename(fName).split('.')[0][3:]))
nRun = len(runs)
runs.sort()

f = TFile("test.root", "recreate")
for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    #if run == 317297 or run == 317591 : continue
    irun = runs.index(run)
    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if den == 0: continue

        if name not in cat4history: cat4history[name] = []

        eff = num/den
        effHi = TEfficiency.ClopperPearson(den, num, 0.683, True)
        errLo = abs(eff - TEfficiency.ClopperPearson(den, num, 0.683, False))
        errHi = abs(effHi - eff)

        if max(errLo, errHi) > 0.1: continue
        
        if eff == 0:
        #if eff-errLo < 0.01:
            nZeroEff[name] += 1
        else:
            nNonZeroEff[name] += 1
            if effHi >  0.7 : nHighEff[name] += 1

        hist[name].Fill(eff)

        cat4history[name].append(eff)

        np = grps[name].GetN()
        grps[name].SetPoint(np, irun+0.5, eff)
        #grps[name].SetPointError(np, 0, 0, errLo, errHi)

'''
for name in hist:
    hist[name].Write()
'''
#f.Close()

l1 = []
l2 = []
l3 = []
l4 = []

#a = TCanvas("c","WOW", 800, 400)
#h = TH1F("h", ";Efficiency;", 100, 0, 1)
#h.SetMaximum(1)

#h.Draw()

cHistories = [TCanvas("cHistory%d" % i) for i in range(4)]
hHistoryFrame = TH1F("hHistoryFrame", "hHistoryFrame", nRun, 0, nRun)

for i, run in enumerate(runs):
    '''
    if i % 10 != 0: continue
    hHistoryFrame.GetXaxis().SetBinLabel(i+1, "%d" % run)
    '''
    '''
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
    if run == 320500 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "30Jul2018 (18D)")
    '''
    if run == 320673 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "01Aug2018 (18D)")
    if run == 321461 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "DCSissueOver")
    if run == 321475 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "20Aug2018")
    if run == 321908 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "28Aug2018")
    if run == 322633 : hHistoryFrame.GetXaxis().SetBinLabel(i+1, "10Sep2018")

for c in cHistories:
    c.cd()
    hHistoryFrame.Draw()

for name in hist:
    if nNonZeroEff[name] == 0:
        l1.append(name)
        hist[name].SetLineColor(kRed)
        hist[name].Draw("same")
        cHistories[0].cd()
        grps[name].SetLineColor(kRed)
        grps[name].SetMarkerColor(kRed)
        grps[name].Draw("LP")
    elif nHighEff[name] == nNonZeroEff[name]:
        if nZeroEff[name] == 0:
            l2.append(name)
            hist[name].SetLineColor(kBlue)
            hist[name].Draw("same")
            cHistories[1].cd()
            grps[name].SetLineColor(kBlue)
            grps[name].SetMarkerColor(kBlue)
            grps[name].Draw("LP")
        else:
            l3.append(name)
            hist[name].SetLineColor(kBlack)
            hist[name].Draw("same")
            cHistories[2].cd()
            grps[name].SetLineColor(kBlack)
            grps[name].SetMarkerColor(kBlack)
            grps[name].Draw("LP")
    else:
        l4.append(name)
        hist[name].SetLineColor(kGreen+1)
        hist[name].Draw("same")
        cHistories[3].cd()
        grps[name].SetLineColor(kGreen+1)
        grps[name].SetMarkerColor(kGreen+1)
        grps[name].Draw("LP")

print len(l1), len(l2), len(l3), len(l4)

grpOverlay = None

# If want to show category4, change all to 4 and cHistories number to 3
for index, name in enumerate(l4):
    if name not in l4: continue

    c = cHistories[3]

    c.cd()

    grpOverlay = grps[name].Clone()
    grpOverlay.SetLineColor(kRed+1)
    grpOverlay.SetMarkerColor(kRed+1)
    grpOverlay.SetLineWidth(3)
    grpOverlay.Draw("LPsame")

    c.SetName("%03d_%s" % (index, name))
    hHistoryFrame.SetTitle("%s" % name)

    c.Modified()
    c.Update()
    c.Write()

f.Close()

#f.Write()
