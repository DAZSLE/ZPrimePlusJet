#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

# including other directories
sys.path.insert(0, '../.')
from tools import *


##-------------------------------------------------------------------------------------
def main(options,args):
    
    if not os.path.isdir(options.odir+"plots"):         os.mkdir(options.odir+ "plots" );
    if not os.path.isdir(options.odir+"plots/hinputs"): os.mkdir(options.odir+ "plots/hinputs" );

    # plot input histos
    #do2DHistInputs(options.idir+"../data/hist_1DZbb_pt_scalesmear.root");

    # Load the input histograms
    fhist = r.TFile(options.idir+"../data/hist_1DZbb_pt_scalesmear.root")

    if options.suffix:
        fcard = r.TFile(options.idir+"card_rhalphabet_all_%s_floatZ.root"%options.suffix);
    else:
        fcard = r.TFile(options.idir+"card_rhalphabet_all_floatZ.root");
    fml   = r.TFile(options.idir+"mlfit.root");
    f     = r.TFile(options.idir+"base.root");
    fr    = r.TFile(options.idir+"rhalphabase.root");

    wp = f.Get("w_pass_cat1");
    wf = f.Get("w_fail_cat1");
    wpr = fr.Get("w_pass_cat1");
    wfr = fr.Get("w_fail_cat1");

    # wp.Print();
    # wf.Print();
    #wpr.Print();
    #wfr.Print();
    #ReplaceQCDpass(f,fr,"poissonQCD",True)
    #ReplaceQCDpass(f,fr,"fakeQCD",False)
    #RescaleVqq('rescaledVqq','ddb_Apr17/ddb_M2_full/data/')

    for i in range(6): 
        #drawCategory(f,fr,fhist,fml,"cat"+str(i+1));
        #drawProcess(f,fml,['qcd','zqq','wqq'],'cat'+str(i+1))
        drawProcess(f,fml,['zqq','wqq'],'cat'+str(i+1),nostack=True)
        drawProcess(f,fml,['zqq','wqq'],'cat'+str(i+1),nostack=False)
        pass
    MergeDrawProcess(nostack=True)
    MergeDrawProcess(nostack=False)

def MergeDrawProcess(nostack=True):
    for pf in ['pass','fail']:
        cmd = ' montage -density 500 -tile 3x0 -geometry 1600x1600 -border 5 '
        if nostack:
            plotName = options.odir+"plots/"+"_".join(["shapes",pf,'nostack',"cat*"])
            plotpdf = options.odir+"plots/"+"_".join(["shapes",pf,'nostack'])
        else:
            plotName = options.odir+"plots/"+"_".join(["shapes",pf,'stack',"cat*"])
            plotpdf = options.odir+"plots/"+"_".join(["shapes",pf,'stack'])

        cmd += plotName+".png"
        cmd += ' ' 
        cmd += plotpdf+".pdf"
        print cmd
        os.system(cmd)
        print 'rm '+plotName+".png"
        os.system('rm '+plotName+'.png')


###############################################################
def getShape(fml,pf,catname,proc,fit):
    rags        = fml.Get("norm_" + fit)
    if options.suffix:
        suffix = options.suffix
        shape       = fml.Get("shapes_%s/%s_%s_%s_%s/%s"%(fit,catname,suffix,pf,catname,proc))
        rrvName     = "%s_%s_%s_%s/%s" % (catname,suffix,pf,catname, proc)
    else:
        shape       = fml.Get("shapes_%s/%s_%s_%s/%s"%(fit,catname,pf,catname,proc))
        rrvName     = "%s_%s_%s/%s" % (catname,pf,catname, proc)
    if rags.find(rrvName) != None:
      rrv = r.RooRealVar(rags.find(rrvName))
      norm = rrv.getVal()
    else:
        raise ValueError("Cannot find rrv %s in  %s/%s"%(rrvName,"_".join([catname,pf,catname]),proc))
    print rrvName, norm, shape.Integral()
    if norm>0 and shape.Integral()>0: 
        shape.Scale(norm/shape.Integral())
    else:
        if not ('125' in proc and fit =='fit_b'):
            raise ValueError("Norm or integral of %s <=0, norm = %s, integral = %s"%("_".join([proc,catname,pf]),norm,shape.Integral()))
    if fit =='prefit': kColor = r.kBlack
    if fit =='fit_b' : kColor = r.kBlue
    if fit =='fit_s' : kColor = r.kRed
    shape.SetLineColor(kColor)
    shape.SetMarkerColor(kColor)
    shape.SetLineWidth(2)
    return shape

