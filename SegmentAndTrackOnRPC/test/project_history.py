#!/usr/bin/env python

from ROOT import *
import os, sys
from array import array
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

from RPCDPGAnalysis.SegmentAndTrackOnRPC.buildLabels import *
sys.path.append("%s/src/RPCDPGAnalysis/SegmentAndTrackOnRPC/python" % os.environ["CMSSW_BASE"])
from ProjectTHnSparse import *
era = "Run2018A"

runs = []
categories = {
  "RB" :[{'region':(0,0)}],
  "RE" :[{'region':(-1,-1), 'disk':(1,3)}, {'region':(1,1), 'disk':(1,3)}],
  "RE4":[{'region':(-1,-1), 'disk':(4,4)}, {'region':(1,1), 'disk':(4,4)}],
#  "REp43":[{'region':(+1,+1), 'disk':(4,4), 'ring':(3,3)}],
#  "REm43":[{'region':(-1,-1), 'disk':(4,4), 'ring':(3,3)}],
#  "REp42":[{'region':(+1,+1), 'disk':(4,4), 'ring':(2,2)}],
#  "REm42":[{'region':(-1,-1), 'disk':(4,4), 'ring':(2,2)}],
#  "W+2_RB2in_S12_Forward":[{'wheel':(2,2), 'station':(2,2), 'layer':(1,1), 'sector':(12,12), 'roll':(3,3)}],
}
colors = [kGreen+2, kAzure+1, kRed+2, kOrange+2, kMagenta+1, kBlack]
hEffs, hClss = {}, {}

print "Projecting nDim histograms to 1D..."
for fName in sys.argv[1:]:
    print "Analyzing", fName
    f = TFile(fName)
    hInfo = f.Get("rpcExt/hInfo")
    hSel = THnSparseSelector(hInfo)

    for name, ranges in categories.iteritems():
        ## For the cluster size
        hCl = None
        if name in hClss: hCl = hClss[name]
        for r in ranges:
            cut = {'isFiducial':(1,1)}
            cut.update(r)
            if hCl == None: hCl = hSel.Project2D('run', 'cls', cut, suffix=name)
            else          : hCl.Add(hSel.Project2D('run', 'cls', cut))
        if name not in hClss:
            hClss[name] = hCl
            hCl.SetDirectory(0)

        ## For the efficiency
        hNum, hDen = None, None
        if name in hEffs: hNum, hDen = hEffs[name]
        for r in ranges:
            cut = {'isFiducial':(1,1)}
            cut.update(r)
            if hDen == None: hDen = hSel.Project1D('run', cut, suffix=('_Den%s'%name))
            else           : hDen.Add(hSel.Project1D('run', cut))
            cut.update({'isMatched':(1,1)})
            if hNum == None: hNum = hSel.Project1D('run', cut, suffix=('_Num%s'%name))
            else           : hNum.Add(hSel.Project1D('run', cut))
        if name not in hEffs:
            hNum.SetDirectory(0)
            hDen.SetDirectory(0)
            hEffs[name] = [hNum, hDen]

for name in hClss: hClss[name] = hClss[name].ProfileX()

fout = TFile("history.root", "recreate")
print "Computing efficiencies...",
hAnything = hEffs[hEffs.keys()[0]][0]
runs = []
grpEffs = {}
grpClss = {}
for i, catName in enumerate(hEffs.keys()):
    grp = TGraphAsymmErrors()
    grp.SetLineColor(colors[i])
    grp.SetMarkerColor(colors[i])
    grp.SetMarkerStyle(kFullCircle)
    grp.SetMarkerSize(0.6)
    grpEffs[catName] = grp

    grp = TGraphErrors()
    grp.SetLineColor(colors[i])
    grp.SetMarkerColor(colors[i])
    grp.SetMarkerStyle(kFullCircle)
    grp.SetMarkerSize(0.6)
    grpClss[catName] = grp

for b in range(1,hAnything.GetNbinsX()+2):
    run = hAnything.GetXaxis().GetBinLowEdge(b)
    dens, nums = [0]*len(hEffs), [0]*len(hEffs)
    for i, (catName, (hNum, hDen)) in enumerate(hEffs.iteritems()):
        dens[i], nums[i] = hDen.GetBinContent(b), hNum.GetBinContent(b)

    if 0.0 in dens or 0 in dens: continue

    runs.append(run)
    for i, (catName, den, num) in enumerate(zip(hEffs.keys(), dens, nums)):
        eff = num/den
        eHi = TEfficiency.ClopperPearson(den, num, 0.95, True) - eff
        eLo = eff -  TEfficiency.ClopperPearson(den, num, 0.95, False)
        grpEff = grpEffs[catName]
        np = grpEff.GetN()
        grpEff.SetPoint(np, np+0.3*i, eff)
        grpEff.SetPointError(np, 0., 0., eLo, eHi)

        cls = hClss[catName].GetBinContent(b)
        grpCls = grpClss[catName]
        np = grpCls.GetN()
        grpCls.SetPoint(np, np+0.3*i, cls)
        grpCls.SetPointError(np, 0., 0.)

hEffFrame = TH1D("hEffFrame", "hFrame", len(runs), 0, len(runs))
hEffFrame.SetMinimum(0.7)
hEffFrame.SetMaximum(1.0)
for i, run in enumerate(runs):
    hEffFrame.GetXaxis().SetBinLabel(i+1, "%d" % run)

cEff = TCanvas("cHistoryEff", "cEff", 1600, 400)
cEff.SetLeftMargin(0.05)
cEff.SetRightMargin(0.05)
legEff = TLegend(0.3, 0.2, 0.5, 0.4)
legEff.SetFillStyle(0)
legEff.SetLineWidth(0)
hEffFrame.Draw()
#hEffFrame.Write()
for catName, grp in grpEffs.iteritems():
    grp.Draw("epZ")
    legEff.AddEntry(grp, catName, "lp")
    #grp.Write()
legEff.Draw()
llsEffs = buildLabel(era)
for ll in llsEffs: ll.Draw()

cCls = TCanvas("cHistoryCls", "cCls", 1600, 400)
cCls.SetLeftMargin(0.05)
cCls.SetRightMargin(0.05)
legCls = TLegend(0.3, 0.2, 0.5, 0.4)
legCls.SetFillStyle(0)
legCls.SetLineWidth(0)
hClsFrame = hEffFrame.Clone()
hClsFrame.SetName("hClsFrame")
hClsFrame.SetMinimum(1.0)
hClsFrame.SetMaximum(3.0)
hClsFrame.Draw()
for catName, grp in grpClss.iteritems():
    grp.Draw("epZ")
    legCls.AddEntry(grp, catName, "lp")
    #grp.Write()
legCls.Draw()
llsCls = buildLabel(era)
for ll in llsCls: ll.Draw()

for c in [cEff, cCls]:
    c.Print("%s.C" % c.GetName())
    c.Print("%s.png" % c.GetName())
    c.Print("%s.pdf" % c.GetName())

