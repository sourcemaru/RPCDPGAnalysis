#!/usr/bin/env python

import sys, os
from ROOT import *
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

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

f = TFile("hist.root", "recreate")
for fName in sys.argv[1:]:
    run = int(os.path.basename(fName).split('.')[0][3:])
    #if run == 317297 or run == 317591 or run == 305589 : continue
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

        if eff-errLo < 0.01:
        #if eff == 0:
            nZeroEff[name] += 1
        else:
            nNonZeroEff[name] += 1
            if effHi >  0.7 : nHighEff[name] += 1

        hist[name].Fill(eff)

        cat4history[name].append(eff)

        np = grps[name].GetN()
        grps[name].SetPoint(np, irun+0.5, eff)
        #grps[name].SetPointError(np, 0, 0, errLo, errHi)

for name in hist:
    hist[name].Write()

f.Close()

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
        #hist[name].Draw("same")
        cHistories[0].cd()
        grps[name].SetLineColor(kRed)
        grps[name].SetMarkerColor(kRed)
        grps[name].Draw("LP")
    elif nHighEff[name] == nNonZeroEff[name]:
        if nZeroEff[name] == 0:
            l2.append(name)
            hist[name].SetLineColor(kBlue)
            #hist[name].Draw("same")
            cHistories[1].cd()
            grps[name].SetLineColor(kBlue)
            grps[name].SetMarkerColor(kBlue)
            grps[name].Draw("LP")
        else:
            l3.append(name)
            hist[name].SetLineColor(kBlack)
            #hist[name].Draw("same")
            cHistories[2].cd()
            grps[name].SetLineColor(kBlack)
            grps[name].SetMarkerColor(kBlack)
            grps[name].Draw("LP")
    else:
        l4.append(name)
        hist[name].SetLineColor(kGreen+1)
        #hist[name].Draw("same")
        cHistories[3].cd()
        grps[name].SetLineColor(kGreen+1)
        grps[name].SetMarkerColor(kGreen+1)
        grps[name].Draw("LP")

print(len(l1), len(l2), len(l3), len(l4))

f1 = open("Cat2018_2.txt",'w')

for name in l1:
    linename = name + "  1\n"
    f1.write(linename)
for name in l2:
    linename = name + "  2\n"
    f1.write(linename)
for name in l3:
    linename = name + "  3\n"
    f1.write(linename)
for name in l4:
    linename = name + "  4\n"
    f1.write(linename)

f1.close()

for c in cHistories:
    c.Modified()
    c.Update()

#f.Write()
