# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 15:26:33 2022

@author: sethd
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

'''
wrote coefs in increasing order, but polyval takes coefs in decreasing order
polynomial takes voltage in mV, returns temp in celsius
type J thermocouple: Iron-Constantan
need to use inverse relationship c

temp error: -.05 to .03 K
lo coefs work for -8.095< V< 0 (mV)
effective T range is 63.2 < T < 273.15 (K)
or -210 < T < 0 (C)

DMM has DC V_err : 0.005%

calibrate polynomial for voltage error as function of voltage, and correct thermocouple
voltages for each temperature calculation

vdiff= vmeas - vcalc
vmeas=v_raw + v_ref
then vmeas - vdiff =-> vcalc
vcalc is the voltage to derive temperatures from

error propogation was roughed out for an initial plot of the voltage discrepancy function
'''
vref=1.1853622516574873
t_room=(73.8-32)*5/9
dt_room=(74-32)*5/9 - t_room
t_nitro=77-273.15
t_ice=0

v_room=-0.0203
v_nitro=-6.315
v_ice=-.9009


def getT(V,co,kelvin=False,ref=False):
    coefs=np.flip(co)
    k=0
    if ref:
        V+=vref
    
    if kelvin:
        k=273.15
    return np.polyval(coefs,V) + k

dtemp=.05 #the expected uncertainty in calculated temperatures according to source on thermocouple

#coefs for 'inverse' polynomial. this gets temperature from voltage
cmlo=[0,1.9528268E+01,-1.2286185E+00, -1.0752178E+00,
      -5.9086933E-01, -1.7256713E-01, -2.8131513E-02,
      -2.3963370E-03, -8.3823321E-05]

#coefs for polynomial that gets voltage from temperature (the 'forward' thermocouple function)
#this one is just used for predicting what measured voltages should be
cmin=[0.000000000000E+00,
 0.503811878150E-01,
 0.304758369300E-04,
-0.856810657200E-07,
 0.132281952950E-09,
-0.170529583370E-12,
 0.209480906970E-15,
-0.125383953360E-18,
 0.156317256970E-22]

vmeas=np.array([v_nitro,v_ice,v_room])+vref
tmeas=np.array([t_nitro,t_ice,t_room])
dtmeas=np.array([2,2,dt_room])
vcalc=getT(tmeas,cmin)
dvcalc=getT(tmeas+dtmeas,cmin) - vcalc
vdiff=vmeas-vcalc
vshift=np.polyfit(tmeas,vdiff,1)# voltage offset as func of temp
vshift2,res,rank,other,other2=np.polyfit(vmeas,vdiff,1,full=True)# voltage offset as func of v_meas

txt=np.array(['$N_2$', '$H_2 O$', 'Room'])
vcor=vmeas-np.polyval(vshift2,vmeas)
'''
print(res)
print(vcor)
print(vcalc)
print(getT(vcor,cmlo,kelvin=True))'''
print(vshift2)

#plot offset
fig,ax=plt.subplots()
ax.errorbar(vmeas,vdiff,yerr=dvcalc,linestyle='none',capsize=5,marker='o',markersize=5,c='k',zorder=3)
ax.plot(vmeas,np.polyval(vshift2,vmeas),c='b',label='{:.3f} V + {:.3f}'.format(vshift2[0],vshift2[1]),zorder=1)
ax.set(xlabel='$V_{meas}$ [mV]',ylabel='$\Delta V$ [mV]',title='Offset: $V_{meas} - V_{calc}$')
ax.legend()

ax.errorbar(tmeas,vdiff,yerr=dvcalc,linestyle='none',capsize=5,marker='o',markersize=5,c='k',zorder=3)
ax.plot(tmeas,np.polyval(vshift,tmeas),c='b',label='{:.3f} T + {:.3f}'.format(vshift[0],vshift[1]),zorder=1)
ax.set(xlabel='$T_{meas}$ [C]',ylabel='$\Delta V$ [mV]',title='Offset: $V_{meas} - V_{calc}$')
for i in range(len(txt)):
    ax.text(tmeas[i]+4,vdiff[i]+.05,txt[i])
ax.legend()
plt.savefig('vshift_plot.png',dpi=300)
