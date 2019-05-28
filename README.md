# Alaska

This repository contains replication code, data, and additional material to accompany the paper <a href="https://mggg.org/Alaska">Mathematics of Nested Districts: The Case of Alaska</a>. 


<H2> Subdirectories </H2>

<ul>
  <li> <b>GerryChain</b> contains sample code for building ensembles that we used while doing the exploratory analysis. </li>
  <li><b>Limited Adjacency </b> contains a version of the shapefile that is clipped to the land area of the state. </li>
  <li><b>Outputs</b> contains a zipped folder with the actual outputs analyzed in the paper as well as providing the directory structure to be populated for replication. </li>
  <li><b>Preprocessing</b> contains code for downloading the state level shapefiles and extracting the corresponding dual graphs as .csvs. </li>
  <li> <b> Summer Code</b> contains more exploratory code an earlier versions of the main functions. </li>
  <li> <b>data</b> contains the adjacency matrices for the dual graphs and .json files for the complete matchings of the Permissive and Restricted plans. The main precinct level shapefile for Alaska is included as AK_precicnts_NS.zip. </li>
  <li><b>shapefiles</b> contains the state level shapefiles. 
  
  </ul>

<!--
enum_matchings.py - Most recently updated enum_mathcing file that takes in multiple adjacency matrices of a potential districting plans from chain and outputs the number of matchings in each plan. Creates .pkl file. 

enum_matchings_original.py - Orignal code from Samir. 

04_check_matchings.py- Code for checking matchings from Samir. NOTE: Written in Python 2 

-->
