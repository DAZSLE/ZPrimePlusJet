#!/usr/bin/env python
import ROOT as r, sys, math, os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

#r.gSystem.Load("~/Dropbox/RazorAnalyzer/python/lib/libRazorRun2.so")
r.gSystem.Load(os.getenv('CMSSW_BASE') + '/lib/' + os.getenv('SCRAM_ARCH') + '/libHiggsAnalysisCombinedLimit.so')

# including other directories
# sys.path.insert(0, '../.')
from tools import *
from hist import *

MASS_BINS = 23
MASS_LO = 40       # mass range for RooVar
MASS_HI = 201
MASS_HIST_LO = 47   # mass range for histograms
MASS_HIST_HI = 201
BLIND_LO = 110
BLIND_HI = 131
RHO_LO = -6
RHO_HI = -2.1

SF2018={
            #cristina July8
            'shift_SF'  : 0.970,           'shift_SF_ERR' : 0.012,
            'smear_SF'  : 0.9076,          'smear_SF_ERR' : 0.0146,
            'V_SF'      : 0.953,           'V_SF_ERR'     : 0.016,  
            #'smear_SF'  : 0.952,            'smear_SF_ERR' : 0.0495  , # prelim SF @26% N2ddt 
            #'V_SF'      : 0.845,            'V_SF_ERR'     : 0.031   , # prelim SF @26% N2ddt
            #'BB_SF'     : 0.7,              'BB_SF_ERR' : 0.065,      #2018 prelim ddb SF
            #'BB_SF'     : 0.77,             'BB_SF_ERR' : 0.07,     ## M2 SF
            'BB_SF'     : 1.0,             'BB_SF_ERR' : 0.3,     ## M2 SF
}
SF2017={
            #cristina July8
            #'shift_SF'  : 0.978,           'shift_SF_ERR' : 0.012,
            #'smear_SF'  : 0.9045,          'smear_SF_ERR' : 0.048,
            #'V_SF'      : 0.924,           'V_SF_ERR'  : 0.018,  
            #cristina Jun25
            'shift_SF'  : 0.979,           'shift_SF_ERR' : 0.012,
            #'smear_SF'  : 0.911,           'smear_SF_ERR' : 0.0476,
            'smear_SF'  : 1.037,            'smear_SF_ERR' : 0.049   , # prelim SF @26% N2ddt 
            'V_SF'      : 0.92,            'V_SF_ERR'     : 0.018,  

            #'shift_SF'  : 1.001,            'shift_SF_ERR' : 0.0044   , # 2016 shift SF 
            #'smear_SF'  : 1.084,            'smear_SF_ERR' : 0.0905  , #  2016 smear SF 
            #'V_SF'      : 0.993,            'V_SF_ERR'  : 0.043,       # 2016 VSF
            #'shift_SF'  : 1.00,            'shift_SF_ERR' : 0.01   , # prelim SF @26% N2ddt 
            #'shift_SF'  : 1.00,             'shift_SF_ERR' : 0.03   , # prelim SF @26% N2ddt 
            #'V_SF'      : 0.95 ,            'V_SF_ERR'     : 0.02   , # prelim SF @26% N2ddt
            #'BB_SF'     : 0.68,             'BB_SF_ERR' : 0.06       , # prelim ddb SF
            'BB_SF'     : 1.0,             'BB_SF_ERR' : 0.3        , # prelim ddb SF
            #'BB_SF'     : 0.77,             'BB_SF_ERR' : 0.07,     ## M2 SF
}
SF2016={
            #'m_data'    : 82.657,           'm_data_err': 0.313,
            #'m_mc'      : 82.548,           'm_mc_err'  : 0.191,
            #'s_data'    : 8.701,            's_data_err': 0.433,
            #'s_mc'      : 8.027,            's_mc_err'  : 0.607,
            #'BB_SF'     : 0.68,             'BB_SF_ERR' : 0.15,     ## T2 SF
            #'BB_SF'     : 0.77,             'BB_SF_ERR' : 0.07,     ## M2 SF
            'BB_SF'     : 1.0,             'BB_SF_ERR' : 0.3,     ## M2 SF
            'V_SF'      : 0.993,            'V_SF_ERR'  : 0.043,
            'shift_SF'  : 1.001,            'shift_SF_ERR' : 0.012   , # m_data/m_mc, sqrt((m_data_err/m_data)**2+(m_mc_err/m_mc)**2)
            #'shift_SF'  : 1.001,            'shift_SF_ERR' : 0.044   , # m_data/m_mc, sqrt((m_data_err/m_data)**2+(m_mc_err/m_mc)**2)
            'smear_SF'  : 1.084,            'smear_SF_ERR' : 0.0905  , # s_data/s_mc, sqrt((s_data_err/s_data)**2+(s_mc_err/s_mc)**2)
        }
