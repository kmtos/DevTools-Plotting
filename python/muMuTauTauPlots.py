import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from DevTools.Plotter.haaUtils import *
from copy import deepcopy
import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

blind = True
doDetRegions = False
doSignals = True
doMC = True
do2D = True

plotter = Plotter('MuMuTauTau')

#########################
### Define categories ###
#########################

sigMap = getSampleMap()

#samples = ['QCD','W','Z','TT','WW','WZ','ZZ']
#samples = ['JPsi','Upsilon','W','Z','TT','WW','WZ','ZZ']
#samples = ['JPsi','W','Z','TT','WW','WZ','ZZ']
#samples = ['W','Z','TT','WW','WZ','ZZ']
samples = ['TT','W','Z']

sigMap['BG'] = []
for s in samples:
    sigMap['BG'] += sigMap[s]

signals = ['HToAAH125A15']

signame = 'HToAAH{h}A{a}'

hmasses = [125,300,750]
amasses = [5,7,9,11,13,15,17,19,21]
amasses = [5,9,13,17,21]

hColors = {
    125: ROOT.TColor.GetColor('#000000'),
    300: ROOT.TColor.GetColor('#B20000'),
    750: ROOT.TColor.GetColor('#FFCCCC'),
}

aColors = {
    5 : ROOT.TColor.GetColor('#000000'),
    7 : ROOT.TColor.GetColor('#330000'),
    9 : ROOT.TColor.GetColor('#660000'),
    11: ROOT.TColor.GetColor('#800000'),
    13: ROOT.TColor.GetColor('#B20000'),
    15: ROOT.TColor.GetColor('#FF0000'),
    17: ROOT.TColor.GetColor('#FF6666'),
    19: ROOT.TColor.GetColor('#FF9999'),
    21: ROOT.TColor.GetColor('#FFCCCC'),
}


sels = ['default','regionA','regionB','regionC','regionD']

for sel in ['default','regionA','regionB','regionC','regionD']:
    sels += ['{0}/{1}'.format(sel,'dr0p8')]
    #sels += ['{0}/{1}'.format(sel,'bveto')]
    #sels += ['{0}/{1}'.format(sel,'taubveto')]
    #sels += ['{0}/{1}'.format(sel,'bothbveto')]
    #sels += ['{0}/{1}'.format(sel,det) for det in ['BB','BE','EE']]

########################
### plot definitions ###
########################
plots = {
    # h
    'hMass'                 : {'xaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,1000,10), 'logy': False, 'overflow': True},
    'hMassKinFit'           : {'xaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,1000,10), 'logy': False, 'overflow': True},
    'hMt'                   : {'xaxis': 'm_{T}^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': False, 'overflow': True},
    'hMcat'                 : {'xaxis': 'm_{CA}^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': True, 'overflow': True},
    'hDeltaMass'            : {'xaxis': 'm^{#mu#mu}-m^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,10), 'logy': True, 'overflow': True},
    'hDeltaMt'              : {'xaxis': 'm^{#mu#mu}-m_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,10), 'logy': True, 'overflow': True},
    # amm
    'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.5, range(0,60,1)), 'logy': False, 'overflow': True},
    'ammDeltaR'             : {'xaxis': '#Delta R(#mu#mu) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.05, range(0,30,1)), 'logy': False, 'overflow': True},
    'ammDeltaPhi'           : {'xaxis': '#Delta #phi(#mu#mu) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    'am1Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{1} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(25,150,5), 'logy': False, 'overflow': True},
    'am1GenPtRatio'         : {'xaxis': '#mu_{1} p_{T}^{gen}/p_{T}^{reco}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(50,150,1)), 'logy': False, 'overflow': True},
    'am2Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{2} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'am2GenPtRatio'         : {'xaxis': '#mu_{2} p_{T}^{gen}/p_{T}^{reco}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(50,150,1)), 'logy': False, 'overflow': True},
    # att
    'attMass'               : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,60,1), 'logy': False, 'overflow': True},
    'attMassKinFit'         : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,60,1), 'logy': False, 'overflow': True},
    'attMt'                 : {'xaxis': 'm_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 2 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,120,2), 'logy': False, 'overflow': True},
    'attMcat'               : {'xaxis': 'm_{CA}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 2 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,120,2), 'logy': True, 'overflow': True},
    'attDeltaR'             : {'xaxis': '#Delta R(#tau_{#mu}#tau_{h}) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.1, range(0,30,1)), 'logy': False, 'overflow': True},
    'attDeltaPhi'           : {'xaxis': '#Delta #phi(#tau_{#mu}#tau_{h}) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': False, 'overflow': False},
    'atmPt'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{#mu} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'atmDxy'                : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{#mu} d_{xy} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    'atmDz'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{#mu} d_{z} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    'atmGenPtRatio'         : {'xaxis': '#tau_{#mu} p_{T}^{gen}/p_{T}^{reco}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(50,150,1)), 'logy': False, 'overflow': True},
    'athPt'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(10,150,5), 'logy': False, 'overflow': True},
    'athDxy'                : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} d_{xy} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    'athDz'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} d_{z} (cm)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'logy': True},
    'athGenPtRatio'         : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen}', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    'athGenPtRatioDM0'      : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen} (DM 0)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    'athGenPtRatioDM1'      : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen} (DM 1)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    'athGenPtRatioDM10'     : {'xaxis': '#tau_{h} p_{T}^{reco}/p_{T}^{gen} (DM 10)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(0,250,5)), 'logy': False, 'overflow': True},
    'athJetCSV'             : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} CSVv2 (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': 10, 'logy': True, 'overflow': True},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,320,20), 'numcol': 2, 'logy': False, 'overflow': True},
    'nBJetsT'               : {'xaxis': 'Number of b-tagged jets (p_{T} > 20 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5], 'overflow': True, 'binlabels': ['0','1','2','#geq3'], 'logy': True,},
    'nBJetsM'               : {'xaxis': 'Number of b-tagged jets (p_{T} > 20 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5], 'overflow': True, 'binlabels': ['0','1','2','#geq3'], 'logy': True,},
    'nBJetsL'               : {'xaxis': 'Number of b-tagged jets (p_{T} > 20 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5], 'overflow': True, 'binlabels': ['0','1','2','#geq3'], 'logy': True,},
}

plots2D = {
    'ammMass_vs_attMass'          : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)',},
    'ammMass_vs_attMassKinFit'    : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#tau_{#mu}#tau_{h}} Kin. Fit (GeV)',},
    'ammMass_vs_hMass'            : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'rangey': [0,250],},
    'ammMass_vs_hMassKinFit'      : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'rangey': [0,250],},
    'attMass_vs_hMass'            : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'rangey': [0,250],},
    'attMassKinFit_vs_hMassKinFit': {'xaxis': 'm^{#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} Kin. Fit (GeV)', 'rangey': [0,250],},
    'ammMass_vs_ammDeltaR'        : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': '#Delta R(#mu#mu) (GeV)', 'rangey': [0,3],},
    'attMass_vs_attDeltaR'        : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': '#Delta R(#tau_{#mu}#tau_{h}) (GeV)', 'rangey': [0,3],},
    'attMcat_vs_attDeltaR'        : {'xaxis': 'm_{CA}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': '#Delta R(#tau_{#mu}#tau_{h}) (GeV)', 'rangey': [0,6],},
}

