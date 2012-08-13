# Mapping the Tool Communities of The Setup

This repository contains the code used to generate [this interactive visualization](http://labs.drewconway.com/thesetup/) of the tool communities that emerge from [The Setup](http://usesthis.com).  This project attempts to utilize the meta-data contained in each post from The Setup to project the relationship of tools onto a two-dimensional map with community clusters based tool use.  

Below is a explanation of the methodology I used to create this visualization and how the code works.

## Methodology

The Setup is one of my favorite websites.  I love learning what hardware and software smart people use to get stuff done.  I had often wondered how all of these tools related to each other based on who was using them.  One day I noticed that (for the most part) all of the entries are actually fairly well structured.  When an interviewee mentions a tool he or she uses, that tool is linked too.  Also, tools are fairly well organized under the Hardware and Software headings.

![Example text from The Setup](https://raw.github.com/drewconway/thesetup/master/readme_files/usesthis_example.png)

It occurred to me that this meta-data could be used the generate structure among the tools vis a vis the people who use them.  As is often the case, this structure can be conceptualized as a [bipartite graph](http://en.wikipedia.org/wiki/Bipartite_graph), where the node types are people (interviewees) and tools (what they use).  Thus, the structure among tools is based on their affiliation with people.  That is, tools are related through the people that use them.  This is a very convenient way to conceptualize all kinds of data, [particularly on the web](http://www.drewconway.com/zia/?p=2490).

### Generating the data

The best part is once there is structure, we can analyze the resulting graph to map the communities.  To do this, I first scraped http://usesthis.com to create a structured representation of each interview.  The `data_pull.py` file scrapes http://usesthis.com to generate a JSON file called `use_this.json`.  It looks in each interview post for the Hardware and Software headings, and then pulls out the links under each.

This result is a file with a structured representation of the data contained in each interview on the website.  Each entry is now represented as the following:

    {
    "hardware": [
     "macbook pro", 
     "ubuntu"
    ], 
    "date": "2011-09-30", 
    "person": "Drew Conway", 
    "url": "http://drew.conway.usesthis.com/", 
    "portrait": "http://usesthis.com/images/portraits/drew.conway.jpg", 
    "tags": [
     "data", 
     "linux", 
     "mac", 
     "politics", 
     "scientist"
    ], 
    "software": [
     "sparrow", 
     "chrome", 
     "echofon", 
     "textmate", 
     "emacs", 
     "marsedit", 
     "python", 
     "r", 
     "ipython", 
     "rstudio", 
     "latex", 
     "openoffice"
    ]
    },
   
In the final result, only a small amount of this data is actually used to generate the visualization.  But, I find it much better to collect more data than you think you'll need, especially when sharing the results and code!  From this JSON object we will use the `person` key, and the `hardware` and `software` keys to create a bipartite graph from edges formed among people and tools.

### Analyzing the data

Next, we must analyze this graph to project those relationships onto a map.  To do this we use the `tools_graph.py` file.  Our first step is to project this bipartite graph into a single mode, wherein tools are directly connected to each other.  A useful outcome of this projection is that the resulting edges can be weighted by the frequency of co-use between two tools in the full data set.  That is, if tools X and Y were mentioned in 10 different interviews, then their edge in our graph would have a weight of 10.

As if often the case in analyses such as this, the resulting graph projection generates multiple components, i.e., our graph has several small graphs contained in it.  For the purposes of this project I wanted to focus on the core tools from the data, so I extracted the largest component, removed any edges with a weight less than 2, and then removed the nodes orphaned by this edge pruning.

The resulting graph is a single strongly connected component.  For the visualization, I wanted to convey both the similarity of tools by defining communities, but also the overall popularity of tools found in the data. For the latter, a straightforward measure of popularity would be the centrality of nodes in the network.  Also, because we have weighted edges, we can use that information to further refine our measures of popularity.  I compute both Eigenvector and betweenness centralities for all nodes, and add that data to our graph. This data will be used in the visualization to convey popularity.

Our final step in the analysis is to project the nodes onto a map.  Because we have represented the data as a network, one obvious method might be to use some [force-directed network visualization](http://en.wikipedia.org/wiki/Force-based_algorithms_(graph_drawing)) to display communities.  Our network, however, is extremely dense, and is so by-design. In this case, the forced-directed methods are less useful because the resulting visualization will likely look like a big clump of hair.  

Instead, I decided to use the weighted geodesic distance among all nodes as a measure of dissimilarity among the tools.  The logic here is that the further apart tools are on the graph, the less similar they are in terms of who is using them.  This may make more sense if considered directly within the context of The Setup.  One could imagine that a graphic designer uses one set of tools (Photoshop and a nice big monitor), while a data hacker uses a different set (Sublime Text 2 and a cheap Linux laptop).  At the same time, there may also be some universal tools that they both use (Dropbox and GMail).  We want to pick both of these kinds of relationships, and a distance measure is one way of doing that.

Once these distances are measured, we can store them in a tool-by-tool matrix, where each entry is the weighted geodesic distance between each tool.  With this matrix with can use any number of dimensionality reduction (or as the fancy machine learning people call it, "[manifold learning](http://scikit-learn.org/dev/modules/generated/sklearn.manifold.MDS.html)") methods to generate our map projection.  In this case, I decided to use a traditional scaling method called [multidimensional scaling](http://en.wikipedia.org/wiki/Multidimensional_scaling), to take our tool-dimensional matrix and project those relationships into two-dimensions.  There are of course many other methods that could have been used, and I choose this one more because of familiarity than precision.

The final step is to generate the community clusters for each node.  As I said, I wanted to convey these clusters visually, and in this case I wanted to be able to show how they changed as the cluster granularity increased.  To do this, I decided to use a [hierarchical clustering method](http://scikit-learn.org/stable/modules/generated/sklearn.cluster.Ward.html) on the distance matrix to define the communities.  

Once the network has been fully analyzed, all of data required to make the visualization is now contained in the `html/tools_graph.json` file.  Each node's data is now represented as the following:

    {
    "node": "final cut", 
    "betweenness": 0.0, 
    "cluster_map": {
     "0": 0, 
     "1": 0, 
     "2": 1, 
     "3": 1, 
     "4": 1, 
     "5": 0, 
     "6": 0, 
     "7": 2, 
     "8": 0, 
     "9": 1, 
     "10": 0, 
     "11": 10,
     ...
      }, 
    "Y": -1.7882205048619737, 
    "X": -1.007840145266849, 
    "type": "software", 
    "class": 1, 
    "eigenvector": 0.0011864175623134546
    },

I should mention that this version of the analysis is one very specific methodology.  There are many other ways the map could have been generated, and I hope someone will clone this repository and attempt a different one!

### Building the map visualization

The entire visualization is built using [d3.js](http://d3js.org/), and all of its functionality is contained in the `html/usethis.js` file.  There is a lot going on in the Javascript, and since I am a particularly bad Javascript programmer and web designer I do not recommend using a resource on either. That said, I had three primary goals with the visualization:

 1. Allow the user to observer the map at both an aggregate and detailed scale
 2. Allow the user to step through the community clusters
 3. Provide the option to understand distance among nodes using fixed guides
 
To accomplish the first goal I utilized d3's fantastic zooming functionality.  In this case, in aggregate the map appears to be a high-level set of communities.  I use the Eigenvector centrality measure to define the size of each node. So, at this high-level you can easily see the most popular tools. Then, as the user zooms, details are revealed to show what tools are in each community.  For the second goal, I created a slider-bar, and some keyboard interaction to step through the community clusters.  It is definitely sub-optimal, but it does allow the user to alter the current number of communities, and see how they split and group at different levels of granularity.  Finally, I provided the option for the user to toggle on and off a set of concentric ellipses by pressing the "M" key.  I think this provide a sense of distance and scale among the nodes.

I hope this has been useful, and you'll consider hacking the code to create your own version!

## License

Created by Drew Conway (drew.conway@nyu.edu) on 2012-08-13

Copyright (c) 2012, under the Simplified BSD License.
For more information on FreeBSD see: http://www.opensource.org/licenses/bsd-license.php All rights reserved.