#!/usr/bin/env python

from ROOT import *
import sys, os

#files = [TFile("SingleMuon_Run2016%s.root" % i) for i in "BCDE"]
files  = [TFile(x) for x in sys.argv[1:] if x.endswith('.root')]
runs = []
for d in [f.Get("rpcExt") for f in files]: runs.extend([x.GetName() for x in d.GetListOfKeys()])

def collectNames(d):
    names = []
    for name in [x.GetName() for x in d.GetListOfKeys()]:
        if 'XY' in name or 'ZPhi' in name: continue
        obj = d.Get(name)
        if obj.IsA().InheritsFrom("TDirectory"): names.extend(collectNames(obj))
        else: names.append("/".join(d.GetPath().split('.root:',1)[-1].split('/')[3:]+[name]))
    return names
names = collectNames(files[0].Get("rpcExt/%s" % runs[0]))
runs = []

def mkdirs(d, path):
    for pname in path.split('/'):
        if pname == '': continue
        if d.GetDirectory(pname) == None: d = d.mkdir(pname)
        else: d = d.GetDirectory(pname)
    return d

fout = TFile("merged.root", "RECREATE")

houts = []
for fin in files:
    din = fin.Get("rpcExt")
    if din == None: din = fin.Get("rpcPoint")
    if din == None: continue

    nRuns = max(len(runs), len(din.GetListOfKeys()))
    for ii, run in enumerate([x.GetName() for x in din.GetListOfKeys()]):
        if len(runs) > 0 and run not in runs: continue
        print "%s %s (%d/%d)" % (fin.GetName(), run, ii+1, nRuns)
        for name in names:
            hin = din.Get(run+"/"+name)
            if hin == None: continue

            dout = mkdirs(fout, os.path.dirname(name))
            dout.cd()
            hout = dout.Get(os.path.basename(name))
            if hout == None:
                hout = hin.Clone()
                houts.append([dout, hout])
            else: hout.Add(hin)

for dout, hout in houts:
    dout.cd()
    hout.Write()
fout.Close()
fout = None
