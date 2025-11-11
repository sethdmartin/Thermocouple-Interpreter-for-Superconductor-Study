# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 13:52:41 2022

@author: Seth
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
import pwlf

'''
trial_3: good
trial_4: bad
trial_5: good, but short
trial_6: bad

this script was written to take data from a thermocouple and voltmeter attached to a superconducting sample
the sample was exposed to liquid nitrogen and cooled below its superconducting point

visual examination of plot -> piecewise function fit for junction params
pwlf works well for this, adding more params than needed to ensure that the junction at superconducting t gets included
'''

#these values are from investigation on voltage offset in other script
vshift2=np.array([-0.43284684, 0.44866524])
vref=1.1853622516574873
#these are from isntrument's own uncertainty
dvm=.005
dvc=.003**.5
dv=np.sqrt(dvm**2 + dvc**2)
dte=0.5
dtc=.05

def getT(V,co,kelvin=False):
    coefs=np.flip(co)
    k=0
    
    if kelvin:
        k=273.15
    return np.polyval(coefs,V) + k

#polynomial functions for thermocouple
cmlo=[0,1.9528268E+01,-1.2286185E+00, -1.0752178E+00,
      -5.9086933E-01, -1.7256713E-01, -2.8131513E-02,
      -2.3963370E-03, -8.3823321E-05]

cmin=[0.000000000000E+00,
 0.503811878150E-01,
 0.304758369300E-04,
-0.856810657200E-07,
 0.132281952950E-09,
-0.170529583370E-12,
 0.209480906970E-15,
-0.125383953360E-18,
 0.156317256970E-22]

gtr=[3,5] #usable trials
fits=np.array([])

#plot from loop since arrays are different size
fig,ax=plt.subplots(1,2,figsize=(14,6))

for i in range(2):
    #get temps and resistance vals using trial data, polynomial function and corrections
    trno=gtr[i]
    trial=pd.read_csv('data/trial_{}_good.csv'.format(trno),header=None).transpose()
    inds=trial[0]
    vtherm=trial[1]*1e3
    vmeas=vtherm+vref
    vcorr=vmeas-np.polyval(vshift2,vmeas)
    temps=getT(vcorr,cmlo,kelvin=True)
    res_vals=trial[2]*1e3
    #fit piecewise linear around region where break is visually, middle value of the 3 is threshold temp
    pc_lf = pwlf.PiecewiseLinFit(temps[(temps<110)&(temps>95)], res_vals[(temps<110)&(temps>95)])
    junc = pc_lf.fit(2)[1]
    rc=pc_lf.predict(junc)
    fits=np.append(fits,junc)
    #error for error bars
    vthe=getT(junc-273.15,cmin,kelvin=False)
    vdi=np.random.normal(vthe,dv,size=int(1e5))
    tcc=getT(vdi,cmlo,kelvin=True)
    dtcc=np.std(tcc)
    dt=np.sqrt(dte**2 + dtc**2 + dtcc**2)
    
    #plot
    ax[i].scatter(temps,res_vals,c='k',alpha=0.45,s=5,edgecolor='none')
    ax[i].errorbar(junc,rc,xerr=dt,linestyle='none',capsize=5,marker='o',markersize=8,c='r')
    ax[i].set(xlabel='T [K]',ylabel='R [m$\Omega$]',title='Trial {}, T$_c$ = {} $\pm$ {:.1f} K'.format(trno,round(fits[i],1),dt),xlim=(88,118))
   
plt.savefig('superconductor_trials.png',dpi=300)
    
temp_avg=np.mean(fits)

#error estimation based on instrument uncertainty
vthe=getT(temp_avg-273.15,cmin,kelvin=False)
vdi=np.random.normal(vthe,dv,size=int(1e5))
tcc=getT(vdi,cmlo,kelvin=True)
dtcc=np.std(tcc)
dt=np.sqrt(dte**2 + dtc**2 + dtcc**2)
print('Superconducting Temperature: ',temp_avg, ' +/- ',dt)

