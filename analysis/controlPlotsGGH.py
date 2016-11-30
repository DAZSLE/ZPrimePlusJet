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
    isData = options.isData
    muonCR = options.muonCR

    
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'ZHbb': 'ZH(b#bar{b})',
	           'WHbb': 'WH(b#bar{b})',
	           'ttHbb': 't#bar{t}H(b#bar{b})',
               'Diboson': 'VV(4q)',
               'SingleTop': 'single-t',
               'DY': 'Z+jets',
               'W': 'W+jets',
               'TTbar': 't#bar{t}+jets',        
               'TTbar1Mu': 't#bar{t}+jets, 1#mu',  
               'TTbar1Ele': 't#bar{t}+jets, 1e',        
               'TTbar1Tau': 't#bar{t}+jets, 1#tau',        
               'TTbar0Lep': 't#bar{t}+jets, 0l',        
               'QCD': 'QCD',
		       'data': 'JetHT data',
               'muon': 'SingleMuon data'
               }

    if isData and muonCR:
        legname['data'] = 'SingleMuon data'
        
    tfiles = {'ggHbb': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'VBFHbb': [idir+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8_1000pb_weighted.root'],
              'ZHbb': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'WHbb': [idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'Diboson': [idir+'/WWTo4Q_13TeV_amcatnlo_1000pb_weighted.root',idir+'/ZZTo4Q_13TeV_amcatnlo_1000pb_weighted.root'],
              'DY': [idir+'/DY_1000pb_weighted.root '],
              'SingleTop':  [idir+'/ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root',
		                     idir+'/ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root',
		                     idir+'/ST_tW_antitop_5f_inclusiveDecays_13TeV_1000pb_weighted.root',
		                     idir+'/ST_tW_top_5f_inclusiveDecays_13TeV_1000pb_weighted.root'],
              'W':  [idir+'/WJets_1000pb_weighted.root'],
              'ttHbb':  [idir+'/ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'TTbar':  [idir+'/TTJets_13TeV_1000pb_weighted.root'],
              'QCD': [idir+'/QCD_HT200to300_1000pb_weighted.root',
                      idir+'/QCD_HT300to500_1000pb_weighted.root',
                      idir+'/QCD_HT500to700_1000pb_weighted.root',
                      idir+'/QCD_HT700to1000_1000pb_weighted.root',
                      idir+'/QCD_HT1000to1500_1000pb_weighted.root',
                      idir+'/QCD_HT2000toInf_1000pb_weighted.root',
                      idir+'/QCD_HT1500to2000_1000pb_weighted.root'],
              'data': [idir+'/JetHT.root'],
              'muon': [idir+'/SingleMuonRun2016B_PromptReco_v2.root',
                       idir+'/SingleMuonRun2016C_PromptReco_v2.root',
                       idir+'/SingleMuonRun2016D_PromptReco_v2.root',
                       idir+'/SingleMuonRun2016E_PromptReco_v2.root',
                       idir+'/SingleMuonRun2016F_PromptReco_v1.root',
                       idir+'/SingleMuonRun2016G_PromptReco_v1.root']
            }

    color = {'ggHbb': ROOT.kRed,
             'VBFHbb': ROOT.kBlue-10,
		     'ZHbb': ROOT.kAzure+1,
		     'WHbb': ROOT.kTeal+1,
		     'ttHbb': ROOT.kBlue-1,
             'Diboson': ROOT.kOrange,
             'SingleTop': ROOT.kRed-2,
             'DY':  ROOT.kRed,
             'W':  ROOT.kTeal-1,
             #'TTbar':  ROOT.kGray,
             'TTbar1Mu':  ROOT.kViolet,
             'TTbar1Ele':  ROOT.kSpring,
             'TTbar1Tau':  ROOT.kOrange+2,
             'TTbar0Lep':  ROOT.kGray,
             'QCD': ROOT.kBlue+1,
		     'data':ROOT.kBlack,
		     'muon':ROOT.kBlack
            }

    style = {'ggHbb': 2,
             'VBFHbb': 3,
		     'ZHbb': 4,
		     'WHbb': 4,
		     'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'DY': 1,
             'W': 1,
             #'TTbar': 1,
             'TTbar1Mu': 1,
             'TTbar1Ele': 1,
             'TTbar1Tau': 1,
             'TTbar0Lep': 1,
             'QCD': 1,
             'data': 1,
		     'muon':1
            }
        
    print "Signals... "
    sigSamples = {}
    sigSamples['ggHbb']  = sampleContainer(tfiles['ggHbb']  , 1, lumi) 
    sigSamples['VBFHbb'] = sampleContainer(tfiles['VBFHbb'], 1, lumi ) 
    sigSamples['ZHbb'] = sampleContainer(tfiles['ZHbb'], 1, lumi ) 	
    sigSamples['WHbb'] = sampleContainer(tfiles['WHbb'], 1, lumi ) 	
    sigSamples['ttHbb'] = sampleContainer(tfiles['ttHbb'], 1, lumi ) 	
    print "Backgrounds..."
    bkgSamples = {}
    #bkgSamples['QCD'] = sampleContainer(tfiles['QCD'], 100, lumi)
    #bkgSamples['TTbar']  = sampleContainer(tfiles['TTbar'], 1, lumi, False, False)
    bkgSamples['TTbar1Mu']  = sampleContainer(tfiles['TTbar'], 1, lumi, False, False, 'genMuFromW==1&&genEleFromW+genTauFromW==0')
    bkgSamples['TTbar1Ele']  = sampleContainer(tfiles['TTbar'], 1, lumi, False, False, 'genEleFromW==1&&genMuFromW+genTauFromW==0')
    bkgSamples['TTbar1Tau']  = sampleContainer(tfiles['TTbar'], 1, lumi, False, False, 'genTauFromW==1&&genEleFromW+genMuFromW==0')
    bkgSamples['TTbar0Lep']  = sampleContainer(tfiles['TTbar'], 1, lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==0')
    #bkgSamples['SingleTop'] = sampleContainer(tfiles['SingleTop'], 1, lumi)
    #bkgSamples['Diboson'] = sampleContainer(tfiles['Diboson'], 1, lumi)
    #bkgSamples['W']  = sampleContainer(tfiles['W'], 1, lumi)
    #bkgSamples['DY']  = sampleContainer(tfiles['DY'], 1, lumi)
    
    if isData and muonCR:
        dataSample = sampleContainer(tfiles['muon'], 1, lumi, isData, False, '((triggerBits&4)&&passJson)')
    elif isData:
        dataSample = sampleContainer(tfiles['data'], 1, lumi, isData, False, '((triggerBits&2)&&passJson)')
        


    ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root ','recreate')


    canvases = []
    if isData and muonCR:
        plots = ['h_msd_ak8_muCR1','h_msd_ak8_muCR2','h_msd_ak8_muCR3','h_msd_ak8_muCR4','h_msd_ak8_muCR5','h_msd_ak8_muCR6']        
    elif isData:
        plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_t21_ak8','h_t32_ak8','h_n2b1sdddt_ak8','h_t21ddt_ak8']
    else:	
    	plots = ['h_pt_ak8','h_pt_ak8_sub1','h_pt_ak8_sub2','h_msd_ak8','h_dbtag_ak8','h_dbtag_ak8_sub1','h_dbtag_ak8_sub2',
                 'h_n_ak4','h_n_ak4_dR0p8','h_pt_ak8_dbtagCut','h_msd_ak8_dbtagCut',
                 'h_t21_ak8','h_t32_ak8','h_msd_ak8_t21ddtCut','h_msd_ak8_N2Cut','h_n_ak4_fwd',
                 'h_n_ak4L','h_n_ak4M','h_n_ak4T','h_n_ak4L100','h_n_ak4M100','h_n_ak4T100',
                 'h_n_ak4_dR0p8','h_isolationCA15','h_n2b1sdddt_ak8','h_t21ddt_ak8','h_msd_ak8_topR1','h_msd_ak8_topR2',
                 'h_msd_ak8_topR3','h_msd_ak8_topR4','h_met','h_t32_ak8_t21ddtCut','h_msd_ak8_topR5','h_msd_ak8_topR6','h_msd_ak8_topR7',
                 'h_msd_ak8_muCR1','h_msd_ak8_muCR2','h_msd_ak8_muCR3','h_msd_ak8_muCR4','h_msd_ak8_muCR5','h_msd_ak8_muCR6']
    for plot in plots:
        hs = {}
        hb = {}
        hall={}
        for process, s in sigSamples.iteritems():
            hs[process] = getattr(s,plot)
            hall[process] = getattr(s,plot)
        for process, s in bkgSamples.iteritems():
            hb[process] = getattr(s,plot)
            hall[process] = getattr(s,plot)
        if isData:
            hd = getattr(dataSample,plot)
            c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile)
        else:
            c = makeCanvasComparisonStack(hs,hb,legname,color,style,'ggHbb',plot.replace('h_','stack_'),odir,lumi,ofile)
            c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile,True)
        canvases.append(c)	


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 30,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    parser.add_option('-m','--muonCR', action='store_true', dest='muonCR', default =False,help='for muon CR', metavar='muonCR')

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




