#!/usr/bin/env python3

effMin, effMax = 80, 101
method = "avgPerRoll"
#method = "avgPerCount"

import sys, os
from ROOT import *
from math import sqrt
from glob import glob
from RPCDPGAnalysis.SegmentAndTrackOnRPC.buildLabels import *

resultDir = "results/history"
if not os.path.exists(resultDir): os.makedirs(resultDir)

from RPCDPGAnalysis.SegmentAndTrackOnRPC.tdrstyle import set_tdr_style
set_tdr_style()

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetTitleSize(0.06, "X");
gStyle.SetTitleSize(0.06, "Y");

runs = []
avgEffsB, avgEffsE, avgEffsRE4 = [], [], []

for fName in glob("data/efficiency/Run*/run*.txt"):
    if not os.path.exists(fName): continue
    run = int(os.path.basename(fName).split('.')[0][3:])
    runs.append(run)

    if method == "avgPerRoll":
        effsB, effsE, effsRE4 = [], [], []
        denB, denE, denRE4 = 0., 0., 0.
        for l in open(fName).readlines():
            l = l.strip()
            if len(l) == 0 or l[0] == '#': continue

            name, den, num = l.split()
            den, num = float(den), float(num)
            eff = -1
            if den > 0: eff = num/den*100

            #if eff > 70 and den > 10:
            if eff > 0:
                if name.startswith("W"):
                    effsB.append(eff)
                    denB += den
                elif name.startswith("RE+4") or name.startswith("RE-4"):
                    effsRE4.append(eff)
                    denRE4 += den
                else:
                    effsE.append(eff)
                    denE += den

        if denB < 1: avgEffsB.append(-1)
        else: avgEffsB.append(sum(effsB)/len(effsB))
        if denE < 1: avgEffsE.append(-1)
        else: avgEffsE.append(sum(effsE)/len(effsE))
        if denRE4 < 1: avgEffsRE4.append(-1)
        else: avgEffsRE4.append(sum(effsRE4)/len(effsRE4))
    elif method == "avgPerCount":
        numB, numE, numRE4 = 0., 0., 0.
        denB, denE, denRE4 = 0., 0., 0.
        for l in open(fName).readlines():
            l = l.strip()
            if len(l) == 0 or l[0] == '#': continue

            name, den, num = l.split()
            den, num = float(den), float(num)
            if num == 0: continue

            if name.startswith("W"):
                numB += num
                denB += den
            elif name.startswith("RE+4") or name.startswith("RE-4"):
                numRE4 += num
                denRE4 += den
            else:
                numE += num
                denE += den

        if denB < 100: avgEffsB.append(-1)
        else: avgEffsB.append(100*numB/denB)
        if denE < 100: avgEffsE.append(-1)
        else: avgEffsE.append(100*numE/denE)
        if denRE4 < 100: avgEffsRE4.append(-1)
        else: avgEffsRE4.append(100*numRE4/denRE4)

nRuns = len(runs)
gapLS, gapTS = int(nRuns*0.1), int(nRuns*0.02)
periodsLS = {251168:"Run2015", 273150:"Run2016", 297050:"Run2017", 315488:"Run2018"}
periodsTS = {
    254277:"MD1", 257969:"MD2", 258287:"TS2",
    274954:"TS1", 277981:"MD1", 279588:"MD2", 281613:"MD3&TS2", 282708:"MD4",
    298996:"MD1&TS1", 300087:"MD2", 303824:"MD3&TS2",
    318733:"MD1&TS1", 321887:"MD2", 323414:"MD3&TS2",
}
gapTexts = []

nPoints = nRuns+(len(periodsLS)+1)*gapLS+len(periodsTS)*gapTS
hFrame = TH1F("hFrame", "hFrame;Run number;Efficiency [%]", nPoints, 1, nPoints+1)
hFrame.SetMinimum(effMin)
hFrame.SetMaximum(effMax)
hFrame.GetYaxis().SetNdivisions(505)
hFrame.GetYaxis().SetTitleOffset(0.6)
hFrame.GetXaxis().SetBinLabel(1, "")
hFrame.GetXaxis().SetTickSize(0)
hFrame.GetXaxis().SetTitleOffset(1.8)

hLS = hFrame.Clone()
hTS = hFrame.Clone()
#hLS.SetFillStyle(3005)
#hTS.SetFillStyle(3005)
hLS.SetFillColor(TColor.GetColor("#CCCCCC"))
hTS.SetFillColor(TColor.GetColor("#EEEEEE"))
hLS.SetLineColor(TColor.GetColor("#CCCCCC"))
hTS.SetLineColor(TColor.GetColor("#EEEEEE"))
#hLS.SetLineWidth(0)
#hTS.SetLineWidth(0)

