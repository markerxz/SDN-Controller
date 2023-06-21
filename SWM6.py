from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import arp,icmp
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import ipv6
from ryu.lib.packet import ether_types
from ryu.lib import mac, ip
from ryu.app.wsgi import ControllerBase
from ryu.topology import event
from ryu.lib.dpid import dpid_to_str
from ryu.topology import event, switches
from ryu.topology.api import get_switch, get_link
from ryu.ofproto.ofproto_v1_2 import OFPG_ANY
from ryu.ofproto.ofproto_v1_3 import OFP_VERSION
import networkx as nx
import PIL
import urllib.request
import dash
from dash import Dash, html
import dash_core_components as doc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input,Output
import time
from collections import defaultdict
from operator import itemgetter
import dash_cytoscape as cyto
import tkinter as tk
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)

class SWM(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
	
	def draw(self):
		print('DRRRRRRRRRRRRRRRRRAAAAAAAAAAAAAAAAWWWWWWWWWWWWWWWww')
		print(nx.cytoscape_data(self.G))
		print('----------------------------------------------------')
		import json
		json.dump(nx.cytoscape_data(self.G), open("nX2.txt",'w'))
		
		j2 = {'path':self.path,'visited':self.visited,'for_hosts':self.for_hosts,'hosts':self.hosts}
		
		def custom_encoder(obj):
			if isinstance(obj, (list, tuple)):
				return [str(item) for item in obj]
			return str(obj)
		json_string = json.dumps(j2,default=custom_encoder)
		print(json_string)
		file_path = 'n2Xe.txt'

		with open(file_path, 'w') as file:
			json.dump(json_string, file)
		
		
		
	
	
	def __init__(self, *args, **kwargs):
		super(SWM, self).__init__(*args, **kwargs)
		self.mac_to_port = {}
		self.topology_api_app = self
		self.datapath_list = {}
		self.arp_table = {}
		self.switches = []
		self.hosts = {}
		self.hosts_ip = {}
		self.adjacency = defaultdict(dict)
		self.path = []
		self.visited = []
		self.for_hosts = []
		self.bandwidths = defaultdict(lambda: defaultdict(lambda: DEFAULT_BW))
		self.icons = {"switch":'switch.png',"PC":'pc.png'}
		print('----------- I N I T ----------')
		self.images = {k : PIL.Image.open(fname) for k,fname in self.icons.items()}
		self.G = nx.Graph()
		
		print('------------ END OF INIT ---------------')


	@set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
	def switch_features_handler(self, ev):
		datapath = ev.msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		print('*************')
		print('START SWFHNDLR')	
		match = parser.OFPMatch()
		actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,ofproto.OFPCML_NO_BUFFER)]
		self.add_flow(datapath, 0, match, actions)
		print('END SWFH')
		print('*************')

	def add_flow(self, datapath, priority, match, actions, buffer_id=None):
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,actions)]
		
		if buffer_id:
		    	mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
					    priority=priority, match=match,
					    instructions=inst)
		else:
		    	mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
					    match=match, instructions=inst)
		datapath.send_msg(mod)
		
	
	def path_finder(self,src_ip,dst_ip):
		q = []
		start = self.hosts[src_ip]['DPID']
		end = self.hosts[dst_ip]['DPID']
		start = str(start)
		end = str(end)
		import numpy as np
		# (weight, from)
		weight = {str(switch):[2e9,2e9] for switch in self.switches}
		#weight = np.full((len(self.switches)+1,2),int(2e9))
		
		weight[start][0] = 0
		weight[start][1] = 0
		print(weight)
		node_now = start
		print('START : ',start,' END : ',end)
		
		for node_to in self.adjacency[start]:
			node_now = str(node_now)
			node_to = str(node_to)
			if weight[node_now][0] + 1 < weight[node_to][0]:
				 weight[node_to][0] = weight[node_now][0] + 1 
				 weight[node_to][1] = node_now
				 q.append(node_to)
		
		
		while q:
			
			node_now = q.pop(0)
			node_now = str(node_now)
			if node_now == end:
				
				path = []
				pathX = {}
				while node_now != 0:
					path.append(str(node_now))
					node_now = weight[node_now][1]
					
				for i in range(len(path)):
					
					if i == 0:
						node_rep = str(dst_ip)
						port_rep = self.hosts[dst_ip]['IN_PORT']
						node_req = str(path[i+1])
						port_req = self.adjacency[path[i]][path[i+1]]
					elif i == len(path) - 1:
						node_rep = str(path[i-1])
						port_rep = self.adjacency[path[i]][path[i-1]]
						node_req = str(src_ip)
						port_req = self.hosts[src_ip]['IN_PORT']
					else:
						node_rep = str(path[i-1])
						port_rep = self.adjacency[path[i]][path[i-1]]
						node_req = str(path[i+1])
						port_req = self.adjacency[path[i]][path[i+1]]	
					pathX[path[i]] = {'REPLY':{'ID':node_rep,'PORT':port_rep},'REQUEST':{'ID':node_req,'PORT':port_req}}
					
				self.for_hosts = [src_ip,dst_ip]
				self.path = path
				self.pathX = pathX
				
				return path,pathX
			else:
				for node_to in self.adjacency[node_now]:
					if weight[node_now][0] + 1 < weight[node_to][0]:
						weight[node_to][0] = weight[node_now][0] + 1 
						weight[node_to][1] = node_now
						q.append(node_to)
		
		
	def assign_path(self,src_ip,dst_ip):
		print('ASSIGN PATH')
		self.remove_flows()
		path,pathX = self.path_finder(src_ip,dst_ip)
		print('PATH = ',path)
		print('PATHX = ',pathX)
		for node in pathX:
			dp = self.datapath_list[node]
			ofp = dp.ofproto
			ofp_parser = dp.ofproto_parser

			#REPLY            				
			match_ip = ofp_parser.OFPMatch(
			    eth_type=0x0800,
			    ipv4_dst=dst_ip
			)
			match_arp = ofp_parser.OFPMatch(
			    eth_type=0x0806,
			    arp_tpa=dst_ip
			)
			out_port = pathX[node]['REPLY']['PORT']
			#actions = [ofp_parser.OFPActionOutput(out_port)]
			actions = [ofp_parser.OFPActionOutput(out_port),ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER,ofp.OFPCML_NO_BUFFER)]
			self.add_flow(dp, 123, match_ip, actions)
			self.add_flow(dp, 1, match_arp, actions)
			#REQUEST
			match_ip = ofp_parser.OFPMatch(
			    eth_type=0x0800,
			    ipv4_dst=src_ip
			)
			match_arp = ofp_parser.OFPMatch(
			    eth_type=0x0806,
			    arp_tpa=src_ip
			)
			out_port = pathX[node]['REQUEST']['PORT']
			#actions = [ofp_parser.OFPActionOutput(out_port)]
			actions = [ofp_parser.OFPActionOutput(out_port),ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER,ofp.OFPCML_NO_BUFFER)]
			self.add_flow(dp, 123, match_ip, actions)
			self.add_flow(dp, 1, match_arp, actions)
	
	
	def router(self,dpid,src_ip,dst_ip,datapath):
			
		if src_ip in self.hosts and dst_ip in self.hosts and self.hosts[src_ip] != None and self.hosts[dst_ip] != None:
			print('HOST IN THE LIST!')
			if not(dpid in self.path and src_ip in self.for_hosts and dst_ip in self.for_hosts):
				self.assign_path(src_ip,dst_ip)
				self.draw()
				print('PATH INSTALL 788%')
			
			if dpid in self.path:
				print('WE HAVE PATH ALREADY')
				if src_ip == self.for_hosts[0]:
					print('THIS IS REPLY')
					print('WE GO SW', self.pathX[dpid]['REPLY']['ID'],' WITH PORT',self.pathX[dpid]['REPLY']['PORT'])
					return self.pathX[dpid]['REPLY']['PORT']
				else:
					print('THIS IS REQUEST')
					print('WE GO SW', self.pathX[dpid]['REQUEST']['ID'],' WITH PORT',self.pathX[dpid]['REQUEST']['PORT'])
					return self.pathX[dpid]['REQUEST']['PORT']
			else:
								
				print('THIS NODE IS OUTSIDE OUR PATH >> NONE')
				return None
				
		else:
			if src_ip not in self.hosts:
				self.hosts[src_ip] = None
				self.visited = []
			
			if dst_ip not in self.hosts:
				self.hosts[dst_ip] = None
				self.visited = []
			
			print('STILL NO IDEA WHERE IS HOST(S)')		
			print('VISITED : ',self.visited)
			outs = []
			if dpid not in self.visited:
				self.visited.append(dpid)
				return datapath.ofproto.OFPP_FLOOD
			else:
				print('BUT THIS SWITCH WAS VISITED')
				return None
	
	
	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser
		in_port = msg.match['in_port']

		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocol(ethernet.ethernet)
		arp_pkt = pkt.get_protocol(arp.arp)
		icmp_pkt = pkt.get_protocol(icmp.icmp)
		ipv4_header = pkt.get_protocol(ipv4.ipv4)
		
		# avoid broadcast from LLDP
		if eth.ethertype == 35020:
			return

		if pkt.get_protocol(ipv6.ipv6):  # Drop the IPV6 Packets.
			
			match = parser.OFPMatch(eth_type=eth.ethertype)
			actions = []
			self.add_flow(datapath, 1, match, actions)
			return None

		dst = eth.dst
		src = eth.src
		dpid = str(datapath.id)
		data = msg.data
		
		
		
		print('------------------START PACKETIN HANDLR------------------')
		print('DPID : ',dpid,' INPORT : ',in_port)
		print('ETH : ',eth)
		
		
		out_port = ofproto.OFPP_FLOOD
		
		
		if arp_pkt:
			print('ARPA')
			# print dpid, pkt
			src_ip = arp_pkt.src_ip
			dst_ip = arp_pkt.dst_ip
			print(src_ip+' >>> '+dst_ip)
			if src_ip not in self.for_hosts or dst_ip not in self.for_hosts:
				self.for_hosts = []
				self.path = []
				
			if src_ip not in self.hosts or self.hosts[src_ip] == None:
				self.hosts[src_ip] = {'DPID':dpid, 'IN_PORT':in_port, 'SRCMAC':src}
				self.G.add_node(str(src_ip))
				self.G.add_edge('SW'+str(dpid),str(src_ip))
				self.draw()
			
			if arp_pkt.opcode == arp.ARP_REPLY:
				print('ARP_REPLY')
				out_port = self.router(dpid,src_ip,dst_ip,datapath)
				if dpid in self.path:
					out_port = None
				
			elif arp_pkt.opcode == arp.ARP_REQUEST:
				print('ARP_REQUEST')
				out_port = self.router(dpid,src_ip,dst_ip,datapath)
				if dpid in self.path:
					out_port = None
				
		
			if out_port == ofproto.OFPP_FLOOD:
				print('FLoOoOoD')
		
		
		elif icmp_pkt:
			print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxICMPxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
			# print dpid, pkt
			if ipv4_header:
				src_ip = ipv4_header.src
				dst_ip = ipv4_header.dst
				print(src_ip+' >>> '+dst_ip)
			
				if src_ip not in self.hosts or self.hosts[src_ip] == None:
					self.hosts[src_ip] = {'DPID':dpid, 'IN_PORT':in_port, 'SRCMAC':src}
					self.G.add_node(str(src_ip))
					self.G.add_edge('SW'+str(dpid),str(src_ip))
					self.draw()
				
				out_port = self.router(dpid,src_ip,dst_ip,datapath)
				if dpid in self.path:
					out_port = None
					
				if out_port == ofproto.OFPP_FLOOD:
					print('FLoOoOoD')
		else:
			print("WTF IS THIS PACKET")
		
						
		print('FINAL OUTPUT : ',out_port)
	
		if out_port != None:
			
			actions = [parser.OFPActionOutput(out_port)]
			data = msg.data

			out = parser.OFPPacketOut(
			    datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
			    actions=actions, data=data)
			datapath.send_msg(out)
			print('------------------END PACKETIN HANDLR------------------')
		
		
		
	@set_ev_cls(event.EventSwitchEnter)
	def switch_enter_handler(self, ev):
		switch = ev.switch.dp
		ofp_parser = switch.ofproto_parser
		switch_id = str(switch.id)
		print('ENTER > ID = ',switch_id)
		if switch_id not in self.switches:
			self.switches.append(switch_id)
			self.datapath_list[switch_id] = switch

			# Request port/link descriptions, useful for obtaining bandwidth
			req = ofp_parser.OFPPortDescStatsRequest(switch)
			switch.send_msg(req)
			self.G.add_node(f"SW{switch.id}")
			self.draw()
			self.remove_flows()
			if len(self.for_hosts) == 2:
				src_ip,dst_ip = self.for_hosts
				self.assign_path(src_ip,dst_ip)
		
	def remove_flows(self):
		print('REMOVE FLOWSS')
		for datapath_id in self.datapath_list:
			datapath = self.datapath_list[datapath_id]
			self.remove_flow(datapath)
	
	def remove_flow(self,datapath,table_id = 0):
		parser = datapath.ofproto_parser
		ofproto = datapath.ofproto
		empty_match = parser.OFPMatch()
		instructions = []
		flow_mod = self.remove_table_flows(datapath,table_id,empty_match,instructions)
		datapath.send_msg(flow_mod)
		ofp_parser = parser
		ofp = datapath.ofproto
		actions = [ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER,ofp.OFPCML_NO_BUFFER)]
		match = ofp_parser.OFPMatch()
		self.add_flow(datapath, 0, match, actions)
	
	def remove_table_flows(self,datapath,table_id,match,instructions):
		ofproto = datapath.ofproto
		flow_mod = datapath.ofproto_parser.OFPFlowMod(datapath,0,0,table_id,ofproto.OFPFC_DELETE,0,0,1,ofproto.OFPCML_NO_BUFFER,ofproto.OFPP_ANY,OFPG_ANY,0,match,instructions)
		return flow_mod	
	
	@set_ev_cls(event.EventSwitchLeave, MAIN_DISPATCHER)
	def switch_leave_handler(self, ev):	
		if switch in self.switches:
			print('REMOVE SWITHCH : ',switch)
			self.remove_flows()
			self.switches.remove(switch)
			del self.datapath_list[switch]
			del self.adjacency[switch]
			self.G.remove_node(f"SW{switch.id}")
			self.draw()
			if len(self.for_hosts) == 2:
				src_ip,dst_ip = self.for_hosts
				self.assign_path(src_ip,dst_ip)
	
	@set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
	def port_desc_stats_reply_handler(self, ev):
		switch = ev.msg.datapath
		for p in ev.msg.body:
			self.bandwidths[switch.id][p.port_no] = p.curr_speed
		

	@set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
	def port_status_handler(self, ev):
		print('PORTSTATUSHANDLER')
		msg = ev.msg
		dp = msg.datapath
		ofp = dp.ofproto
		datapath = msg.datapath
		dpid = datapath.id
		print('DPID : ',dpid)
		if msg.reason == ofp.OFPPR_ADD:
			reason = 'ADD'
		elif msg.reason == ofp.OFPPR_DELETE:
			reason = 'DELETE'
		elif msg.reason == ofp.OFPPR_MODIFY:
			reason = 'MODIFY'
		else:
			reason = 'unknown'

		self.logger.info('OFPPortStatus received: reason=%s desc=%s',
			      reason, msg.desc)
		              
	
	
			
		
	@set_ev_cls(event.EventLinkAdd, MAIN_DISPATCHER)
	def link_add_handler(self, ev):
		print('ADDLINK')
		s1 = ev.link.src
		s2 = ev.link.dst
		self.adjacency[str(s1.dpid)][str(s2.dpid)] = s1.port_no
		self.adjacency[str(s2.dpid)][str(s1.dpid)] = s2.port_no
		self.path = []
		self.remove_flows()
		print('ADJA ADDDDDDDDDDDDD')
		print(self.adjacency)
		if len(self.for_hosts) == 2:
			src_ip,dst_ip = self.for_hosts
			self.assign_path(src_ip,dst_ip)
		self.G.add_edge('SW'+str(s1.dpid),'SW'+str(s2.dpid))
		self.draw()
		print('END ADDLINK')
        	


	@set_ev_cls(event.EventLinkDelete, MAIN_DISPATCHER)
	def link_delete_handler(self, ev):
		print('DELLINK')
		s1 = ev.link.src
		s2 = ev.link.dst
	# Exception handling if switch already deleted
		try:
			del self.adjacency[str(s1.dpid)][str(s2.dpid)]
			del self.adjacency[str(s2.dpid)][str(s1.dpid)]
			self.path = []
			self.remove_flows()
			print('ADJA DELLLLLLLLLLLLLLL')
			print(self.adjacency)
			if len(self.for_hosts) == 2:
				src_ip,dst_ip = self.for_hosts
				self.assign_path(src_ip,dst_ip)
			self.G.remove_edge('SW'+str(s1.dpid),'SW'+str(s2.dpid))
			self.draw()

		except KeyError:
	    		pass
		
