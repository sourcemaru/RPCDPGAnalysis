#!/usr/bin/env python

run = 0
padW = 500

from ROOT import *
from array import array
import os, sys
from math import floor
gStyle.SetOptStat(0)

class THnSparseSelector:
    def __init__(self, hist):
        self.hist = hist
        self.axisInfo = {}
        for i in range(hist.GetNdimensions()):
            axis = hist.GetAxis(i)
            name, title = axis.GetName(), axis.GetTitle()
            bins = []
            self.axisInfo[name] = {
                'title':title, 'index':i,
                'nbins':axis.GetNbins(), 'min':axis.GetXmin(), 'max':axis.GetXmax(),
            }

    def Project2D(self, axisName1, axisName2, axisRanges, suffix=""):
        if axisName1 not in self.axisInfo: return None
        if axisName2 not in self.axisInfo: return None

        index1 = self.axisInfo[axisName1]['index']
        index2 = self.axisInfo[axisName2]['index']

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo: continue

            index = self.axisInfo[name]['index']

            axis = self.hist.GetAxis(index)
            binLo, binHi = axis.FindBin(lo), axis.FindBin(hi)

            self.hist.GetAxis(index).SetRange(binLo, binHi)

        if suffix != "": suffix = "_"+suffix
        h = self.hist.Projection(index2, index1)
        h.SetName("h_%s_%s%s" % (axisName1, axisName2, suffix))

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo: continue

            index = self.axisInfo[name]['index']

            axis = self.hist.GetAxis(index)

            self.hist.GetAxis(index).SetRange(1, self.axisInfo[name]['nbins'])

        return h

f = TFile(sys.argv[1])
hInfo = f.Get("rpcExt/hInfo")
hSel = THnSparseSelector(hInfo)

plots = {
    'Barrel':['gZ', 'gPhi', {'region':(0,0), 'gZ':(-700, 700), 'isFiducial':(1,1)}],
    'EndcapP':['gX', 'gY', {'region':(1,1), 'isFiducial':(1,1)}],
    'EndcapN':['gX', 'gY', {'region':(-1,-1), 'isFiducial':(1,1)}],
#    'lX_lY':['lX', 'lY', {'isFiducial':(1,1)}],
}

if not os.path.exists("hists"): os.mkdir("hists")
f = TFile("hists/%s" % (os.path.basename(sys.argv[1])), "RECREATE")
for name, (xVar, yVar, ranges) in plots.iteritems():
    subsels = []
    if name.startswith("Barrel"):
        for station in range(1,5):
            nLayer = 2
            if station > 2: nLayer = 1
            for layer in range(1,nLayer+1):
                subsels.append({'station':(station,station), 'layer':(layer,layer)})
    elif name.startswith("Endcap"):
        for station in range(1,5):
            subsels.append({'station':(station,station)})

    for subsel in subsels:
        subranges = ranges.copy()
        subname = name + '_' + ('_'.join("%s%d" % (n, r[0]) for n, r in subsel.iteritems()))

        subranges.update(subsel)
        hDen = hSel.Project2D(xVar, yVar, subranges, subname+"_Den")

        subranges.update({'isMatched':(1,1)})
        hNum = hSel.Project2D(xVar, yVar, subranges, subname+"_Num")

        hDen.Write()
        hNum.Write()

