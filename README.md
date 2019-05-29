# Alaska

This repository contains replication code, data, and additional material to accompany the paper <a href="https://mggg.org/Alaska">Mathematics of Nested Districts: The Case of Alaska</a> which grew out of a project started by the 2018 <a href="http://gerrydata.org/">Voting Rights Data Institute</a> organized by <a href="mggg.org">MGGG</a>. 

<H2> Pairing Districts</H2>

This paper analyzes a pairing rule that eight states require of their state legislative districting plans - Senate districts must be formed by joining adjacent pairs of House districts. From a mathematical perspective, this is a question of constructing perfect matchings on the <b>Dual Graph</b> of the House districts. We focus mainly on the state of Alaska where it is possible to generate the full set of matchings and evaluate the expected partisan behavior of the associated Senate plans. To get a sense of the scale of this problem, the table below shows the number of districts and perfect matchings for each of the relevant states. 


<table>
 <tr><td>State</td><td># House Districts</td><td># Dual Graph Edges</td><td># Perfect Matchings</td></tr>
 <tr><td>Alaska</td><td>40</td><td>100</td><td>108,765</td></tr>
 <tr><td>Illinois</td><td>118</td><td>326</td><td>9,380,573,911</td></tr>
 <tr><td>Iowa</td><td>100</td><td>251</td><td>1,494,354,140,511</td></tr>
 <tr><td>Minnesota</td><td>134</td><td>260</td><td>6,156,723,718,225,577,984</td></tr>
 <tr><td>Montana</td><td>100</td><td>269</td><td>11,629,786,967,358</td></tr>
 <tr><td>Nevada</td><td>42</td><td>111</td><td>313,698</td></tr>
 <tr><td>Oregon</td><td>60</td><td>158</td><td>229,968,613</td></tr>
 <tr><td>Wyoming</td><td>60</td><td>143</td><td>920,864</td></tr>
</table>

Our techincal contributions include an implementation of the FKT algorithm for counting the number of perfect matchings in a planar graph, a prune-and-split algorithm for generating the matchings, and a uniform sampling implementation for analyzing states like Minnesota, where generating the full set of matchings would be prohibitively expensive. The FKT function is fast enough to incorporate at every step of the Markov chain sampling procedure for generating new House plans and forms the backbone of the uniform sampling algorithm. These techniques also allow us to investigate the relationship between the number of edges in the dual graph and the number of matchings, which is of independent mathematical interest. 

For Alaska, we show that compared to the full collection of possible matchings of the currently enacted plan the chosen pairing exhibits an approximate advantage of 1 Republican seat. Interestingly, the House districting plan appears to have a similar magnitude advantage for the Democratic party compared to a neutral ensemble formed with a Markov chain. Histograms of these results are shown below. We also verify the usefulness of our sampling techinque by comparing it to the ground truth available in Alaska and examine the extremal plans found in the Markov chain ensemble.  Finally, we provide a cleaned dataset of merged geographic and partisan data and describe the choices that must be made to compile these resources. 

<table>
 <tr><td># Democratic Senate Seats across all perfect matchings</td><td># Democratic House Seats across 100k alternative plans</td></tr>
 <tr><td> <img src="https://raw.githubusercontent.com/gerrymandr/Alaska/master/GerryChain/Match_Hist_PermissiveUSH18A.png" width="500"/></td><td>  <img src="https://raw.githubusercontent.com/gerrymandr/Alaska/master/GerryChain/New_Ensemble_Hist_USH18A.png" width="500"/> </td></tr>
 </table>


<H2> Replication </H2>

To reproduce the experiments in the paper begin by cloning this repository or clicking the Download ZIP option. After you have extracted the files you will need to unzip AK_precicnts_NS.zip which is in the data directory. Navigate your terminal to the main directory and enter: python matching_verification. py

The replication code does the following:
<ol>
 <li>   Begins by constructing the three dual graphs on house districts: tight, restrictive, and permissive by starting fresh from the shapefile, adding the island edges, and then deleting the water connections around Anchorage.</li>
