#!/usr/bin/env python

import sys, os
from ROOT import *

from RPCDPGAnalysis.SegmentAndTrackOnRPC.tdrstyle import set_tdr_style
set_tdr_style()

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.2)
gStyle.SetPadRightMargin(0.05)
gStyle.SetPadBottomMargin(0.12)

fName1 = sys.argv[1]
fName2 = sys.argv[2]

cHistories = [TCanvas("cHistory%d" % i) for i in range(2)]

h2d = TH2F("comp","comp;2017;2018",4,1,5,4,1,5)
h1 = TH1F("2017","2017;Category[name];",4,1,5)
h2 = TH1F("2018","2018;Category[name];",4,1,5)

h2d.GetXaxis().SetBinLabel(1,"Dead")
h2d.GetXaxis().SetBinLabel(2,"Good")
h2d.GetXaxis().SetBinLabel(3,"Sudden Drop")
h2d.GetXaxis().SetBinLabel(4,"Others")
h2d.GetYaxis().SetBinLabel(1,"Dead")
h2d.GetYaxis().SetBinLabel(2,"Good")
h2d.GetYaxis().SetBinLabel(3,"Sudden Drop")
h2d.GetYaxis().SetBinLabel(4,"Others")

h1.GetXaxis().SetBinLabel(1,"Dead")
h1.GetXaxis().SetBinLabel(2,"Good")
h1.GetXaxis().SetBinLabel(3,"Sudden Drop")
h1.GetXaxis().SetBinLabel(4,"Others")

h2.GetXaxis().SetBinLabel(1,"Dead")
h2.GetXaxis().SetBinLabel(2,"Good")
h2.GetXaxis().SetBinLabel(3,"Sudden Drop")
h2.GetXaxis().SetBinLabel(4,"Others")

cats1 = {}
cats2 = {}
for line in open(fName1).readlines():
    name, cat = line.strip().split()
    cats1[name] = int(cat)
    
for line in open(fName2).readlines():
    name, cat = line.strip().split()
    cats2[name] = int(cat)

for name in list(cats1.keys()):
    cat1 = cats1[name]
    cat2 = cats2[name]
    h2d.Fill(cat1, cat2)
    h1.Fill(cat1)
    h2.Fill(cat2)

h1.SetLineColor(kBlue-4)
#h1.SetFillColor(kBlue-4)
#h1.SetFillStyle(3004)
h1.SetLineWidth(2)
h2.SetLineColor(kRed+1)
#h2.SetFillColor(kRed+1)
#h2.SetFillStyle(3005)
h2.SetLineWidth(2)

h1.SetMaximum(2800)
h2.SetMaximum(2800)

cHistories[0].cd()
h2d.Draw("COLZtext")

cHistories[1].cd()
h1.Draw()
h2.Draw("same")

leg = TLegend(0.6, 0.5, 0.9, 0.6)
#leg.SetHeader("","C")
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.AddEntry(h1, "Run2017 All", "l")
leg.AddEntry(h2, "Run2018 AtoC", "l")

leg.Draw("same")

for c in cHistories:
    c.Modified()
    c.Update()

