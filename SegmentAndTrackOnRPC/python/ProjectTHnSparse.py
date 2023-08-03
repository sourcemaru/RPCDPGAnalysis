#!/usr/bin/env python3

from ROOT import gStyle
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
            if name not in self.axisInfo:
                print("Cannot find axis '%s'" % name)
                continue

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
            if name not in self.axisInfo:
                print("Cannot find axis '%s'" % name)
                continue

            index = self.axisInfo[name]['index']
            axis = self.hist.GetAxis(index)
            self.hist.GetAxis(index).SetRange(1, self.axisInfo[name]['nbins'])

        if 'copyAxisLabel' in kwargs and kwargs['copyAxisLabel'] == True:
            index = self.axisInfo[axisName]['index']
            sourceAxis = self.hist.GetAxis(index)
            targetAxis = h.GetXaxis()
            for b in range(0, targetAxis.GetNbins()+2):
                label = sourceAxis.GetBinLabel(b)
                if label == '': continue
                targetAxis.SetBinLabel(b, label)

        return h

    def Project2D(self, axisName1, axisName2, axisRanges, **kwargs):
        if axisName1 not in self.axisInfo: return None
        if axisName2 not in self.axisInfo: return None

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo:
                print("Cannot find axis '%s'" % name)
                continue

            index = self.axisInfo[name]['index']
            axis = self.hist.GetAxis(index)
            binLo, binHi = axis.FindBin(lo), axis.FindBin(hi)
            if binLo > binHi: binHi, binLo = binLo, binHi
            self.hist.GetAxis(index).SetRange(binLo, binHi)

        suffix = ''
        if 'suffix' in kwargs: suffix = "_"+kwargs['suffix']

        index1 = self.axisInfo[axisName1]['index']
        index2 = self.axisInfo[axisName2]['index']
        h = self.hist.Projection(index2, index1)
        h.SetName("h_%s_%s%s" % (axisName1, axisName2, suffix))

        for name, (lo, hi) in axisRanges.iteritems():
            if name not in self.axisInfo:
                print("Cannot find axis '%s'" % name)
                continue

            index = self.axisInfo[name]['index']
            axis = self.hist.GetAxis(index)
            self.hist.GetAxis(index).SetRange(1, self.axisInfo[name]['nbins'])

        if 'copyXAxisLabel' in kwargs and kwargs['copyXAxisLabel'] == True:
            index = self.axisInfo[axisName1]['index']
            sourceAxis = self.hist.GetAxis(index)
            targetAxis = h.GetXaxis()
            for b in range(0, targetAxis.GetNbins()+2):
                label = sourceAxis.GetBinLabel(b)
                if label == '': continue
                targetAxis.SetBinLabel(b, label)
        if 'copyYAxisLabel' in kwargs and kwargs['copyYAxisLabel'] == True:
            index = self.axisInfo[axisName2]['index']
            sourceAxis = self.hist.GetAxis(index)
            targetAxis = h.GetYaxis()
            for b in range(0, targetAxis.GetNbins()+2):
                label = sourceAxis.GetBinLabel(b)
                if label == '': continue
                targetAxis.SetBinLabel(b, label)

        return h

