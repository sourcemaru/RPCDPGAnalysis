#!/usr/bin/env python

from ROOT import *
import os

files_SingleMuon = [TFile("SingleMuon_Run2016%s.root" % i) for i in "BCDE"]
runs_SingleMuon = []
for d in [f.Get("rpcExt") for f in files_SingleMuon]: runs_SingleMuon.extend([x.GetName() for x in d.GetListOfKeys()])

files_RPCMonitor = [TFile("RPCMonitor_Run2016%s.root" % i) for i in "BCDE"]
runs_RPCMonitor = []
for d in [f.Get("rpcPoint") for f in files_RPCMonitor]: runs_RPCMonitor.extend([x.GetName() for x in d.GetListOfKeys()])

runs = list(set(runs_SingleMuon).intersection(set(runs_RPCMonitor)))
runs.sort()

def collectNames(d):
    names = []
    for name in [x.GetName() for x in d.GetListOfKeys()]:
        obj = d.Get(name)
        if obj.IsA().InheritsFrom("TDirectory"): names.extend(collectNames(obj))
        else: names.append("/".join(d.GetPath().split('/')[3:]+[name]))
    return names
names = collectNames(files_SingleMuon[0].Get("rpcExt/%s" % runs[0]))
runs = []

def mkdirs(d, path):
    for pname in path.split('/'):
        if pname == '': continue
        if d.GetDirectory(pname) == None: d = d.mkdir(pname)
        else: d = d.GetDirectory(pname)
    return d

for prefix in ["SingleMuon", "RPCMonitor"]:
    fout = TFile("%s.root" % prefix, "RECREATE")

    houts = []
    for suffix in "BCDE":
        fin = TFile("%s_Run2016%s.root" % (prefix, suffix))
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
