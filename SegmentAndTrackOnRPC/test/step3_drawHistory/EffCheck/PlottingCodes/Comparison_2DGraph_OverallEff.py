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

Effcomp = TGraphAsymmErrors()

hFrame = TH1F("Comp","Comp;AllRun2;2018",10,0,1)
hFrame.SetMaximum(1.0)
hFrame.Draw()

effs1 = {}
effs2 = {}
for line in open(fName1).readlines():
    if len(line) == 0 or line.startswith('#'): continue
    name, eff, errLo, errHi, something1 = line.strip().split()
    effs1[name] = float(eff)

for line in open(fName2).readlines():    
    if len(line) == 0 or line.startswith('#'): continue
    name, eff, errLo, errHi, something1 = line.strip().split()
    effs2[name] = float(eff)

for name in list(effs1.keys()):
    if name not in list(effs2.keys()): continue

    eff_1 = effs1[name]
    eff_2 = effs2[name]

    n = Effcomp.GetN()
    Effcomp.SetPoint(n, eff_1, eff_2)

Effcomp.SetMarkerStyle(24)
Effcomp.SetMarkerColor(kBlue+1)
Effcomp.SetMarkerSize(0.5)

Effcomp.Draw("Psame")
