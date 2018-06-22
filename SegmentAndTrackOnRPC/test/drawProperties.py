#!/usr/bin/env python

from ROOT import *
import sys, os
fName = sys.argv[1]
from RPCDPGAnalysis.SegmentAndTrackOnRPC.buildLabels_cff import *

era = "Run2017"
if len(sys.argv) > 2: era = sys.argv[2]

gROOT.ProcessLine(".L %s/src/SUSYBSMAnalysis/HSCP/test/ICHEP_Analysis/tdrstyle.C" % os.environ["CMSSW_RELEASE_BASE"])
setTDRStyle()
gStyle.SetOptStat(0)
    
gStyle.SetPadTopMargin(0.09)
gStyle.SetPadLeftMargin(0.17)
gStyle.SetPadRightMargin(0.048)
gStyle.SetPadBottomMargin(0.12)
gStyle.SetTitleSize(0.06, "X");
gStyle.SetTitleSize(0.06, "Y");

plots = {
    "cls_Barrel":["cls_Barrel",], 
    "bx_Barrel":["bx_Barrel_Station1", "bx_Barrel_Station2", "bx_Barrel_Station3", "bx_Barrel_Station4", ],

    "cls_Endcap":["cls_EndcapP", "cls_EndcapN", ], 
    "bx_Endcap":["bx_EndcapP_Disk1", "bx_EndcapP_Disk2", "bx_EndcapP_Disk3", "bx_EndcapP_Disk4",
                 "bx_EndcapN_Disk1", "bx_EndcapN_Disk2", "bx_EndcapN_Disk3", "bx_EndcapN_Disk4", ],

    "mass":["mass"],
}

f = TFile(fName)

objs = []
for name, hists in plots.iteritems():
    if len(hists) == 0: continue

    h = f.Get(hists[0]).Clone()
    h.SetName(name)
    h.SetTitle("c_%s" % name)
    if "Barrel" in name:
        h.SetFillColor(30)
        h.SetLineColor(TColor.GetColor("#007700"))
    elif "Endcap" in name:
        h.SetFillColor(38)
        h.SetLineColor(TColor.GetColor("#000099"))
    else:
        h.SetFillStyle(0)
        h.SetLineColor(1)
    h.Reset()
    for hh in hists:
        h.Add(f.Get(hh))

    c = TCanvas("c_%s" % name, name, 500, 500)

    if "mass" in name:
        h.GetXaxis().SetRangeUser(70, 110)
        h.GetYaxis().SetTitle("Events / 0.5GeV")
        h.GetYaxis().SetLabelSize(0.04)
    else:
        h.GetYaxis().SetTitle("Normalized")
        h.Scale(1./h.Integral())

    if "bx" in name:
        c.SetLogy()
    if "cls" in name:
        h.SetMaximum(h.GetMaximum()*1.5)

    h.Draw("hist")
    lls = buildLabel(era, "inset")
    for ll in lls: ll.Draw()

    fixOverlay()

    objs.extend([c, h])
    objs.extend(lls)
    
    c.Print("%s.png" % c.GetName())
    c.Print("%s.pdf" % c.GetName())
    c.Print("%s.C" % c.GetName())

    print name, h.GetMean(), h.GetRMS(), h.GetEntries()
