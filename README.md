# Maping the Tool Communities of The Setup

This repository contains the code used to generate [this interactive visualization](http://labs.drewconway.com/thesetup/) of the tool communities that emerge from [The Setup](http://usesthis.com).

For a more detail on the methodology used to generate this visualization, see my [blog post on the project](http://drewconway.com/zia/).

## How it works

There are three primary steps in creating this visualization:

 1. Generate the data
 2. Analyze the relationships to specify a map
 3. Visualize the map

All of the Python files contain here are use for steps 1-2, and the HTML, Javascript and CSS contained in the `html` directory generate the visualization/

### Generating the data

The `data_pull.py` file scraps http://usesthis.com to generate a JSON file called `use_this.json`.  This file is a structured representation of the data contained in each interview on the website.

### Analyzing the data