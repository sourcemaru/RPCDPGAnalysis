#!/usr/bin/env python3

import sys, os
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

hist = {}
grps = {}

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

cat3check = {}

minEffs = {}
#f = TFile("hist.root", "recreate")
for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    irun = runs.index(run)
    for line in open(fName).readlines():
        line = line.strip()
        if len(line) == 0 or line.startswith('#'): continue
        name, den, num = line.split()
        den, num = float(den), float(num)

        if name not in cat3check : cat3check[name] = []

        if den == 0: continue

        eff = num/den
        effHi = TEfficiency.ClopperPearson(den, num, 0.683, True)
        errLo = abs(eff - TEfficiency.ClopperPearson(den, num, 0.683, False))
        errHi = abs(effHi - eff)

        if max(errLo, errHi) > 0.1: continue

        if eff == 0:
            nZeroEff[name] += 1
        else:
            nNonZeroEff[name] += 1
            if effHi >  0.7 : nHighEff[name] += 1

        hist[name].Fill(eff)

        if eff != 0 : cat3check[name].append(eff)

        np = grps[name].GetN()
        grps[name].SetPoint(np, irun+0.5, eff)
        #grps[name].SetPointError(np, 0, 0, errLo, errHi)

        if name in minEffs: 
            minEffs[name] = min(minEffs[name], eff)
        else:
            minEffs[name] = eff

minEffs = list(zip(list(minEffs.keys()), list(minEffs.values())))
minEffs.sort(key=lambda x: x[1])
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
    if i % 10 != 0: continue
    hHistoryFrame.GetXaxis().SetBinLabel(i+1, "%d" % run)
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

print(len(l1), len(l2), len(l3), len(l4))

summation = 0

for name in cat3check:
    if name in l3: 
        for i in range(len(cat3check[name])):
            summation += cat3check[name][i]
        mean = summation / len(cat3check[name])
        print(name, len(cat3check[name]), mean)
        
        summation = 0

'''
f = TFile("hist_cat2.root", "recreate")

grpOverlay = None

for index, (name, eff) in enumerate(minEffs):
    if name not in l2: continue

    c = cHistories[1]

    c.cd()
    hHistoryFrame.SetTitle("%03d_%s" % (index, name))

    grpOverlay = grps[name].Clone()
    grpOverlay.SetLineColor(kRed+1)
    grpOverlay.SetMarkerColor(kRed+1)
    grpOverlay.SetLineWidth(3)
    grpOverlay.Draw("LPsame")

    c.SetName("%03d_%s" % (index, name))

    c.Modified()
    c.Update()
    c.Write()
    
f.Close()
'''

#f.Write()