#==================== ddb_Apr17/ddb_M2/msd47_TF21/card_rhalphabet_all_floatZ.root ====================
#qcdeff =  0.0153 +/- 0.0000 
#p0r0 =  -0.7085  +/- 0.0529 
#p0r1 =  2.2649   +/- 0.0350 
#p0r2 =  0.7067   +/- 0.0155 
#p1r0 =  1.1266   +/- 0.0919 
#p1r1 =  1.7097   +/- 0.1284 
#p1r2 =  -0.8651  +/- 0.0997 

#==================== ddb_Jun24_v2/ddb_M2_full/TF22_MC_muonCR_SFJul8/card_rhalphabet_all_2017_floatZ.root ====================
#qcdeff_2017 =  0.0151  +/- 0.0000              (post-fit)
#p0r0_2017   =  -1.0404 +/- 0.0667              p0r0_2017   -9.2544e-01 +/-  1.17e-01
#p0r1_2017   =  2.3977  +/- 0.0406              p0r1_2017    2.3221e+00 +/-  7.27e-02
#p0r2_2017   =  0.7081  +/- 0.0174              p0r2_2017    7.2724e-01 +/-  2.34e-02
#p1r0_2017   =  1.1165  +/- 0.1255              p1r0_2017    1.0017e+00 +/-  2.90e-01
#p1r1_2017   =  1.6787  +/- 0.1259              p1r1_2017    1.7054e+00 +/-  2.45e-01
#p1r2_2017   =  -0.1655 +/- 0.0798              p1r2_2017   -1.7416e-01 +/-  1.30e-01
#p2r0_2017   =  0.1460  +/- 0.1745              p2r0_2017    2.8648e-01 +/-  3.77e-01
#p2r1_2017   =  1.5137  +/- 0.2721              p2r1_2017    1.3657e+00 +/-  5.22e-01
#p2r2_2017   =  -0.0976 +/- 0.3093              p2r2_2017    8.9347e-02 +/-  5.33e-01

#==================== ddb2016_Jun24_v2/ddb_M2_full/TF22_MC_muonCR_SFJul8/card_rhalphabet_all_2016_floatZ.root ====================
#qcdeff_2016 =  0.0145 +/- 0.0000 
#p0r0_2016 =  -1.0210 +/- 0.0610 
#p0r1_2016 =  2.3459  +/- 0.0361 
#p0r2_2016 =  0.6978  +/- 0.0147 
#p1r0_2016 =  0.9232  +/- 0.1238 
#p1r1_2016 =  2.3925  +/- 0.1187 
#p1r2_2016 =  -0.7023  +/- 0.0676 
#p2r0_2016 =  0.5732  +/- 0.1745 
#p2r1_2016 =  1.2283  +/- 0.2591 
#p2r2_2016 =  0.1019  +/- 0.2752 


qcdTFpars={
            #'n_rho':2, 'n_pT':1,
            #'pars':[  0.0153,-0.7085 ,2.2649  ,0.7067  ,1.1266  ,1.7097  ,-0.8651     ]
            #'n_rho':2, 'n_pT':2,
            #'pars':[  0.0151 ,-1.0404,2.3977 ,0.7081 ,1.1165 ,1.6787 ,-0.1655,0.1460 ,1.5137 ,-0.0976]
            'n_rho':2, 'n_pT':2,
            'pars':[  0.0145 ,-1.0210,2.3459 ,0.6978 ,0.9232 ,2.3925 ,-0.7023,0.5732 ,1.2283 ,0.1019 ]
        }

#2016  T2pt350to2000, WPcut=0.92, SF= 0.68  +0.20/-0.10
#2016  M2pt350to2000, WPcut=0.89, SF= 0.77  +0.11/-0.04

