import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

from plotHelpers import *
from sampleContainer import *
#

##############################################################################
def main(options,args):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
    idir = options.idir
    odir = options.odir
    lumi = options.lumi

    
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'Diboson': 'VV(4q)',
               'SingleTop': 'single-t',
               'DY': 'Z+jets',
               'W': 'W+jets',
               'TTbar': 't#bar{t}+jets',        
               'QCD': 'QCD'
               }

        
    tfiles = {'ggHbb': [idir+'/GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_ext.root'],
               'VBFHbb': [idir+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8.root'],
               'Diboson': [idir+'/WWTo4Q_13TeV_amcatnlo.root',idir+'/ZZTo4Q_13TeV_amcatnlo.root'],
               'SingleTop': [idir+'/SingleTop.root'],
               'DY':  [idir+'/DY.root'],
               'W':  [idir+'/W.root'],
               'TTbar':  [idir+'/TTbar_madgraphMLM.root'],
               'QCD': [idir+'/QCD.root']
               }

    color = {'ggHbb': ROOT.kRed,
               'VBFHbb': ROOT.kBlue-10,
               'Diboson': ROOT.kOrange,
               'SingleTop': ROOT.kViolet+1,
               'DY':  ROOT.kCyan+1,
               'W':  ROOT.kTeal-1,
               'TTbar':  ROOT.kGray,
               'QCD': ROOT.kBlue+1
               }

    style = {'ggHbb': 2,
               'VBFHbb': 3,
               'Diboson': 1,
               'SingleTop': 1,
               'DY': 1,
               'W': 1,
               'TTbar': 1,
               'QCD': 1
               }
        
    print "Signals... "
    sigSamples = {}
    sigSamples['ggHbb']  = sampleContainer(tfiles['ggHbb']  , 1, lumi * 48.85 * 5.824E-01) 
    sigSamples['VBFHbb'] = sampleContainer(tfiles['VBFHbb'], 1, lumi * 3.782E+00 * 5.824E-01)
    print "Backgrounds..."
    bkgSamples = {}
    bkgSamples['Diboson'] = sampleContainer(tfiles['Diboson'], 1, lumi)
    bkgSamples['DY'] = sampleContainer(tfiles['DY'], 1, lumi)
    bkgSamples['SingleTop'] = sampleContainer(tfiles['SingleTop'], 1, lumi)
    bkgSamples['W']  = sampleContainer(tfiles['W'], 1, lumi)
    bkgSamples['TTbar']  = sampleContainer(tfiles['TTbar'], 1, lumi)
    # this 100 scale factor...just makes the QCD run faster, to use all the QCD, make the SF = 1
    bkgSamples['QCD'] = sampleContainer(tfiles['QCD'], 100, lumi) 


    ofile = ROOT.TFile.Open(odir+'/Plots.root','recreate')

    plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_pt_ak8_dbtagCut','h_msd_ak8_dbtagCut','h_t21_ak8','h_t32_ak8']
    for plot in plots:
        hs = {}
        for process, s in sigSamples.iteritems():
            hs[process] = getattr(s,plot)
        hb = {}
        for process, s in bkgSamples.iteritems():
            hb[process] = getattr(s,plot)
        c = makeCanvasComparisonStack(hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi)
        ofile.cd()
        for process, h in hs.iteritems():
            h.Write()
        for process, h in hb.iteritems():
            h.Write()
        
        c.Write()


##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()
    
    main(options,args)
##----##----##----##----##----##----##




