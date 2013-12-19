from lxml import html, etree
from datetime import date
import urllib2
import re
import json
import pickle

# Create functions for extracting article data: meta-tags, hardware, software
def parse_person(url):
	"""
	Requires a valid URL
	Returns a dict with meta-data on the user
	"""
	doc = html.parse(url)

	# Parse time posted
	date_obj = doc.xpath("//p[@class='date']/time[@datetime]")[0]
	page_date = date_obj.values()[0]
	
	# Parse tags
	tags_obj = doc.xpath("//ul[@class='categories']//li/a")
	tags = map(lambda obj: obj.items()[0], tags_obj)
	tags = map(lambda href: href[1].split("/")[2], tags)

	# Portrait link and person's name
	person = doc.xpath("//h3[@class='person']")[0].text
	portait = doc.xpath("//img[@class='portrait']")[0]
	portait_dict = dict(portait.items())
	
	return {'url' : url, 'date' : page_date, 'tags' : tags, 'person' : person, 'portrait' : portait_dict["src"]} 

def get_links(lines):
	"""
	Takes a list of strings with formatted HTML and returns the value of each link.
	Used to extract the tools used by each person in the.
	"""
	tools = []
	for l in lines:
		if(l.find("</a>") > 0):
			try:
				doc = etree.fromstring(l)
				link_obj = doc.xpath("//a")
				links = map(lambda obj: obj.text, link_obj)
				tools.extend(links)
			except etree.XMLSyntaxError:
				pass
	return tools

def parse_tools(url):
	"""
	Requires a parsed HTML doc.
	Returns the a list of the hardware and software used by the person
	"""
	doc = urllib2.urlopen(url)
	lines = doc.readlines()

	# Find the indicies in the list of HTML lines that separate hardware / software sections
	section_regex = re.compile("What hardware do you use?|And what software?|What would be your dream setup?")
	header_inds = [i for i, l in enumerate(lines) if re.search(section_regex, l)]
	hardware_inds =[header_inds[0], header_inds[1]-1]
	software_inds =[header_inds[1], header_inds[2]-1]

	# Extract the tools, and clean out random None types from malformed HTML
	hardware_tools = get_links(lines[hardware_inds[0]:hardware_inds[1]])
	hardware_tools = [(a) for (a) in hardware_tools if a is not None]
	
	software_tools = get_links(lines[software_inds[0]:software_inds[1]])
	software_tools = [(a) for (a) in software_tools if a is not None]
	
	return {'hardware' : map(lambda s: s.lower(), hardware_tools), 'software' : map(lambda s: s.lower(), software_tools)}
	

if __name__ == '__main__':
	# First, pull all of the interview URLs
	# years_back = 4
	# current_year = date.today().year
	# years = xrange(current_year-years_back, current_year)
	base_url = "http://usesthis.com/feed/"

	# Setup XML namespace
	tree = etree.parse(base_url)
	rt = tree.getroot()
	ns = rt.nsmap.values()[0]
	ns_map = {'ns':ns}
	
	# Extract urls
	id_objects = tree.xpath("//ns:feed/ns:entry/ns:id", namespaces=ns_map)
	interview_urls = map(lambda x: x.text, id_objects)
	# for y in years:
	# 	doc = html.parse(base_url+str(y))
	# 	link_objects = doc.xpath("//h2[@class='person']/a[@href]")
	# 	interview_urls.extend(map(lambda obj: obj.values()[0], link_objects))


	# Create a list of dicts with all of the data
	data = []
	for url in interview_urls:
		person = parse_person(url)
		person.update(parse_tools(url))
		data.append(person)

	# Export list of dicts as JSON file
	data_json = json.dumps(data, indent=1)

	f = 'use_this.json'
	con = open(f, "w")
	con.writelines(data_json)
	con.close()

	# Export list of dicts as Pickle
	pickle.dump(data, open("use_this.p", "wb"))