def drawProcess(f,fml,procs,catname,nostack=True): 
    for pf in ['pass','fail']:
        cp = r.TCanvas("cp","cp",1000,800);
        leg = r.TLegend(0.7,0.7,0.9,0.9)
        maxs = []
        stacks = []
        wp      = f.Get("w_%s_%s"%(pf,catname))
        dh_d_p  = wp.data("data_obs_%s_%s"%(pf,catname))
        x   = wp.var("x"); 
        frame = x.frame()

        subtractQCD = True
        if subtractQCD:  
            data_shapes = [] 
            #for fit in ['prefit','fit_b','fit_s']:
            for fit in ['fit_b']:
                qcdshape  = getShape(fml,pf,catname,'qcd',fit)
                tqqshape  = getShape(fml,pf,catname,'tqq',fit)
                dataShape = dh_d_p.createHistogram("h_dataMinusBkg_"+catname,x)
                dataShape.Add(qcdshape,-1)
                dataShape.Add(tqqshape,-1)
                dataShape.SetMarkerColor(r.kBlack)
                dataShape.Draw("pe same")
                leg.AddEntry(dataShape,'data-QCD-tqq(fit_b)','p')
        else:
            dh_d_p.plotOn(frame, r.RooFit.DrawOption("pe same"), r.RooFit.MarkerColor(r.kBlack));
            frame.Draw()

        suffix = options.suffix
        for fit in ['prefit','fit_b','fit_s']:
        #for fit in ['prefit','fit_b']:
            stack = r.THStack('stack_%s_%s'%(pf,fit),"")
            for i,proc in enumerate(procs):
                #print "shapes_%s/%s_%s_%s/%s"%(fit,catname,pf,catname,proc)
                rags        = fml.Get("norm_" + fit)
                if options.suffix:
                    shape       = fml.Get("shapes_%s/%s_%s_%s_%s/%s"%(fit,catname,suffix,pf,catname,proc))
                    rrvName     = "%s_%s_%s_%s/%s" % (catname,suffix,pf,catname, proc)
                else:
                    shape       = fml.Get("shapes_%s/%s_%s_%s/%s"%(fit,catname,pf,catname,proc))
                    rrvName     = "%s_%s_%s/%s" % (catname,pf,catname, proc)
                if rags.find(rrvName) != None:
                  rrv = r.RooRealVar(rags.find(rrvName))
                  norm = rrv.getVal()
                else:
                    raise ValueError("Cannot find rrv %s in  %s/%s"%(rrvName,"_".join([catname,pf,catname]),proc))
                print rrvName, norm, shape.Integral()
                if norm>0 and shape.Integral()>0: 
                    shape.Scale(norm/shape.Integral())
                else:
                    #if not ('125' in proc and fit =='fit_b'):
                    #    raise ValueError("Norm or integral of %s <=0, norm = %s, integral = %s"%("_".join([proc,catname,pf]),norm,shape.Integral()))
                    pass
                if fit =='prefit': kColor = r.kBlack
                if fit =='fit_b' : kColor = r.kBlue
                if fit =='fit_s' : kColor = r.kRed
                shape.SetLineColor(kColor)
                shape.SetMarkerColor(kColor)
                shape.SetLineStyle(i+1)
                shape.SetLineWidth(2)
                stack.Add(shape)
                leg.AddEntry(shape," ".join([proc,pf,fit]),'l')
            stacks.append(stack)
        for stack in stacks:
            if nostack:
                stack.Draw("same nostack hist")
            else:
                stack.Draw("same hist")

        leg.Draw("same")
        if nostack:
            plotName =options.odir+"plots/"+"_".join(["shapes",pf,'nostack',catname])
        else:
            plotName =options.odir+"plots/"+"_".join(["shapes",pf,'stack',catname])
        cp.SaveAs(plotName+".pdf")
        cp.SaveAs(plotName+".png")
        

def RescaleVqq(fhist_outdir,ref_dir):
    vqqIn = options.idir+"../data/hist_1DZbb_pt_scalesmear.root"
    vqqRef= ref_dir+"../data/hist_1DZbb_pt_scalesmear.root"
    vqqOut= vqqIn.replace("data",fhist_outdir)

    if not os.path.isdir(options.idir+"../%s"%fhist_outdir):
       os.mkdir(options.idir+"../%s"%fhist_outdir )

    os.system("cp %s %s"%(vqqIn,vqqOut))
    fhist_Out       = r.TFile(vqqOut,"UPDATE")
    fhist_ref       = r.TFile(vqqRef,"READ")
    for proc in ['zqq','wqq']:
        for pf in ['pass','fail']:
            hname = '_'.join([proc,pf,'matched'])
            href  = fhist_ref.Get(hname)
            hout  = fhist_Out.Get(hname)
            hout.SetDirectory(0)
            ratio =  href.Integral()/hout.Integral()
            print hname, " Ref integral: %.3f"% href.Integral(), ' out integral: %.3f '% hout.Integral(), ' ratio = %.3f'%ratio
            hout.Scale(ratio)
            print "After scale: %.3f"% hout.Integral()
            fhist_Out.cd()
            hout.Write()

