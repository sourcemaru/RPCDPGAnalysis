import FWCore.ParameterSet.Config as cms
from ROOT import *

def buildLabel(era):
    eraToLumi = {
        "Run2017":42599.789/1000, ## Run2017 luminosity without normtag
        "Run2016":36235.493/1000, ## Run2016 luminosity with latest normtag
        "Run2017B":4930.853/1000,
        "Run2017C":9961.856/1000,
        "Run2017D":4352.364/1000,
        "Run2017E":9536.896/1000,
        "Run2017F":13817.819/1000,
        "Run2018A_CCUError":1087.642/1000, ## Run2018A_MuonPhys with CCU error, without normtag yet
        "Run2018A":12096.396/1000, ## Run2018A_MuonPhys without normtag yet
    }
    lumiVal = 0
    if era in eraToLumi: lumiVal = eraToLumi[era]

    #left, top = 0.17, 0.82
    left, top = gStyle.GetPadLeftMargin()+0.03, 1-gStyle.GetPadTopMargin()-0.07
    coverText1 = TLatex(left,top-0.00,"CMS")
    coverText2 = TLatex(left,top-0.02,"Preliminary")
    coverText3 = TLatex(left,top-0.07,"Data %s" % era)
    coverText1.SetNDC()
    coverText2.SetNDC()
    coverText3.SetNDC()
    coverText1.SetTextFont(62)
    coverText2.SetTextFont(52)
    coverText3.SetTextFont(52)
    coverText1.SetTextAlign(11)
    coverText2.SetTextAlign(13)
    coverText3.SetTextAlign(13)
    coverText1.SetTextSize(0.06)
    coverText2.SetTextSize(0.0456)
    coverText3.SetTextSize(0.0456)

    if lumiVal > 0:
        lumi = TLatex(1-gStyle.GetPadRightMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                      "%.1f fb^{-1} (13 TeV)" % lumiVal)
    else:
        lumi = TLatex(1-gStyle.GetPadRightMargin(), 1-gStyle.GetPadTopMargin()+0.01,
                      "(13 TeV)")
    lumi.SetNDC()
    lumi.SetTextAlign(31)
    lumi.SetTextFont(42)

    return [coverText1, coverText2, coverText3, lumi]