#2017  M2pt350to2000, WPcut=0.89, SF= 0.68  +0.05/-0.07
#2018  M2pt350to2000, WPcut=0.89, SF= 0.70  +0.07/-0.06
def main(options, args):
    ifile = options.ifile
    odir = options.odir

    print "loading default rhalphabet_builder"
    from rhalphabet_builder import RhalphabetBuilder, LoadHistograms, GetSF
    # Load the input histograms
    # 	- 2D histograms of pass and fail mass,pT distributions
    # 	- for each MC sample and the data
    f = r.TFile.Open(ifile)    
    fLoose = None
    if options.ifile_loose is not None:
        fLoose = r.TFile.Open(options.ifile_loose)
    if   options.year =='2018':      sf=SF2018
    elif options.year =='2017':      sf=SF2017
    elif options.year =='2016':      sf=SF2016
    #(hpass, hfail) = loadHistograms(f, options.pseudo, options.blind, options.useQCD, options.scale, options.r)
    (pass_hists,fail_hists) = LoadHistograms(f, options.pseudo, options.blind, options.useQCD, scale=options.scale, r_signal=options.r, mass_range=[MASS_HIST_LO, MASS_HIST_HI], blind_range=[BLIND_LO, BLIND_HI], rho_range=[RHO_LO,RHO_HI], fLoose=fLoose,sf_dict=sf,createPassFromFail=options.createPassFromFail,skipQCD=options.skipQCD)
    #f.Close()

    # Build the workspacees
    #dazsleRhalphabetBuilder(hpass, hfail, f, odir, options.NR, options.NP)

    rhalphabuilder = RhalphabetBuilder(pass_hists, fail_hists, f, options.odir, nr=options.NR, np=options.NP, mass_nbins=MASS_BINS, mass_lo=MASS_LO, mass_hi=MASS_HI, blind_lo=BLIND_LO, blind_hi=BLIND_HI, rho_lo=RHO_LO, rho_hi=RHO_HI, blind=options.blind, mass_fit=options.massfit, freeze_poly=options.freeze, remove_unmatched=options.removeUnmatched, input_file_loose=fLoose,suffix=options.suffix,sf_dict=sf,mass_hist_lo=MASS_HIST_LO,mass_hist_hi=MASS_HIST_HI,qcdTFpars=qcdTFpars,exp=options.exp)
    rhalphabuilder.run()
    if options.addHptShape:
        rhalphabuilder.addHptShape()	
    if options.prefit:
        rhalphabuilder.prefit()
    elif options.loadfit is not None:
        rhalphabuilder.loadfit(options.loadfit)
        

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('-i', '--ifile', dest='ifile', default='hist_1DZbb.root', help='file with histogram inputs',
                      metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)',
                      metavar='ifile_loose')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write plots', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='use MC', metavar='pseudo')
    parser.add_option('--blind', action='store_true', dest='blind', default=False, help='blind signal region',
                      metavar='blind')
    parser.add_option('--use-qcd', type='int', dest='useQCD', default=1, help='use real QCD MC',
                      metavar='useQCD')
    parser.add_option('--massfit', action='store_true', dest='massfit', default=False, help='mass fit or rho',
                      metavar='massfit')
    parser.add_option('--exp', action='store_true', dest='exp', default=False, help='use exp(bernstein poly) transfer function',
                      metavar='exp')
    parser.add_option('--freeze', action='store_true', dest='freeze', default=False, help='freeze pol values',
                      metavar='freeze')
    parser.add_option('--scale', dest='scale', default=1, type='float',
                      help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('--nr', dest='NR', default=2, type='int', help='order of rho (or mass) polynomial')
    parser.add_option('--np', dest='NP', default=1, type='int', help='order of pt polynomial')
    parser.add_option('-r', dest='r', default=1, type='float', help='signal strength for MC pseudodataset')
    parser.add_option('--remove-unmatched', action='store_true', dest='removeUnmatched', default =False,help='remove unmatched', metavar='removeUnmatched')
    parser.add_option('--prefit', action='store_true', dest='prefit', default =False,help='do prefit', metavar='prefit')
    parser.add_option('--addHptShape',action='store_true',dest='addHptShape',default =False,help='add H pt shape unc', metavar='addHptShape')
    parser.add_option('--loadfit', dest='loadfit', default=None, help='load qcd polynomial parameters from alternative rhalphabase.root',metavar='loadfit')
    parser.add_option('-y' ,'--year', type='choice', dest='year', default ='2016',choices=['2016','2017','2018'],help='switch to use different year ', metavar='year')
    parser.add_option('--suffix', dest='suffix', default='', help='suffix for conflict variables',metavar='suffix')
    parser.add_option('--createPassFromFail', action='store_true', dest='createPassFromFail', default=False, help='Creating data_obs pass from data_obs fail', metavar='createPassFromFail')
    parser.add_option('--skipQCD', action='store_true', dest='skipQCD', default=False, help='skipQCD MC template', metavar='skipQCD')

    (options, args) = parser.parse_args()

    import tdrstyle

    tdrstyle.setTDRStyle()
    r.gStyle.SetPadTopMargin(0.10)
    r.gStyle.SetPadLeftMargin(0.16)
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPalette(1)
    r.gStyle.SetPaintTextFormat("1.1f")
    r.gStyle.SetOptFit(0000)
    r.gROOT.SetBatch()

    main(options, args)
##-------------------------------------------------------------------------------------
