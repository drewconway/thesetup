import json
import itertools
import networkx as nx
from sklearn import manifold
from sklearn.cluster import Ward
from numpy import zeros

def build_graph(data):
	"""
	Builds a  person x column bipartite graph of tool use, where 'column' can be
	either 'software' or 'hardware'

	Returns as NetworkX DiGraph 
	"""
	G = nx.DiGraph()
	for x in data:
		hardware = x['hardware']
		software = x['software']
		person = x['person']
		G.add_node(person, {'type': 'person', 'class':0})
		G.add_nodes_from(zip(hardware, itertools.repeat({'type' : 'hardware', 'class' : 1})))
		G.add_nodes_from(zip(software, itertools.repeat({'type' : 'software', 'class' : 1})))
		rel = zip(itertools.repeat(person), hardware + software)
		G.add_edges_from(rel)
	return G

def build_projection(G, node_class):
	"""
	Returns the bipartite projection of graph G onto some node_type,
	where edge weights is equal to the number of shared connections
	between nodes of a the given type.
	"""
	nodes = [a for (a,b) in G.nodes(data=True) if b['class'] == node_class]
	M = nx.bipartite.projection.weighted_projected_graph(nx.Graph(G), nodes)
	return M

def multiple_measures(G):
	"""
	"""
	# First we add centrality measures to the nodes

	# In both cases, we have to be careful to invert the weights because in this 
	# context the weight refers to a strength of relationship -- not distance or cost.
	# Next we add distance measures to the edges.  

	weighted_betweeness = nx.betweenness_centrality(G, weight=lambda x: 1./x["weight"])
	eigenvector_centrality = nx.eigenvector_centrality(G)

	for i in G.nodes():
		G.add_node(i, {'betweenness': weighted_betweeness[i], 'eigenvector' : eigenvector_centrality[i]})
	return G
		
	
def compute_projection(G):
	"""
	Computes a random principal components scaling of nodes based on some pre-computed 
	distance from one-another.
	"""
	sp = nx.shortest_path_length(G, weight=lambda x: 1./x['weight'])
	# print sp["apache"]
	M = zeros((len(sp), len(sp)))

	for i, v in enumerate(sp.keys()):
		for j, n in enumerate(sp.keys()):
			if i == j:
				M[i,j] = 0
			else:
				try:
					M[i,j] = sp[v][n]
				except KeyError:
					M[i,j] = 0


	proj = manifold.MDS(n_components=2, dissimilarity="precomputed").fit_transform(M)
	# print proj

	# # Add this data to each node as an attribute
	for i, v in enumerate(G.nodes()):
		X, Y = proj[i,].tolist()
		G.add_node(v, {"X" : X, "Y" : Y})

	return G, M

def build_clusters(G, dist_matrix):
	cluster_map = dict()
	for v in G.nodes():
		cluster_map[v] = list()

	for i in xrange(G.number_of_nodes()):
		ward = Ward(n_clusters=i).fit(dist_matrix)
		labels = ward.labels_
		for j, v in enumerate(G.nodes()):
			cluster_map[v].append(labels[j])
			
	for v in G.nodes():
		G.add_node(v, cluster_map=dict(zip(range(G.number_of_nodes()), cluster_map[v])))

	return G

if __name__ == '__main__':
	# Load in the use.this data from our JSON file
	data = json.load(open('use_this.json', 'r'))

	# Build a list of tool-to-tool weighted projections from the full graphs, which
	# contains multiple components. We can think of these components as being islands 
	# where the populations are centered around the hardware and sofware they use.
	tool_graph = build_graph(data)
	tool_components = nx.weakly_connected_component_subgraphs(tool_graph)
	tool_projections = map(lambda g: build_projection(g, 1), tool_components)

	# Let's save the raw data, as it may be useful later
	for i, g in enumerate(tool_projections):
		nx.write_gpickle(g, 'tool_projections_'+str(i)+'.p')

	# Extract out only those edges from the largest component with a weight > 1
	# This will reduce the size of the network, and allow us to focus on the most
	# interesting and revealing relationships in the graph.
	main_component = tool_projections[0]
	main_component.remove_edges_from([(a,b,c) for (a,b,c) in main_component.edges(data=True) if c['weight'] <= 1])

	# To clean up, we need to remove the people nodes and orphaned nodes (isolates)
	main_component.remove_nodes_from([(a) for (a,b) in main_component.nodes(data=True) if b == {}])
	main_component.remove_nodes_from(nx.isolates(main_component))
	
	# Now, compute the weighted betweenness and eigenvector centrality of nodes
	# in this main component.  This will be added data that we may use later
	# during the visualization
	main_component = multiple_measures(main_component)

	# Create an adjacency matrix as from the shortest path calculation.
	# This will allow us to do a 2-dimensional scaling of the data
	# for the map projection.
	main_component, dist_matrix = compute_projection(main_component)

	# Create a hierarchical clustering of nodes based on the distance
	# computed in the previous step. This will allow us to create
	# the illusion of zooming in and out of map to see more or less
	# detail of the communities.
	main_component = build_clusters(main_component, dist_matrix)

	# Finally, take all of that great data we just generated, and export it as 
	# a single JSON file
	complete_data = []
	for v, d in main_component.nodes(data=True):
		datum = {'node' : v}
		datum.update(d)
		complete_data.append(datum)

	complete_json = json.dumps(complete_data, indent=1)
	f = 'html/tools_graph.json'
	con = open(f, 'w')
	con.writelines(complete_json)
	con.close()
	

	