grpB, grpE, grpRE4 = TGraph(), TGraph(), TGraph()
ii = 0
for run, avgEffB, avgEffE, avgEffRE4 in sorted(zip(runs, avgEffsB, avgEffsE, avgEffsRE4), key=lambda x: x[0]):
    ii += 1
    if run in periodsLS:
        for i in range(ii, ii+gapLS): hLS.Fill(i, 100)
        hFrame.GetXaxis().SetBinLabel(ii+gapLS, "%d" % run)

        #t = TText(ii+gapLS/2, effMin+(effMax-effMin)*.1, "YETS")
        #t.SetTextAlign(12)
        #t.SetTextAngle(90)
        #t.SetTextSize(0.05)
        #gapTexts.append(t)

        #t = TText(ii+gapLS*1.05, effMin+(effMax-effMin)*.02, periodsLS[run])
        t = TPaveText(ii+gapLS*1.05, effMin, ii+gapLS*2.25, effMin+(effMax-effMin)*.09, "")
        t.SetFillColor(kWhite)
        t.SetBorderSize(0)
        t.SetFillStyle(1001)
        t.SetTextAlign(11)
        t.SetTextSize(0.04)
        t.AddText(periodsLS[run])
        gapTexts.append(t)

        ii += gapLS
    elif run in periodsTS:
        for i in range(ii, ii+gapTS): hTS.Fill(i, 100)
        hFrame.GetXaxis().SetBinLabel(ii+gapTS, "%d" % run)

        t = TText(ii+gapTS/2, effMin+(effMax-effMin)*.4, periodsTS[run])
        t.SetTextAlign(12)
        t.SetTextAngle(90)
        t.SetTextSize(0.025)
        gapTexts.append(t)
        ii += gapTS

    if avgEffB > 0: grpB.SetPoint(grpB.GetN(), ii, avgEffB)
    if avgEffE > 0: grpE.SetPoint(grpE.GetN(), ii, avgEffE)
    if avgEffRE4 > 0: grpRE4.SetPoint(grpRE4.GetN(), ii, avgEffRE4)

for i in range(ii+1, nPoints+1): hLS.Fill(i, 100)
#gapTexts[0].SetText(gapTexts[0].GetX(), gapTexts[0].GetY(), "LS1")
t = TText(gapLS/2, effMin+(effMax-effMin)*.4, "LS1")
t.SetTextAlign(12)
t.SetTextAngle(90)
t.SetTextSize(0.05)
gapTexts.append(t)
t = TText(ii+gapLS/2, effMin+(effMax-effMin)*.4, "LS2")
t.SetTextAlign(12)
t.SetTextAngle(90)
t.SetTextSize(0.05)
gapTexts.append(t)

grpB.SetMarkerStyle(26)
grpE.SetMarkerStyle(24)
grpRE4.SetMarkerStyle(25)

grpB.SetMarkerSize(.5)
grpE.SetMarkerSize(.5)
grpRE4.SetMarkerSize(.5)

grpB.SetMarkerColor(kRed)
grpE.SetMarkerColor(kBlue)
grpRE4.SetMarkerColor(kGreen+1)

grpB.SetLineColor(kRed)
grpE.SetLineColor(kBlue)
grpRE4.SetLineColor(kGreen+1)

c = TCanvas("cEffHistory", "cEffHistory", 1000, 450)
c.SetLeftMargin(0.08)
c.SetRightMargin(0.03)
c.SetTopMargin(0.1)
c.SetBottomMargin(0.25)

#leg = TLegend(992, 80, 1500, 87, "", "")
leg = TLegend(1-c.GetRightMargin()-0.1, c.GetBottomMargin(), 1-c.GetRightMargin(), c.GetBottomMargin()+0.2)
leg.SetBorderSize(0)
leg.SetFillStyle(1001)
leg.SetFillColor(kWhite)
leg.AddEntry(grpB, "Barrel", "lp")
leg.AddEntry(grpE, "RE1/2/3", "lp")
leg.AddEntry(grpRE4, "RE4", "lp")

hFrame.Draw()
hLS.Draw("histsame")
hTS.Draw("histsame")
grpRE4.Draw("p")
grpE.Draw("p")
grpB.Draw("p")
for t in gapTexts: t.Draw()
leg.Draw()
hFrame.Draw("axissame")

ll = buildLabel("", "outset")
ll[0].SetX(c.GetLeftMargin())
ll[0].SetY(1-c.GetTopMargin()+0.01)
ll[1].SetX(c.GetLeftMargin()+0.06)
ll[1].SetY(1-c.GetTopMargin()+0.01)
ll[2].SetX(1-c.GetRightMargin())
ll[2].SetY(1-c.GetTopMargin()+0.01)
for l in ll: l.Draw()

c.Print("%s/%s.png" % (resultDir, c.GetName()))
c.Print("%s/%s.pdf" % (resultDir, c.GetName()))
c.Print("%s/%s.C" % (resultDir, c.GetName()))
