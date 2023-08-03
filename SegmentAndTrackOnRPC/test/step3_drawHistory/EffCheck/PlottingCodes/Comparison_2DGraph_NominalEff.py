#!/usr/bin/env python

import sys, os
from ROOT import *

from RPCDPGAnalysis.SegmentAndTrackOnRPC.tdrstyle import set_tdr_style
set_tdr_style()

gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

gStyle.SetPadTopMargin(0.07)
gStyle.SetPadLeftMargin(0.16)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)

fName1 = sys.argv[1]
fName2 = sys.argv[2]

#cHistories = [TCanvas("cHistory%d" % i) for i in range(2)]

Effcomp_cat1 = TGraphAsymmErrors()
Effcomp_cat2 = TGraphAsymmErrors()
Effcomp_cat3 = TGraphAsymmErrors()
Effcomp_cat4 = TGraphAsymmErrors()

hFrame = TH1F("Comp","Comp;2017;2018",10,0,1)
hFrame.SetMaximum(1.0)
hFrame.Draw()

effs1 = {}
effs2 = {}
for line in open(fName1).readlines():
    cat, name, nominaleff = line.strip().split()
    effs1[name] = [int(cat), float(nominaleff)]
    
for line in open(fName2).readlines():
    cat, name, nominaleff = line.strip().split()
    effs2[name] = [int(cat), float(nominaleff)]

for name in list(effs1.keys()):
    cat1 = effs1[name][0]
    cat2 = effs2[name][0]
    eff1 = effs1[name][1]
    eff2 = effs2[name][1]
        
    if cat2 == 1:
        n = Effcomp_cat1.GetN()
        Effcomp_cat1.SetPoint(n, eff1, eff2)
    elif cat2 == 2:
        n = Effcomp_cat2.GetN()
        Effcomp_cat2.SetPoint(n, eff1, eff2)
    elif cat2 == 3:
        n = Effcomp_cat3.GetN()
        Effcomp_cat3.SetPoint(n, eff1, eff2)
    else :
        n = Effcomp_cat4.GetN()
        Effcomp_cat4.SetPoint(n, eff1, eff2)

Effcomp_cat1.SetMarkerStyle(21)
Effcomp_cat1.SetMarkerColor(kRed+1)
Effcomp_cat1.SetMarkerSize(0.7)
Effcomp_cat2.SetMarkerStyle(24)
Effcomp_cat2.SetMarkerColor(kBlue-4)
Effcomp_cat2.SetMarkerSize(0.7)
Effcomp_cat3.SetMarkerStyle(22)
Effcomp_cat3.SetMarkerColor(kBlack)
Effcomp_cat3.SetMarkerSize(0.7)
Effcomp_cat4.SetMarkerStyle(25)
Effcomp_cat4.SetMarkerColor(kGreen+1)
Effcomp_cat4.SetMarkerSize(1)

Effcomp_cat1.Draw("Psame")
Effcomp_cat2.Draw("Psame")
Effcomp_cat3.Draw("Psame")
Effcomp_cat4.Draw("Psame")