<li>    It next checks that the edges nest i.e. that tight <= restricted <= permissive. </li>
 <li>   Once it confirms that everything is OK, the adjacency matrices are written to Outputs.</li>
 <li>   Then it uses FKT to enumerate the matchings for each graph and returns the number and the running time</li>
   <li>   Next it generates all of the matchings for each graph and returns the running time</li>
  <li>    The full sets of matchings are written to file to save for later</li>
  <li>    Next it checks that for each of the sets of matchings, the indices correctly correspond to pairs of adjacent districts by checking that there are cut edges in the partition that correspond to each pair.</li>
 <li>     For each of the three graphs it loads each matching and computes the partisan balance for the elections</li>
 <li>     These values are  also written to Outputs</li>
 <li>     Then it generates the box plots and histograms for seats and competitive districts, just like the ones in the paper. These are saved in Outputs/plots</li>
 <li>     It also writes separate text files with the averages compared to the enacted plan values, like the tables in the paper. These are saved in Outputs/values</li>
 <li>     It takes about 12 minutes to get to this point - having generated and analyzed all of the matchings of the enacted plan corresponding to the three graphs.</li>
  <li>    Next, for each of the graphs it runs 100,000 ReCom steps starting at the enacted plan.</li>
  <li>    At every step, it records the partisan values as well as the number of edges in the house dual graph and FKT # of matchings.</li>
  <li>    After it finishes each run, it generates the same box plots, histograms, and text files as the matchings version as well as the plot of edges vs. matchings.</li>
 <li>     Finally, the outputs are written to file and the final time is reported.</li>
 <li>     For these 100k steps runs it takes about 3 hours to do everything (shortens to 1/2 an hour if you only do 10k steps). </li>
   
  </ol>
  
  
 
<H2> Subdirectories </H2>

<ul>
  <li> <b>GerryChain</b> contains sample code for building ensembles that we used while doing the exploratory analysis. </li>
  <li><b>Limited Adjacency </b> contains a version of the shapefile that is clipped to the land area of the state. </li>
  <li><b>Outputs</b> contains a zipped folder with the actual outputs analyzed in the paper as well as providing the directory structure to be populated for replication. </li>
  <li><b>Preprocessing</b> contains code for downloading the state level shapefiles and extracting the corresponding dual graphs as .csvs. </li>
  <li> <b> Summer Code</b> contains more exploratory code an earlier versions of the main functions. </li>
  <li> <b>data</b> contains the adjacency matrices for the dual graphs and .json files for the complete matchings of the Permissive and Restricted plans. The main precinct level shapefile for Alaska is included as AK_precicnts_NS.zip. </li>
 <li><b>shapefiles</b> contains the state level shapefiles. </li>
 <li><b>Tests</b> contains testing examples for the various python functions and plotting code for nearly planar embeddings like those in the paper.</li>
  
  </ul>
  
  
  <H2>Python Functions</H2>
  <ul>
 <li><b>FKT.py</b> provides a function named FKT that enumerates all of the perfect matchings in a given planar graph. It takes as input a numpy matrix representing the adjacencies. This can be extracted from a networkx graph object as nx.adjacency_matrix(G).todense() and the program can be called with round(FKT(nx.adjacency_matrix(G).todense())) </li>
 <li><b>enum_matchings.py</b> provides a function names enumerate_matchings that generates a list off all of the perfect matchings of a planar graph. It takes an input a numpy array of the graph adjacencies and can be called with enumerate_matchigs(np.array(FKT(nx.adjacency_matrix(G).tolist(),list(range(len(G.nodes())))). </li>
 <li><b>uniform_matching.py</b> provides a function uniform matching that takes as input a networkx graph object and returns a uniformly sampled perfect matching. </li>
 <li> The remainder of the python files perform tests and plotting features. </li>

<!--
enum_matchings.py - Most recently updated enum_mathcing file that takes in multiple adjacency matrices of a potential districting plans from chain and outputs the number of matchings in each plan. Creates .pkl file. 

enum_matchings_original.py - Orignal code from Samir. 

04_check_matchings.py- Code for checking matchings from Samir. NOTE: Written in Python 2 

-->
