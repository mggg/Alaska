#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 09:26:35 2019

@author: ddeford
"""

import json
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

with open('./Outputs/Extreme_Matchings_MaxE_stats.json') as json_file:  
    datamax = json.load(json_file)
    
with open('./Outputs/Extreme_Matchings_MinE_stats.json') as json_file:  
    datamin = json.load(json_file)    
 

with open('./Outputs/Extreme_Matchings_MinM_stats.json') as json_file:  
    dataminM = json.load(json_file)    
    
with open("./Outputs/Matchings_Permissive_stats.json") as json_file:  
    dataenact = json.load(json_file)    
    
plt.figure()

sns.distplot(datamax['2'],kde=False,color='slateblue',bins=[x for x in range(4,13)], hist_kws={"rwidth":1,"align":"left"})#,norm_hist=True)
plt.axvline(x=np.mean(datamax['2']),label="Matchings Mean",color='green',linewidth=5)
plt.axvline(x=7,label="Current Plan",color='red',linewidth=5)

plt.legend()

plt.show()
plt.figure()

sns.distplot(datamin['2'],kde=False,color='slateblue',bins=[x for x in range(4,13)], hist_kws={"rwidth":1,"align":"left"})#,norm_hist=True)
plt.axvline(x=np.mean(datamin['2']),label="Matchings Mean",color='green',linewidth=5)
plt.axvline(x=7,label="Current Plan",color='red',linewidth=5)

plt.legend()

plt.show()
plt.figure()

sns.distplot(dataminM['2'],kde=False,color='slateblue',bins=[x for x in range(4,13)], hist_kws={"rwidth":1,"align":"left"})#,norm_hist=True)
plt.axvline(x=np.mean(dataminM['2']),label="Matchings Mean",color='green',linewidth=5)
plt.axvline(x=7,label="Current Plan",color='red',linewidth=5)

plt.legend()

plt.show()

plt.figure()

sns.distplot(dataenact['2'],kde=False,color='slateblue',bins=[x for x in range(4,13)], hist_kws={"rwidth":1,"align":"left"})#,norm_hist=True)
plt.axvline(x=np.mean(dataenact['2']),label="Matchings Mean",color='green',linewidth=5)
plt.axvline(x=7,label="Current Plan",color='red',linewidth=5)

plt.legend()

plt.show()




