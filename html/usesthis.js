var w = 1024,
	h = 600,
	margin = [80,10,600],
	min_cluster = 3,
	max_cluster = 11,
	current_clusters = 3,
	cluster_levels = d3.range(min_cluster,max_cluster + 1),
	slider_scale = d3.scale.linear().domain([min_cluster, max_cluster]).range([margin[1], w - margin[1]]),
	grid = false,

	chart = d3.select("#chart")
		.append('svg:svg')
		.attr('width', w)
		.attr('height', h)
		.attr('class', 'Spectral')
			.append('g')
			.attr("transform", "translate(" + margin[1] + "," + margin[1] + ")")
			.call(d3.behavior.zoom().scaleExtent([1, 10]).on("zoom", zoom)),

	canvas = chart.append('svg:rect')
			.attr('x', margin[1])
			.attr('y', 0)
			.attr('height', h)
			.attr('width', w - margin[1])
			.style('fill-opacity', '0%');

d3.json("tools_graph.json", function(data) {
	var n = data.length,
		x_vals = data.map(function(x) { return x.X; }),
		y_vals = data.map(function(y) { return y.Y; }),
		x = d3.scale.linear().domain([d3.min(x_vals), d3.max(x_vals)]).range([margin[0], w - margin[0]]),
		y = d3.scale.linear().domain([d3.max(y_vals), d3.min(y_vals)]).range([margin[0], h - margin[0]]),

		grid_rings = chart.selectAll('ellipse')
			.data(d3.range(50,500,50))
		  .enter().append('svg:ellipse')
		  	.attr('class', 'grid')
		  	.attr('cx', w / 2)
		  	.attr('cy', h / 2)
		  	.attr('rx', function(d) { return d; })
		  	.attr('ry', function(d) { return d / 2; }),


		points = chart.selectAll('circle')
			.data(data)
		  .enter().append('svg:circle')
		  	.attr('class', function(d) { return 'q'+d.cluster_map[min_cluster]+"-"+min_cluster; })
		  	.attr('id', function(d, i) { return i; })
		  	.attr('cx', function(d) { return x(d.X); })
		  	.attr('cy', function(d) { return y(d.Y); })
		  	.attr('r', 0)
		  	.style('stroke', 'grey')
		  	.style('fill-opacity', '65%')
		  	.transition()
		  	  	.delay(function(d, i) { return i * (Math.random() * 2); })
		  	  	.duration(200)
		  	.attr('r', function(d) { return 4 + (d.eigenvector * 20); }),

		tool_labels = chart.selectAll('text.tool')
			.data(data)
		  .enter().append('svg:text')
			.attr('class', 'tool')
			.attr('x', function(d) { return x(d.X); })
			.attr('y', function(d) { return y(d.Y); })
			.text(function(d) { return d.node; })
			.on('mousedown', function() { return false; }),


		slider = d3.select("#slider")
		.append('svg:svg')
		.attr('width', w)
		.attr('height', margin[0]),

		slider_line = slider.append('svg:line')
			.attr('class', 'slider')
			.attr('x1', -1)
			.attr('y1', margin[0] / 2)
			.attr('x2', -1)
			.attr('y2', margin[0] / 2)
			.transition()
				.delay(data.length)
				.duration(margin[2])
			.attr('x1', margin[1])
			.attr('y1', margin[0] / 2)
			.attr('x2',  w - margin[1])
			.attr('y2', margin[0] / 2),

		cluster_ticks = slider.selectAll("line.ticks")
		  	.data(cluster_levels)
		  .enter().append('svg:line')
		  	.attr('class', 'ticks')
		  	.attr('x1', -1)
			.attr('y1', (margin[0] / 2) - margin[1])
			.attr('x2', -1)
			.attr('y2', (margin[0] / 2) + margin[1])
		  	.transition()
		  		.delay(data.length)
		  		.duration(margin[2])
		  	.attr('x1', function(d) { return slider_scale(d); })
			.attr('x2', function(d) { return slider_scale(d); }),

		cluster_labels = slider.selectAll("text.slider")
			.data(cluster_levels)
		  .enter().append('svg:text')
		  	.attr('class', 'slider')
		  	.attr('x', -10)
			.attr('y', (margin[0] / 2) + (margin[1]*3))
			.text(function(d) { return d; })
			.on('mousedown', function() { return false; }) 
		  	.transition()
		  		.delay(data.length)
		  		.duration(margin[2])
		  	.attr('x', function(d) { return slider_scale(d); }),

		slider_label = slider.append('text')
			.attr('class', 'label')
			.attr('x', margin[1])
			.attr('y', margin[1] + 5)
			.text('Number of Communities')
			.on('mousedown', function() { return false; })
			.transition()
				.delay(data.length)
				.duration(margin[2])
			.style('fill-opacity', "100%"),

		cluster_selector = slider.selectAll('rect.selector')
			.data(cluster_levels)
		  .enter().append('svg:rect')
		  	.attr('class', 'selector')
		  	.attr('id', function(d) { return d; })
			.attr('height', 20)
			.attr('width', 20)
			.attr('x', function(d) { return slider_scale(d) - 5; })
			.attr('y', (margin[0] / 2) - margin[1])
			.on('dblclick', function(d) {
				current_clusters = d;
				redrawPicker();
				redrawPoints();
			}),

		cluster_picker = slider.append('rect')
			.attr('class', 'picker')
			.attr('height', 20)
			.attr('width', 10)
			.attr('x', margin[1] / 2)
			.attr('y', (margin[0] / 2) - margin[1])
			.transition()
				.delay(data.length)
				.duration(margin[2])
			.style('fill-opacity', "90%")
			.style('stroke-opacity', "90%");

	chart.call(d3.behavior.zoom().x(x).y(y).scaleExtent([1, 8]).on("zoom", zoom));
});

