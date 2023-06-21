import json
from dash import Dash, html
import dash
import dash_cytoscape as cyto
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
app = Dash(__name__)

d = json.load(open("nX2.txt"))
node_positions = {}
layout = {'name': 'preset'}
elements = d['elements']

app.layout = html.Div([
    	cyto.Cytoscape(
		id='cytoscape',
		elements=elements,
		style={'width': '100%', 'height': '1000px'},
		layout=layout,
		stylesheet=[
		# Group selectors
		{
			'selector': 'node',
			'style': {
			'content': 'data(label)'
			
			}
		},

		# Class selectors
		{
			'selector': '.path',
			'style': {
			
			'line-color':'red'
			}
		},
		
		{
			'selector': '.outsidepath',
			'style': {
			
			'line-color':'green'
			}
		},
		
		{
			'selector': '.switch',
			'style': {
			'width': 50,
			'height' : 20,
			'shape' : 'square',
			'background-fit' : 'cover',
			'background-image': 'data(url)',
			}
		},
		
		
		{
			'selector': '.pc',
			'style': {
			'width': 50,
			'height' : 50,
			'shape': 'square',
			'background-fit' : 'cover',
			'background-image': 'data(url)'
		}
		},
		
		]
		
		),
        dcc.Interval(
		id='interval-component',
		interval=1*500, # in milliseconds
		n_intervals=0),
	dcc.Interval(
		id='interval-component2',
		interval=1*500, # in milliseconds
		n_intervals=0)
])

class CustomDecoder(json.JSONDecoder):
    def decode(self, s):
        result = super().decode(s)
        if isinstance(result, str):
            return json.loads(result)
        return result



@app.callback(Output('cytoscape', 'elements'),
              [Input('interval-component', 'n_intervals')])
def update_elements(elements):
	d = json.load(open("nX2.txt"))
	with open('n2Xe.txt', 'r') as file:
		json_string = file.read()
		d2 = json.loads(json_string,cls=CustomDecoder)
	elements = d['elements']
	nodes = elements['nodes']
	edges = elements['edges']
	
	path = d2['path']
	path = ['SW'+str(i) for i in path]
	for_hosts = d2['for_hosts']
	hosts = d2['hosts']
	visited = d2['visited']
	visited = ['SW'+str(i) for i in visited]
	
	
	# Update edge
	for edge in edges:
		edge['classes'] = 'outsidepath'
		
	for host in for_hosts:
		swid = hosts[host]['DPID']
		for edge in edges:
			if edge['data']['source'] == 'SW'+str(swid) and edge['data']['target'] == str(host):
				edge['classes'] = 'path'
	for i in range(len(path)-1):
		id1 = path[i]
		id2 = path[i+1]
		
		for edge in edges:
			if edge['data']['source'] == str(id1) and edge['data']['target'] == str(id2):
				edge['classes'] = 'path'
				
			if edge['data']['source'] == str(id2) and edge['data']['target'] == str(id1):
				edge['classes'] = 'path'
				
			
	
	
	# Update node positions
	for node in nodes:
		node_id = node['data']['id']
		node['data']['content'] = node['data']['name']
		
		
		
		if node_id[0] == 'S':
			node['classes'] = 'switch'
			node['data']['not-active'] = 'https://lh3.googleusercontent.com/drive-viewer/AFGJ81qODdimTAnTQv-TELWW6V2Nuf_3-85JA_c8SuZi0RYD72zlFnx-j0sgbXWgr0azxR2U4OT_OpZdruUnoooOGipBgDPj4w=s2560'
			node['data']['active'] = 'https://lh3.googleusercontent.com/drive-viewer/AFGJ81pjZnVOEGo3EBnn_TH8NF7A8qQSVBO681RRo3cvgAsRvtwCjM5h-TRTVTGW0XtpeA3aWBu1pvQwv1TYSeR3eIgio1j7EA=s2560'
		else:
			node['classes'] = 'pc'
			node['data']['not-active'] = 'https://lh3.googleusercontent.com/drive-viewer/AFGJ81oebxgQsrNgPS0KJO5tPnYw25j0ZyLnQOj3aePY4FiEKCWEpjvZH5HZYKcdGCtodof8d5i1A4ReueyeOXzsifchZ8qd=s2560'
			node['data']['active'] = 'https://lh3.googleusercontent.com/drive-viewer/AFGJ81rxgtQFr3uyaaAKAQT3pNl-fn7qjfLsRi7O22FzQ8NSh2DfJ3xSrPxDctdEP5bYkaKa-4LH8r9w3YhPAA9tmATMhgDieA=s2560'
		
		if node_id in path:
			
			node['data']['label'] = node['data']['name']
			node['classes'] = node['classes']+' '+'path'
			node['data']['url'] = node['data']['active']
		else:
			node['classes'] = node['classes']+' '+'outsidepath'
			node['data']['label'] = node['data']['name']
			node['data']['url'] = node['data']['not-active']
		
		if node_id in for_hosts:
			node['data']['url'] = node['data']['active']
			
		#if node_positions:
		#	if node_id in node_positions:
		#		node['position'] = node_positions[node_id]
		
		
		
		
	
	
	

	return {'nodes':nodes,'edges':edges}
	
	

#@app.callback(Output('cytoscape', 'position'),[Input('cytoscape', 'position')])
def store_node_positions(position):
	print(position)
	global node_positions
	node_positions = position
	return position


if __name__ == '__main__':
	app.run_server(debug=True)






