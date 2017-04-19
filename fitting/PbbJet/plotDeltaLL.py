#!/usr/bin/env python
import ROOT as rt,sys,math,os
import numpy as np
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
from operator import itemgetter

# including other directories
#sys.path.insert(0, '../.')
from tools import *
from RootIterator import RootIterator

from array import array

        
def exec_me(command,dryRun=True):
    print command
    if not dryRun: os.system(command)


def main(options,args):
    odir = options.odir
    lumi = options.lumi 
    npoints = options.npoints

    if options.isData:
        dataTag = 'data'
    else:        
        dataTag = 'asimov'

    floatTag = '-P %s'%options.poi
    if options.floatOtherPOIs:
        floatTag = '--floatOtherPOIs 1 -P %s'%options.poi
        
    if not options.justPlot:
        if options.isData:
            exec_me('combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges %s=%f,%f --algo grid --points %i -d %s -n %s --saveWorkspace %s'%(options.poi,options.rMin,options.rMax,options.npoints,options.datacard,options.datacard.replace('.root','_data'),floatTag),options.dryRun)
            exec_me('combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges %s=%f,%f --algo grid --points %i -d %s -n %s -S 0 --snapshotName MultiDimFit %s'%(options.poi,options.rMin,options.rMax,options.npoints,'higgsCombine%s.MultiDimFit.mH120.root'%options.datacard.replace('.root','_data'),options.datacard.replace('.root','_data_nosys'),floatTag),options.dryRun)
        else:
            dataTag = 'asimov'
            exec_me('combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges %s=%f,%f --algo grid --points %i -d %s -n %s -t -1 --toysFreq --setPhysicsModelParameters %s=%f --saveWorkspace %s'%(options.poi,options.rMin,options.rMax,options.npoints,options.datacard,options.datacard.replace('.root','_asimov'),options.poi,options.r,floatTag),options.dryRun)
            exec_me('combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges %s=%f,%f --algo grid --points %i -d %s -n %s -t -1 --toysFreq -S 0 --snapshotName MultiDimFit --setPhysicsModelParameters %s=%f %s'%(options.poi,options.rMin,options.rMax,options.npoints,'higgsCombine%s.MultiDimFit.mH120.root'%options.datacard.replace('.root','_asimov'),options.datacard.replace('.root','_asimov_nosys'),options.poi,options.r,floatTag),options.dryRun)

    tfileWithSys = rt.TFile.Open('higgsCombine%s.MultiDimFit.mH120.root'%(options.datacard.replace('.root','_%s'%dataTag)))
    limitWithSys = tfileWithSys.Get('limit')    
    xp = []
    yp = []
    for i in range(0,limitWithSys.GetEntries()):
        limitWithSys.GetEntry(i)
        if limitWithSys.quantileExpected < 1:
            if 2*limitWithSys.deltaNLL > 7*7: continue
            xp.append(getattr(limitWithSys,options.poi))
            yp.append(2*limitWithSys.deltaNLL)
    [xp, yp] = [list(x) for x in zip(*sorted(zip(xp, yp), key=itemgetter(0)))]
    
    tfileWithoutSys = rt.TFile.Open('higgsCombine%s.MultiDimFit.mH120.root'%(options.datacard.replace('.root','_%s_nosys'%dataTag)))
    limitWithoutSys = tfileWithoutSys.Get('limit')
    xs = []
    ys = []
    for i in range(0,limitWithoutSys.GetEntries()):
        limitWithoutSys.GetEntry(i)
        if limitWithoutSys.quantileExpected < 1:
            if 2*limitWithoutSys.deltaNLL > 7*7: continue
            xs.append(getattr(limitWithoutSys,options.poi))
            ys.append(2*limitWithoutSys.deltaNLL)
    [xs, ys] = [list(x) for x in zip(*sorted(zip(xs, ys), key=itemgetter(0)))]
        
    print xs, ys
    gr_s = rt.TGraph(len(xs), array('f', xs), array('f', ys))
    gr_s.SetLineStyle(2)
    gr_s.SetLineColor(rt.kBlue)
    gr_s.SetLineWidth(3)
    gr_s.SetName("n2ll_data")
    
    print xp, yp
    gr_p = rt.TGraph(len(xp), array('f', xp), array('f', yp))
    gr_p.SetLineColor(rt.kBlack)
    gr_p.SetLineWidth(3)
    gr_p.SetName("p2ll_data")

    r = rt.RooRealVar('r','r',options.rMin,options.rMax)
    
    rFrame = r.frame(rt.RooFit.Bins(npoints),rt.RooFit.Range(options.rMin,options.rMax),rt.RooFit.Title("r frame (%s)"%dataTag))
    rFrame.SetMinimum(0)
    rFrame.SetMaximum(6)

    #n2ll.plotOn(rFrame,rt.RooFit.ShiftToZero(),rt.RooFit.LineStyle(2),rt.RooFit.Name("n2ll_data"))
    #p2ll.plotOn(rFrame,rt.RooFit.LineColor(rt.kBlack),rt.RooFit.Name("p2ll_data"),rt.RooFit.Precision(-1))
    rFrame.addObject(gr_s, 'L')
    rFrame.addObject(gr_p, 'L')

    tlines = []
    cl = 0.95
    crossing = rt.TMath.Power(rt.Math.normal_quantile(1-0.5*(1-cl), 1.0),2)
    tline = rt.TLine(options.rMin,crossing,options.rMax,crossing)
    tline.SetLineColor(rt.kRed)
    tline.SetLineWidth(2)
    tlines.append(tline)
    
    rLimit = -1
    rLimitNoSys = -1
    for xi in range(0,1001):
        xr = xi*options.rMax/1000.
        if gr_p.Eval(xr) >= crossing and rLimit < 0:
            rLimit = xr
        if gr_s.Eval(xr) >= crossing and rLimitNoSys < 0:
            rLimitNoSys = xr

    tline = rt.TLine(rLimit,0,rLimit,crossing)
    tline.SetLineColor(rt.kBlack)
    tline.SetLineWidth(2)
    tlines.append(tline)
    tline = rt.TLine(rLimitNoSys,0,rLimitNoSys,crossing)
    tline.SetLineColor(rt.kBlue)
    tline.SetLineStyle(2)
    tline.SetLineWidth(2)
    tlines.append(tline)
            
    for tline in tlines:
        rFrame.addObject(tline,"")

    d = rt.TCanvas('d','d',500,400)
    rFrame.Draw()
    rFrame.SetMinimum(0)
    rFrame.SetMaximum(4.*4.)
    
    rFrame.SetXTitle("#mu (signal strength)")
    rFrame.SetYTitle("-2 #Delta log L(%s)"%dataTag)
    rFrame.SetTitleSize(0.04,"X")
    rFrame.SetTitleOffset(0.85,"X")
    rFrame.SetTitleSize(0.04,"Y")
    rFrame.SetTitleOffset(0.8,"Y")
    rFrame.SetLabelSize(0.04,"X")
    rFrame.SetLabelSize(0.04,"Y")
    rFrame.SetNdivisions(505,"X")
    
    leg = rt.TLegend(0.7,0.15,0.89,0.3)
    leg.SetTextFont(42)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.SetFillStyle(0)
    leg.AddEntry("p2ll_data", "stat + syst","l")
    leg.AddEntry("n2ll_data", "stat only","l")
    leg.Draw("same")
    
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.04)
    tag2 = rt.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = rt.TLatex(0.27,0.92,"Simulation Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.05); tag3.SetTextSize(0.04); tag1.Draw(); tag2.Draw(); tag3.Draw()
    
    d.Print(odir+"/deltaLL_%s_r%f.pdf"%(dataTag,options.r))
    d.Print(odir+"/deltaLL_%s_r%f.C"%(dataTag,options.r))

    print "stat+sys:  r < %f"%rLimit
    print "stat-only: r < %f"%rLimitNoSys



##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-r','--r',dest='r', default=0 ,type='float',help='default value of r (for asimov)')
    parser.add_option('--rMin',dest='rMin', default=0 ,type='float',help='minimum of r (signal strength) in profile likelihood plot')
    parser.add_option('--rMax',dest='rMax', default=20,type='float',help='maximum of r (signal strength) in profile likelihood plot')  
    parser.add_option('-d','--datacard'   ,action='store',type='string',dest='datacard'   ,default='card_rhalphabet.txt', help='datacard name')  
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--data', action='store_true', dest='isData', default=False, help='is data')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('-n','--npoints'   ,action='store',type='int',dest='npoints'   ,default=20, help='npoints')
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")
    parser.add_option('-P','--poi'   ,action='store',type='string',dest='poi'   ,default='r', help='poi name')  
    parser.add_option('--floatOtherPOIs',action='store_true', dest='floatOtherPOIs', default=False, help='float other pois')

    (options, args) = parser.parse_args()

    import tdrstyle
    tdrstyle.setTDRStyle()
    rt.gStyle.SetPadTopMargin(0.10)
    rt.gStyle.SetPadLeftMargin(0.16)
    rt.gStyle.SetPadRightMargin(0.10)
    rt.gStyle.SetPalette(1)
    rt.gStyle.SetPaintTextFormat("1.1f")
    rt.gStyle.SetOptFit(0000)
    rt.gROOT.SetBatch()

    main(options,args)