function keyboardAction (e) {
	var key_code = e.keyCode;
	if(key_code == 37 | key_code == 39) {
		changeCluster(key_code);
	}
	// if(key_code == 38 | key_code == 40) {
	// 	applyNoise(key_code);
	// }
	if(key_code == 77) {
		if(grid) {
			grid = false;
		}
		else {
			grid = true;
		}
		toggleGrid();
	}
}

// function applyNoise (key_code) {
// 	d3.json("tools_graph.json", function(data) {
// 		var x_vals = data.map(function(x) { return x.X; }),
// 			y_vals = data.map(function(y) { return y.Y; }),
// 			x = d3.scale.linear().domain([d3.min(x_vals), d3.max(x_vals)]).range([margin[0], w - margin[0]]),
// 			y = d3.scale.linear().domain([d3.max(y_vals), d3.min(y_vals)]).range([margin[0], h - margin[0]]);
// 		// Reset 
// 		if(key_code < 40) {
// 			var points = d3.selectAll('circle')
// 				.data(data)
// 				.attr('cx', function(d) { return x(d.X); })
// 				.attr('cy', function(d) { return y(d.Y); });
// 		}
// 		// Increase jitter
// 		else {
// 			var points = d3.selectAll('circle')
// 				.attr('cx', this.cx + Math.random())
// 				.attr('cy', this.cy + Math.random());	
// 		}
// 	});
// }

function changeCluster (key_code) {
	// Press left key
	if(key_code < 39) {
		if(current_clusters > 3) {
			current_clusters -= 1;
			redrawPoints();
			redrawPicker();
		}
	}
	// Press right key
	else {
		if(current_clusters < 11) {
			current_clusters += 1;
			redrawPoints();
			redrawPicker();
		}
	}
}

function redrawPoints() {
	d3.json("tools_graph.json", function(data) {
		var points = d3.selectAll('circle')
		  .data(data)
		  .attr('class', function(d) { return 'q'+d.cluster_map[current_clusters]+"-"+current_clusters; })
	});
}

function redrawPicker() {
	var cluster_picker = d3.select('rect.picker')
			.transition().duration(500)
		.attr('x', slider_scale(current_clusters) - 5)
		.attr('y', (margin[0] / 2) - margin[1])
}

function zoom() {
	var tool_labels = chart.selectAll('text.tool');
	if(d3.event.scale > 1) {
		tool_labels.style('fill-opacity', d3.event.scale * 10+'%')
	}
	else {
		tool_labels.style('fill-opacity', '0%')
	}
  	chart.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

function toggleGrid() {
	var grid_rings = chart.selectAll('ellipse');
	if(grid) {
		grid_rings.style('stroke-opacity', '25%')
	}
	else {
		grid_rings.style('stroke-opacity', '0%')
	}
}


