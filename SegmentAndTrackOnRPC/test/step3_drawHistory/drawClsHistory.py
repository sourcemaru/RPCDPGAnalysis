#!/usr/bin/env python3

clsMin, clsMax = 1, 3

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
avgClssB, avgClssE, avgClssRE4 = [], [], []

for fName in glob("data/cls/Run*/run*.txt"):
    if not os.path.exists(fName): continue
    run = int(os.path.basename(fName).split('.')[0][3:])
    runs.append(run)

    clssB, clssE, clssRE4 = [], [], []
    denB, denE, denRE4 = 0., 0., 0.
    for l in open(fName).readlines():
        l = l.strip()
        if len(l) == 0 or l[0] == '#': continue

        name, den, mean, err2 = l.split()
        den, mean, err2 = float(den), float(mean), float(err2)

        #if cls > 70 and den > 10:
        if den > 0:
            if name.startswith("W"):
                clssB.append(mean)
                denB += den
            elif name.startswith("RE+4") or name.startswith("RE-4"):
                clssRE4.append(mean)
                denRE4 += den
            else:
                clssE.append(mean)
                denE += den

    if denB == 0: avgClssB.append(-1)
    else: avgClssB.append(sum(clssB)/len(clssB))
    if denE  == 0: avgClssE.append(-1)
    else: avgClssE.append(sum(clssE)/len(clssE))
    if denRE4 == 0: avgClssRE4.append(-1)
    else: avgClssRE4.append(sum(clssRE4)/len(clssRE4))

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
hFrame = TH1F("hFrame", "hFrame;Run number;Cluster size", nPoints, 1, nPoints+1)
hFrame.SetMinimum(clsMin)
hFrame.SetMaximum(clsMax)
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
for run, avgClsB, avgClsE, avgClsRE4 in sorted(zip(runs, avgClssB, avgClssE, avgClssRE4), key=lambda x: x[0]):
    ii += 1
    if run in periodsLS:
        for i in range(ii, ii+gapLS): hLS.Fill(i, 100)
        hFrame.GetXaxis().SetBinLabel(ii+gapLS, "%d" % run)

        #t = TText(ii+gapLS/2, clsMin+(clsMax-clsMin)*.1, "YETS")
        #t.SetTextAlign(12)
        #t.SetTextAngle(90)
        #t.SetTextSize(0.05)
        #gapTexts.append(t)

        #t = TText(ii+gapLS*1.05, clsMin+(clsMax-clsMin)*.02, periodsLS[run])
        t = TPaveText(ii+gapLS*1.05, clsMin, ii+gapLS*2.25, clsMin+(clsMax-clsMin)*.09, "")
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

        t = TText(ii+gapTS/2, clsMin+(clsMax-clsMin)*.35, periodsTS[run])
        t.SetTextAlign(12)
        t.SetTextAngle(90)
        t.SetTextSize(0.025)
        gapTexts.append(t)
        ii += gapTS

    if avgClsB > 0: grpB.SetPoint(grpB.GetN(), ii, avgClsB)
    if avgClsE > 0: grpE.SetPoint(grpE.GetN(), ii, avgClsE)
    if avgClsRE4 > 0: grpRE4.SetPoint(grpRE4.GetN(), ii, avgClsRE4)

for i in range(ii+1, nPoints+1): hLS.Fill(i, 100)
#gapTexts[0].SetText(gapTexts[0].GetX(), gapTexts[0].GetY(), "LS1")
t = TText(gapLS/2, clsMin+(clsMax-clsMin)*.35, "LS1")
t.SetTextAlign(12)
t.SetTextAngle(90)
t.SetTextSize(0.05)
gapTexts.append(t)
t = TText(ii+gapLS/2, clsMin+(clsMax-clsMin)*.35, "LS2")
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

c = TCanvas("cClsHistory", "cClsHistory", 1000, 450)
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