special = {
    'jpsi': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 10 MeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(290,400,1)), 'logy': False, 'overflow': False},
    },
    'upsilon': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 50 MeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(850,1150,5)), 'logy': False, 'overflow': False},
    },
}

############################
### MC based BG estimate ###
############################
if doMC:
    for sel in sels:
        plotter.clearHistograms()

        for s in samples:
            plotter.addHistogramToStack(s,sigMap[s])
        
        for signal in signals:
            plotter.addHistogram(signal,sigMap[signal],signal=True)
        
        if not blind or 'regionD' in sel: plotter.addHistogram('data',sigMap['data'])
        
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotname = '{0}/{1}'.format(sel,plot)
            savename = '{0}/mc/{1}'.format(sel,plot)
            plotter.plot(plotname,savename,**kwargs)
        
        if blind and 'regionD' not in sel: plotter.addHistogram('data',sigMap['data'])
        
        for s in special:
            for plot in special[s]:
                kwargs = deepcopy(special[s][plot])
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/mc/{1}_{2}'.format(sel,plot,s)
                plotter.plot(plotname,savename,**kwargs)

#########################
### Signals on 1 plot ###
#########################

if doSignals:
    for h in hmasses:
        plotter.clearHistograms()
    
        for a in amasses:
            name = signame.format(h=h,a=a)
            plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': aColors[a]})
    
        for plot in plots:
            for sel in sels:
                kwargs = deepcopy(plots[plot])
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/h{h}/{1}'.format(sel,plot,h=h)
                plotter.plot(plotname,savename,plotratio=False,**kwargs)
        
    
    for a in [5,19]:
        plotter.clearHistograms()
        
        for h in hmasses:
            name = signame.format(h=h,a=a)
            plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': hColors[h]})
    
        for plot in plots:
            for sel in sels:
                kwargs = deepcopy(plots[plot])
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/a{a}/{1}'.format(sel,plot,a=a)
                plotter.plot(plotname,savename,plotratio=False,**kwargs)
    
################
### 2D plots ###
################
if do2D:
    for sample in samples+signals+['data']:
        plotter.clearHistograms()
        plotter.addHistogram(sample,sigMap[sample])
        
        for plot in plots2D:
            for sel in sels:
                if sample=='data' and blind and 'regionD' not in sel: continue
                kwargs = deepcopy(plots2D[plot])
                if sample not in signals:
                    kwargs['rebinx'] = 10
                    kwargs['rebiny'] = 10
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/2D/{1}/{2}'.format(sel,sample,plot)
                plotter.plot2D(plotname,savename,**kwargs)