def ReplaceQCDpass(f,fr,fhist_outdir,doPoisson=False):
    qcdIn = options.idir+"../data/hist_1DZbb_pt_scalesmear.root"
    qcdOut= qcdIn.replace("data",fhist_outdir)

    if not os.path.isdir(options.idir+"../%s"%fhist_outdir):
       os.mkdir(options.idir+"../%s"%fhist_outdir )

    os.system("cp %s %s"%(qcdIn,qcdOut))
    fhist_Out       = r.TFile(qcdOut,"UPDATE")
    qcdpass = fhist_Out.Get("qcd_pass")
    qcdpass.SetDirectory(0)
    for i in range(6):
        catname = "cat"+str(i+1) 
        wp           = f.Get("w_pass_"+catname);
        wpr          = fr.Get("w_pass_"+catname);
        rrv          = wp.var("x"); 
        #QCD fail x T.F. pdf
        ph_q_p       = wpr.pdf("qcd_pass_"+catname);
        #norm (QCD fail x T.F. pdf)
        ph_q_p_norm  = wpr.function("qcd_pass_"+catname+"_norm").getVal();

        h_ph_q_p = ph_q_p.createHistogram('h_qcd_pass_'+catname,rrv)
        h_ph_q_p.Scale(ph_q_p_norm)

        #Update qcdpass bin content
        ptbin = i+1
        for xbin in range(0,qcdpass.GetXaxis().GetNbins()+1):
            print  xbin, ptbin,h_ph_q_p.GetBinContent(xbin), r.gRandom.Poisson(h_ph_q_p.GetBinContent(xbin))
            if doPoisson:
                binContent = r.gRandom.Poisson(h_ph_q_p.GetBinContent(xbin))
                qcdpass.SetBinContent( xbin, ptbin, binContent)
                qcdpass.SetBinError( xbin, ptbin, binContent**0.5)
            else:
                qcdpass.SetBinContent( xbin, ptbin, h_ph_q_p.GetBinContent(xbin))
                qcdpass.SetBinError( xbin, ptbin, h_ph_q_p.GetBinError(xbin))
    fhist_Out.cd()
    qcdpass.Write()


