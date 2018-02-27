import ROOT as r,sys,math,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array


def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

def makedirs_wrap(dir):
    import errno
    try:
        os.makedirs(dir)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

        
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('--model',dest="model", default="DMSbb",type="string", help="signal model name")
    parser.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('--nr1' ,action='store',type='int',dest='NR1'   ,default=1, help='order of rho polynomial for model 1')
    parser.add_option('--np1' ,action='store',type='int',dest='NP1'   ,default=1, help='order of pt polynomial for model 1')
    parser.add_option('--nr2' ,action='store',type='int',dest='NR2'   ,default=2, help='order of rho polynomial for model 2')
    parser.add_option('--np2' ,action='store',type='int',dest='NP2'   ,default=1, help='order of pt polynomial for model 2')
    parser.add_option('--scale',dest='scale', default=1,type='float',help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z templates)',metavar='ifile_loose')
    parser.add_option('-t','--toys'   ,action='store',type='int',dest='toys'   ,default=200, help='number of toys')
    parser.add_option('-r','--r',dest='r', default='0' ,type='string',help='default value of r')    
    parser.add_option('-n','--n' ,action='store',type='int',dest='n'   ,default=5*20, help='number of bins')
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='run on asimov dataset')
    parser.add_option('--blind', action='store_true', dest='blind', default=False, help='run on blinded dataset')
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")    
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write plots', metavar='odir')
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('-b','--box',dest="box", default="AK8",type="string", help="box name")
    parser.add_option('--lrho', dest='lrho', default=-6.0, type= 'float', help='low value rho cut')
    parser.add_option('--hrho', dest='hrho', default=-2.1, type='float', help=' high value rho cut')
    parser.add_option('--seed' ,action='store',type='int',dest='seed'   ,default=-1, help='random seed')


    (options,args) = parser.parse_args()
    jet_type = options.box
    cut = options.cuts.split(',')[0]
    
    if options.pseudo:
        rhalphDir1 = '%s/cards_mc_r%ip%i'%(options.odir,options.NR1,options.NP1)
        rhalphDir2 = '%s/cards_mc_r%ip%i'%(options.odir,options.NR2,options.NP2)
        cardsDir1 = '%s/cards_mc_r%ip%i/%s/%s'%(options.odir,options.NR1,options.NP1, jet_type, cut)
        cardsDir2 = '%s/cards_mc_r%ip%i/%s/%s'%(options.odir,options.NR2,options.NP2, jet_type, cut)
        sigDir1 = '%s/cards_mc_r%ip%i/%s/%s/%s'%(options.odir,options.NR1,options.NP1, jet_type, cut, options.model+str(options.mass))
        sigDir2 = '%s/cards_mc_r%ip%i/%s/%s/%s'%(options.odir,options.NR2,options.NP2, jet_type, cut, options.model+str(options.mass))
    else:        
        rhalphDir1 = '%s/cards_r%ip%i'%(options.odir,options.NR1,options.NP1)
        rhalphDir2 = '%s/cards_r%ip%i'%(options.odir,options.NR2,options.NP2)
        cardsDir1 = '%s/cards_r%ip%i/%s/%s'%(options.odir,options.NR1,options.NP1, jet_type, cut)
        cardsDir2 = '%s/cards_r%ip%i/%s/%s'%(options.odir,options.NR2,options.NP2, jet_type, cut)
        sigDir1 = '%s/cards_r%ip%i/%s/%s/%s'%(options.odir,options.NR1,options.NP1, jet_type, cut, options.model+str(options.mass))
        sigDir2 = '%s/cards_r%ip%i/%s/%s/%s'%(options.odir,options.NR2,options.NP2, jet_type, cut, options.model+str(options.mass))
        
    ftestDir_muonCR = '%s/ftest_r%ip%i_r%ip%i_muonCR/%s/%s'%(options.odir,options.NR1, options.NP1, options.NR2, options.NP2, jet_type, cut)
    ftestDir = '%s/ftest_r%ip%i_r%ip%i/%s/%s'%(options.odir,options.NR1, options.NP1, options.NR2, options.NP2, jet_type, cut)

    pseudoString = ''
    if options.pseudo:
        pseudoString = '--pseudo'

    blindString = ''
    if options.blind:
        blindString = '--blind'

    import errno
    try:
        makedirs_wrap(ftestDir_muonCR)
        makedirs_wrap(ftestDir)
        makedirs_wrap(rhalphDir1)
        makedirs_wrap(rhalphDir2)
        makedirs_wrap(cardsDir1)
        makedirs_wrap(cardsDir2)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    if options.ifile_loose is not None:
        ifile_loose = '--ifile-loose %s'%options.ifile_loose
    else:
        ifile_loose = ''
    #if not os.path.isfile('%s/base.root'%cardsDir1) and not os.path.isfile('%s/rhalphabase.root'%cardsDir1):
    if True:
        exec_me('python buildRhalphabetPhibb.py -i %s %s --scale %f -o %s --nr %i --np %i %s %s --remove-unmatched --prefit --use-qcd -c %s --lrho %f --hrho %f --masses %s'%(options.ifile, ifile_loose, options.scale, cardsDir1, options.NR1, options.NP1, blindString, pseudoString, cut, options.lrho, options.hrho, options.mass),options.dryRun )
        
    #if not os.path.isfile('%s/base.root'%cardsDir2) and not os.path.isfile('%s/rhalphabase.root'%cardsDir2):
    if True:
        exec_me('python buildRhalphabetPhibb.py -i %s %s --scale %f -o %s --nr %i --np %i %s %s --remove-unmatched --prefit --use-qcd -c %s --lrho %f --hrho %f --masses %s'%(options.ifile, ifile_loose, options.scale, cardsDir2, options.NR2, options.NP2, blindString, pseudoString, cut, options.lrho, options.hrho, options.mass),options.dryRun )
    exec_me('python makeCardsPhibb.py -i %s %s -o %s/ --remove-unmatched --no-mcstat-shape  -c %s --lrho %f --hrho %f'%(options.ifile,ifile_loose,
                                                                                                                           cardsDir1, cut,
                                                                                                                           options.lrho,
                                                                                                                           options.hrho),options.dryRun)
    exec_me('python makeCardsPhibb.py -i %s %s -o %s/ --remove-unmatched --no-mcstat-shape  -c %s --lrho %f --hrho %f'%(options.ifile,ifile_loose,
                                                                                                                           cardsDir2, cut,
                                                                                                                           options.lrho,
                                                                                                                           options.hrho),options.dryRun)
    
    exec_me('cp %s/base.root %s/'%(cardsDir1,sigDir1),options.dryRun)
    exec_me('cp %s/rhalphabase.root %s/'%(cardsDir1,sigDir1),options.dryRun)
    exec_me('cp %s/base.root %s/'%(cardsDir2,sigDir2),options.dryRun)
    exec_me('cp %s/rhalphabase.root %s/'%(cardsDir2,sigDir2),options.dryRun)
    
    fillString = ''
    if options.box=='CA15':
        fillString = '--fillCA15'
    if not options.pseudo:
        exec_me('python writeMuonCRDatacard.py -i %s/ -o %s/ -c %s --mass %s %s --no-mcstat-shape'%(os.path.dirname(options.ifile),sigDir1, cut, options.mass, fillString),options.dryRun)
        exec_me('python writeMuonCRDatacard.py -i %s/ -o %s/ -c %s --mass %s %s --no-mcstat-shape'%(os.path.dirname(options.ifile),sigDir2, cut, options.mass, fillString),options.dryRun)
    
    
    if not options.pseudo:
        if options.box=='CA15':
            exec_me('combineCards.py cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt muonCR=%s/datacard_muonCR.txt > %s/card_rhalphabet_muonCR_r%ip%i_%s_%s.txt'%(sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,options.NR1, options.NP1, options.box, cut),options.dryRun)

            exec_me('combineCards.py cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt muonCR=%s/datacard_muonCR.txt > %s/card_rhalphabet_muonCR_r%ip%i_%s_%s.txt'%(sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,options.NR2, options.NP2, options.box, cut),options.dryRun)
        else:
            exec_me('combineCards.py cat1=%s/card_rhalphabet_cat1.txt cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt muonCR=%s/datacard_muonCR.txt > %s/card_rhalphabet_muonCR_r%ip%i_%s_%s.txt'%(sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,options.NR1, options.NP1, options.box, cut),options.dryRun)
            exec_me('combineCards.py cat1=%s/card_rhalphabet_cat1.txt cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt muonCR=%s/datacard_muonCR.txt > %s/card_rhalphabet_muonCR_r%ip%i_%s_%s.txt'%(sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,options.NR2, options.NP2, options.box, cut),options.dryRun)
        #exec_me("text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' %s/card_rhalphabet_muonCR_r%ip%i.txt -o %s/card_rhalphabet_muonCR_floatZ_r%ip%i.root"%(sigDir1, options.NR1, options.NP1, sigDir1, options.NR1, options.NP1))
        #exec_me("text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' %s/card_rhalphabet_muonCR_r%ip%i.txt -o %s/card_rhalphabet_muonCR_floatZ_r%ip%i.root"%(sigDir2, options.NR2, options.NP2, sigDir2, options.NR2, options.NP2))
    else:
        if options.box=='CA15':
            exec_me('combineCards.py cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt > %s/card_rhalphabet_r%ip%i_%s_%s.txt'%(sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,options.NR1, options.NP1, options.box, cut),options.dryRun)
            exec_me('combineCards.py cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt > %s/card_rhalphabet_r%ip%i_%s_%s.txt'%(sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,options.NR2, options.NP2, options.box, cut),options.dryRun)
        else:
            exec_me('combineCards.py cat1=%s/card_rhalphabet_cat1.txt cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt > %s/card_rhalphabet_r%ip%i_%s_%s.txt'%(sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,options.NR1, options.NP1, options.box, cut),options.dryRun)
            exec_me('combineCards.py cat1=%s/card_rhalphabet_cat1.txt cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt > %s/card_rhalphabet_r%ip%i_%s_%s.txt'%(sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,sigDir2,options.NR2, options.NP2, options.box, cut),options.dryRun)
        #exec_me("text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' %s/card_rhalphabet_r%ip%i.txt -o %s/card_rhalphabet_r%ip%i.txt"%(sigDir1, options.NR1, options.NP1, sigDir1, options.NR1, options.NP1))
        #exec_me("text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' %s/card_rhalphabet_r%ip%i.txt -o %s/card_rhalphabet_r%ip%i.txt"%(sigDir2, options.NR2, options.NP2, sigDir2, options.NR2, options.NP2))

    p1 = int((options.NR1+1)*(options.NP1+1)) # free paramaters
    p2 = int((options.NR2+1)*(options.NP2+1)) # free parameters
    

    dataString = ''
    if not options.pseudo:
        dataString = '--data'

    if options.pseudo:
        exec_me('python limit.py -M FTest --datacard %s/card_rhalphabet_r%ip%i_%s_%s.txt --datacard-alt %s/card_rhalphabet_r%ip%i_%s_%s.txt -o %s -n %i --p1 %i --p2 %i -t %i --lumi %f %s -r %s --freezeNuisances tqqeffSF,tqqnormSF --mass %s --seed %s'%(sigDir1, options.NR1, options.NP1, options.box, cut, sigDir2, options.NR2, options.NP2, options.box, cut, ftestDir, options.n, p1, p2, options.toys, options.lumi, dataString, options.r, options.mass,options.seed),options.dryRun)
    else:
        exec_me('python limit.py -M FTest --datacard %s/card_rhalphabet_muonCR_r%ip%i_%s_%s.txt --datacard-alt %s/card_rhalphabet_muonCR_r%ip%i_%s_%s.txt -o %s -n %i --p1 %i --p2 %i -t %i --lumi %f %s -r %s --mass %s --seed %s'%(sigDir1, options.NR1, options.NP1, options.box, cut, sigDir2, options.NR2, options.NP2, options.box, cut, ftestDir_muonCR, options.n, p1, p2, options.toys, options.lumi, dataString, options.r, options.mass,options.seed),options.dryRun)
     

     
