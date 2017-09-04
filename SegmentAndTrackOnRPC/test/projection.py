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

    def Project1D(self, axisName, axisRanges, **kwargs):
        if axisName not in self.axisInfo: return None

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo: continue

            index = self.axisInfo[name]['index']
            axis = self.hist.GetAxis(index)
            binLo, binHi = axis.FindBin(lo), axis.FindBin(hi)
            self.hist.GetAxis(index).SetRange(binLo, binHi)

        suffix = ''
        if 'suffix' in kwargs: suffix = "_"+kwargs['suffix']

        index = self.axisInfo[axisName]['index']
        h = self.hist.Projection(index)
        h.SetName("h_%s%s" % (axisName, suffix))

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo: continue

            index = self.axisInfo[name]['index']
            axis = self.hist.GetAxis(index)
            self.hist.GetAxis(index).SetRange(1, self.axisInfo[name]['nbins'])

        if 'copyAxisLabel' in kwargs and kwargs['copyAxisLabel'] == True:
            index = self.axisInfo[axisName]['index']
            sourceAxis = self.hist.GetAxis(index)
            targetAxis = h.GetXaxis()
            for b in range(1, targetAxis.GetNbins()+1):
                label = sourceAxis.GetBinLabel(b)
                if label == '': continue
                targetAxis.SetBinLabel(b, label)

        return h

    def Project2D(self, axisName1, axisName2, axisRanges, **kwargs):
        if axisName1 not in self.axisInfo: return None
        if axisName2 not in self.axisInfo: return None

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo: continue

            index = self.axisInfo[name]['index']
            axis = self.hist.GetAxis(index)
            binLo, binHi = axis.FindBin(lo), axis.FindBin(hi)
            self.hist.GetAxis(index).SetRange(binLo, binHi)

        suffix = ''
        if 'suffix' in kwargs: suffix = "_"+kwargs['suffix']

        index1 = self.axisInfo[axisName1]['index']
        index2 = self.axisInfo[axisName2]['index']
        h = self.hist.Projection(index2, index1)
        h.SetName("h_%s_%s%s" % (axisName1, axisName2, suffix))

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo: continue

            index = self.axisInfo[name]['index']
            axis = self.hist.GetAxis(index)
            self.hist.GetAxis(index).SetRange(1, self.axisInfo[name]['nbins'])

        if 'copyXAxisLabel' in kwargs and kwargs['copyXAxisLabel'] == True:
            index = self.axisInfo[axisName1]['index']
            sourceAxis = self.hist.GetAxis(index)
            targetAxis = h.GetXaxis()
            for b in range(1, targetAxis.GetNbins()+1):
                label = sourceAxis.GetBinLabel(b)
                if label == '': continue
                targetAxis.SetBinLabel(b, label)
        if 'copyYAxisLabel' in kwargs and kwargs['copyYAxisLabel'] == True:
            index = self.axisInfo[axisName2]['index']
            sourceAxis = self.hist.GetAxis(index)
            targetAxis = h.GetYaxis()
            for b in range(1, targetAxis.GetNbins()+1):
                label = sourceAxis.GetBinLabel(b)
                if label == '': continue
                targetAxis.SetBinLabel(b, label)

        return h

f = TFile(sys.argv[1])
hInfo = f.Get("rpcExt/hInfo")
hSel = THnSparseSelector(hInfo)

plots = {
    'Barrel_ZPhi':[['gZ', 'gPhi'], {'region':(0,0), 'gZ':(-700, 700), 'isFiducial':(1,1)}],
    'EndcapP_XY':[['gX', 'gY'], {'region':(1,1), 'isFiducial':(1,1)}],
    'EndcapN_XY':[['gX', 'gY'], {'region':(-1,-1), 'isFiducial':(1,1)}],
#    'lX_lY':['lX', 'lY', {'isFiducial':(1,1)}],
    'Barrel_detId':[['rollName'], {'region':(0,0), 'isFiducial':(1,1)}],
    'EndcapP_detId':[['rollName'], {'region':(1,1), 'isFiducial':(1,1)}],
    'EndcapN_detId':[['rollName'], {'region':(-1,-1), 'isFiducial':(1,1)}],
}

if not os.path.exists("hists"): os.mkdir("hists")
f = TFile("hists/%s" % (os.path.basename(sys.argv[1])), "RECREATE")
for name, (variables, ranges) in plots.iteritems():
    subranges = ranges.copy()
    xVar = variables[0]
    hDen = hSel.Project1D(xVar, subranges, name+"_Den", copyAxisLabel=True)
    subranges.update({'isMatched':(1,1)})
    hNum = hSel.Project1D(xVar, subranges, name+"_Num", copyAxislabel=True)
    hDen.Write()
    hNum.Write()

for name, (variables, ranges) in plots.iteritems():
    subranges = ranges.copy()
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
        if len(variables) == 1:
            xVar = variables[0]
            hDen = hSel.Project1D(xVar, subranges, subname+"_Den")

            subranges.update({'isMatched':(1,1)})
            hNum = hSel.Project1D(xVar, subranges, subname+"_Num")
        elif len(variables) == 2:
            xVar, yVar = variables
            hDen = hSel.Project2D(xVar, yVar, subranges, subname+"_Den")

            subranges.update({'isMatched':(1,1)})
            hNum = hSel.Project2D(xVar, yVar, subranges, subname+"_Num")

        hDen.Write()
        hNum.Write()