def drawCategory(f,fr,fhist,fml,catname):

    wp = f.Get("w_pass_"+catname);
    wf = f.Get("w_fail_"+catname);
    wpr = fr.Get("w_pass_"+catname);
    wfr = fr.Get("w_fail_"+catname);

    rrv   = wp.var("x"); 
    dh_w_p  = wp.data("wqq_pass_"+catname);
    dh_z_p  = wp.data("zqq_pass_"+catname);

    dh_t_p  = wp.data("tqq_pass_"+catname);
    ph_q_p  = wpr.pdf("qcd_pass_"+catname);
    ph_q_p_norm  = wpr.function("qcd_pass_"+catname+"_norm").getVal();
    dh_d_p  = wp.data("data_obs_pass_"+catname);

    leg_p = r.TLegend(0.7,0.7,0.9,0.9)
    ipt = int(catname[-1])-1
    h2  = fhist.Get("qcd_pass")
    h1  = h2.ProjectionX( "px_" + h2.GetName() + str(ipt), ipt+1, ipt+1 );
    leg_p.AddEntry(h1, 'qcdMC','l')

    dh_w_f  = wf.data("wqq_fail_"+catname);
    dh_z_f  = wf.data("zqq_fail_"+catname);
    dh_t_f  = wf.data("tqq_fail_"+catname);
    ph_q_f  = wfr.pdf("qcd_fail_"+catname);
    dh_d_f  = wf.data("data_obs_fail_"+catname);

    frame_p = rrv.frame();
    dh_w_p.plotOn(frame_p,r.RooFit.Name('wqq') ,r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kRed));
    dh_z_p.plotOn(frame_p,r.RooFit.Name('zqq') ,r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kGreen));
    dh_t_p.plotOn(frame_p,r.RooFit.Name('tqq') ,r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kBlue));
    h_ph_q_p = ph_q_p.createHistogram('h_qcd_pass_'+catname,rrv)
    h_ph_q_p.Scale(ph_q_p_norm)
    

    dh_d_p.plotOn(frame_p,r.RooFit.Name('data_obs'), r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kBlack));
    ph_q_f.plotOn(frame_p,r.RooFit.Name('qcd_fail'), r.RooFit.LineColor(r.kRed));

    frame_f = rrv.frame();
    dh_w_f.plotOn(frame_f,r.RooFit.Name('wqq')     , r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kRed));
    dh_z_f.plotOn(frame_f,r.RooFit.Name('zqq')     , r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kGreen));
    dh_t_f.plotOn(frame_f,r.RooFit.Name('tqq')     , r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kBlue));
    ph_q_f.plotOn(frame_f,r.RooFit.Name('qcd_fail'), r.RooFit.LineColor(r.kRed));
    dh_d_f.plotOn(frame_f,r.RooFit.Name('data_obs'), r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kBlack));

    cp = r.TCanvas("cp","cp",1000,800);
    frame_p.Draw();
    leg_p.AddEntry(h_ph_q_p,'Fail x TF','l')
    leg_p.AddEntry(frame_p.findObject("qcd_fail"),'Fail','l')
    leg_p.AddEntry(frame_p.findObject("data_obs"),'data_obs','pe')
    leg_p.AddEntry(frame_p.findObject("wqq"),'wqq','pe')
    leg_p.AddEntry(frame_p.findObject("zqq"),'zqq','pe')
    leg_p.AddEntry(frame_p.findObject("tqq"),'tqq','pe')

    h_ph_q_p.SetLineColor(r.kViolet)
    h_ph_q_p.Draw("same")
    h1.Draw("same ep")
    leg_p.SetFillColor(r.kWhite)
    leg_p.SetLineColor(r.kWhite)
    leg_p.Draw("same")
    cp.SaveAs(options.odir+"plots/mass-pass-"+catname+".pdf");
    #cp.SaveAs("plots/mass-pass-"+catname+".png");
    #r.gPad.SetLogy();
    #cp.SaveAs("plots/mass-pass-"+catname+"-log.pdf");
    #cp.SaveAs("plots/mass-pass-"+catname+"-log.png");

    cf = r.TCanvas("cf","cf",1000,800);
    frame_f.Draw();
    cf.SaveAs(options.odir+"plots/mass-fail-"+catname+".pdf");
    #cf.SaveAs("plots/mass-fail-"+catname+".png");
    #r.gPad.SetLogy();
    #cf.SaveAs("plots/mass-fail-"+catname+"-log.pdf");
    #cf.SaveAs("plots/mass-fail-"+catname+"-log.png");


    ######## Some print outs
 #      print "-------"
 #      print "qcd_fail_cat1_Bin1 = ", wfr.var("qcd_fail_cat1_Bin1").getValV();
 #      print "qcdeff = ", wpr.var("qcdeff").getValV();

    # # "Var_RhoPol_Bin_530.0_-10.138"
    # #     "Var_Pol_Bin_530.0_-10.138_0"
    # #         "r0","p1"
    # #     "Var_Pol_Bin_530.0_-10.138_1"
    # #         "r1","pr11"
 #      print "r0 = ", wpr.var("r0").getValV();
 #      print "p1 = ", wpr.var("p1").getValV();
 #      print "r1 = ", wpr.var("r1").getValV();
 #      print "pr11 = ", wpr.var("pr11").getValV();

###############################################################
###############################################################
###############################################################


def do2DHistInputs(fn):

    tf = r.TFile(fn);
    h2s = [];
    h2s.append( tf.Get("qcd_pass") );
    h2s.append( tf.Get("qcd_fail") );
    h2s.append( tf.Get("wqq_pass") );
    h2s.append( tf.Get("wqq_fail") );
    h2s.append( tf.Get("zqq_pass") );
    h2s.append( tf.Get("zqq_fail") );
    h2s.append( tf.Get("tqq_pass") );
    h2s.append( tf.Get("tqq_fail") );
    h2s.append( tf.Get("hqq125_pass") );
    h2s.append( tf.Get("hqq125_fail") );

    for h2 in h2s:
        for ipt in range(h2.GetNbinsY()):
            tmph1 = h2.ProjectionX( "px_" + h2.GetName() + str(ipt), ipt+1, ipt+1 );
            makeCanvas(tmph1);

def makeCanvas(h):

    c = r.TCanvas("c","c",1000,800);
    h.Draw("hist");
    c.SaveAs(options.odir+"plots/hinputs/"+h.GetName()+".pdf");
    r.gPad.SetLogy();
    c.SaveAs(options.odir+"plots/hinputs/"+h.GetName()+"_log.pdf");
    
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--suffix', dest='suffix', default = '',help='directory to write plots', metavar='suffix')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')

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
    
    main(options,args)
##-------------------------------------------------------------------------------------
