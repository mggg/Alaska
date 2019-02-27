#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 15:04:57 2018

@author: samirkhan
"""

import csv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns



sns.set_style("white")

#Define matching of (1,2), (3,4) which corresponds to actual matching
true_matching = [(str(i), str(i+1)) for i in range(1, 41, 2)]


#Read in csv with vote counts by district, store as dictionary 
def load_data(filename):
    data = {}
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            data[row[0]] = np.array([float(row[1]), float(row[2])])

    return data

#Helper function that takes list of districts and matches in blocks of two
def make_matching(l):
    return [l[i:i+2] for i in range(0, len(l)-1, 2)]


#Function that computes statistics for a matching on data
def evaluate_matching(matching, data):
    
    #initialize voting, seat, and efficiency gap to zero 
    votes = 0
    dem_votes = []
    dem_seats = 0


    eg = 0


    for match in matching:
        #number of dem and rep votes for match 
        m_dem_votes = data[match[0]][0]+data[match[1]][0]
        m_rep_votes = data[match[0]][1]+data[match[1]][1]

        m_votes = m_dem_votes + m_rep_votes

        votes += m_votes

        dem_votes.append(m_dem_votes)

    
        #determines who wins the senate district and update efficiency gap and seats
        if m_dem_votes > m_rep_votes:
            dem_seats +=1
            dem_wasted = m_dem_votes - 0.5*m_votes
            rep_wasted = m_rep_votes

        else:
            dem_wasted = m_dem_votes
            rep_wasted = m_rep_votes - 0.5*m_votes

        eg += dem_wasted - rep_wasted


    return dem_seats, eg/float(votes), np.mean(dem_votes)-np.median(dem_votes)

def check_all_matchings(data):
    #Lists to keep track of seats, efficiency gaps, and mean-median scores
    seats = []
    egs = []
    mms = []

    with open("AKallpairings.csv") as f:
        reader = csv.reader(f)
        for row in tqdm(reader):
            #for each matching, compute and save statistics 
            matching = make_matching(row)
            match_seats, match_eg, match_mm = evaluate_matching(matching, data)

            seats.append(match_seats)
            egs.append(match_eg)
            mms.append(match_mm)


    return seats, egs, mms



def make_hist(filename, name):
    #load in data and run through matchings
    d = load_data(filename)

    true_seats, true_egs, true_mms = evaluate_matching(true_matching, d)
    seats, egs, mms = check_all_matchings(d)


    #plot results
    fig = plt.figure(figsize=(8,10))

    st = fig.suptitle(name, fontsize=14)

    plt.subplot("311")
    plt.hist(seats, bins=len(list(set(seats))))

    plt.gca().axvline(true_seats, c="r")

    plt.xlabel("Seats")
    plt.ylabel("Frequency")

    plt.subplot("312")
    plt.hist(egs, bins=100)

    plt.gca().axvline(true_egs, c="r")

    plt.xlabel("Efficiency Gap")
    plt.ylabel("Frequency")

    plt.subplot("313")
    plt.hist(mms, bins=100)

    plt.gca().axvline(true_mms, c="r")

    plt.xlabel("Mean-Median Score")
    plt.ylabel("Frequency")

    plt.tight_layout()

    st.set_y(0.95)
    fig.subplots_adjust(top=0.9)

    plt.savefig("%s_hist.png" %filename[:-4])

    return seats, egs, mms
