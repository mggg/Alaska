# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:40:37 2019

@author: daryl
"""

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

import json
f = open("ak_test_vecs1.json")
d = json.load(f)


votes = np.array(d)

c='hotpink'

plt.boxplot(votes,whis=[1,99],showfliers=False, patch_artist=True,
                boxprops=dict(facecolor="None", color=c),
                capprops=dict(color=c),
                whiskerprops=dict(color=c),
                flierprops=dict(color=c, markeredgecolor=c),
                medianprops=dict(color=c),
                )

plt.plot(range(1,41),votes[0,:],'o',color='red',label='Current Plan')
plt.plot([.5,41],[.5,.5],color='green',label="50%")
plt.xlabel("Indexed Districts")
plt.ylabel("Dem %")
plt.legend()
plt.show()




plt.figure()
sns.distplot(wins,kde=False,color='slateblue',bins=[x for x in range(10,25)],
                                                hist_kws={"rwidth":1,"align":"left"})
plt.axvline(x=wins[0],color='r',label="Current Plan",linewidth=5)
plt.axvline(x=np.mean(wins),color='g',label="Ensemble Mean",linewidth=5)
plt.legend()
plt.show()
    
comp = []

for i in range(len(votes)):
    temp = 0
    for j in votes[i]:
        if .4 < j < .6:
            temp+=1
    comp.append(temp)

sns.distplot(comp,kde=False,color='slateblue',bins=[x for x in range(10,30)],
                                                hist_kws={"rwidth":1,"align":"left"})
plt.axvline(x=comp[0],color='r',label="Current Plan",linewidth=5)
plt.axvline(x=np.mean(comp),color='g',label="Ensemble Mean",linewidth=5)
plt.legend()
plt.show()
    
    
       
