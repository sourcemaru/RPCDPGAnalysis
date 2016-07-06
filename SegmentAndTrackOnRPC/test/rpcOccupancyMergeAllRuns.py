#!/usr/bin/env python

from ROOT import *
import sys, os

f = TFile("hist_2016B.root")
runs = [x.GetName() for x in f.Get("rpcAn").GetListOfKeys() if x.GetName().startswith("Run")]

fout = TFile("hist_allRuns.root", "RECREATE")
hists = []
for hName in sorted([x.GetName() for x in f.Get("rpcAn/%s" % runs[0]).GetListOfKeys()]):
    print "Processing histogram...", hName
    h = f.Get("rpcAn/%s/%s" % (runs[0], hName)).Clone()
    h.Reset()

    for run in runs:
        hsrc = f.Get("rpcAn/%s/%s" % (runs[0], hName))
        h.Add(hsrc)

    fout.cd()
    h.Write()
    hists.append(h)

