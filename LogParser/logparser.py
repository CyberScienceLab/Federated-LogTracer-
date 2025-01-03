# -*- coding: utf-8 -*-
"""LogParser.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1UNEGfxnZ-hIlJfqA9tuHBViMtgjHiimu
"""

import torch
print(torch.__version__)

import torch_cluster
import torch_scatter
import torch_sparse
import torch_spline_conv

import torch_geometric

import time
import pandas as pd
import numpy as np
import os
import os.path as osp
import csv
import re

def show(str):
	print (str + ' ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

import re
import os
import os.path as osp


path_list = ['ta1-cadets-e3-official.json', 'ta1-cadets-e3-official-2.json', 'ta1-fivedirections-e3-official-2.json', 'ta1-theia-e3-official-1r.json', 'ta1-theia-e3-official-6r.json', 'ta1-trace-e3-official-1.json']

pattern_uuid = re.compile(r'uuid\":\"(.*?)\"')
pattern_src = re.compile(r'subject\":{\"com.bbn.tc.schema.avro.cdm18.UUID\":\"(.*?)\"}')
pattern_dst1 = re.compile(r'predicateObject\":{\"com.bbn.tc.schema.avro.cdm18.UUID\":\"(.*?)\"}')
pattern_dst2 = re.compile(r'predicateObject2\":{\"com.bbn.tc.schema.avro.cdm18.UUID\":\"(.*?)\"}')
pattern_type = re.compile(r'type\":\"(.*?)\"')
pattern_time = re.compile(r'timestampNanos\":(.*?),')
# New pattern for extracting path information
pattern_path = re.compile(r'"predicateObjectPath":\{"string":"(.*?)"\}')
# pattern_path2 = re.compile(r'"predicateObject2Path":\{"string":"(.*?)"\}')


notice_num = 1000000

for path in path_list:
    id_nodetype_map = {}
    for i in range(100):
        now_path = path + '.' + str(i)
        if i == 0: now_path = path
        if not osp.exists(now_path): break
        with open(now_path, 'r') as f:
            print(f"Processing file: {now_path}")
            cnt = 0
            for line in f:
                cnt += 1
                if cnt % notice_num == 0:
                    print(f"Processed {cnt} lines")
                if 'com.bbn.tc.schema.avro.cdm18.Event' in line or 'com.bbn.tc.schema.avro.cdm18.Host' in line: continue
                if 'com.bbn.tc.schema.avro.cdm18.TimeMarker' in line or 'com.bbn.tc.schema.avro.cdm18.StartMarker' in line: continue
                if 'com.bbn.tc.schema.avro.cdm18.UnitDependency' in line or 'com.bbn.tc.schema.avro.cdm18.EndMarker' in line: continue
                if len(pattern_uuid.findall(line)) == 0:
                    print(line)
                    continue
                uuid = pattern_uuid.findall(line)[0]
                subject_type = pattern_type.findall(line)

                if len(subject_type) < 1:
                    if 'com.bbn.tc.schema.avro.cdm18.MemoryObject' in line:
                        id_nodetype_map[uuid] = 'MemoryObject'
                        continue
                    if 'com.bbn.tc.schema.avro.cdm18.NetFlowObject' in line:
                        id_nodetype_map[uuid] = 'NetFlowObject'
                        continue
                    if 'com.bbn.tc.schema.avro.cdm18.UnnamedPipeObject' in line:
                        id_nodetype_map[uuid] = 'UnnamedPipeObject'
                        continue

                id_nodetype_map[uuid] = subject_type[0]

    not_in_cnt = 0
    for i in range(100):
        now_path = path + '.' + str(i)
        if i == 0: now_path = path
        if not osp.exists(now_path): break
        with open(now_path, 'r') as f, open(now_path + '.txt', 'w') as fw:
            cnt = 0
            for line in f:
                cnt += 1
                if cnt % notice_num == 0:
                    print(f"Processed {cnt} lines")

                if 'com.bbn.tc.schema.avro.cdm18.Event' in line:
                    edgeType = pattern_type.findall(line)[0]
                    timestamp = pattern_time.findall(line)[0]
                    srcId = pattern_src.findall(line)
                    if len(srcId) == 0: continue
                    srcId = srcId[0]
                    if srcId not in id_nodetype_map.keys():
                        not_in_cnt += 1
                        continue
                    srcType = id_nodetype_map[srcId]
                    dstId1 = pattern_dst1.findall(line)
                    path_info = pattern_path.findall(line)
                    path_info = path_info[0] if path_info else "N/A"
                    if len(dstId1) > 0 and dstId1[0] != 'null':
                        dstId1 = dstId1[0]
                        if dstId1 not in id_nodetype_map.keys():
                            not_in_cnt += 1
                            continue
                        dstType1 = id_nodetype_map[dstId1]
                        this_edge1 = f"{srcId}\t{srcType}\t{dstId1}\t{dstType1}\t{edgeType}\t{timestamp}\t{path_info}\n"
                        fw.write(this_edge1)

                    dstId2 = pattern_dst2.findall(line)
                    if len(dstId2) > 0 and dstId2[0] != 'null':
                        dstId2 = dstId2[0]
                        if dstId2 not in id_nodetype_map.keys():
                            not_in_cnt += 1
                            continue
                        dstType2 = id_nodetype_map[dstId2]
                        this_edge2 = f"{srcId}\t{srcType}\t{dstId2}\t{dstType2}\t{edgeType}\t{timestamp}\t{path_info}\n"
                        fw.write(this_edge2)
            fw.close()
            f.close()
os.system('cp ta1-theia-e3-official-1r.json.txt theia_train.txt')
os.system('cp ta1-theia-e3-official-6r.json.8.txt theia_test.txt')
os.system('cp ta1-cadets-e3-official.json.1.txt cadets_train.txt')
os.system('cp ta1-cadets-e3-official-2.json.txt cadets_test.txt')
os.system('cp ta1-fivedirections-e3-official-2.json.txt fivedirections_train.txt')
os.system('cp ta1-fivedirections-e3-official-2.json.23.txt fivedirections_test.txt')
os.system('cp ta1-trace-e3-official-1.json.txt trace_train.txt')
os.system('cp ta1-trace-e3-official-1.json.4.txt trace_test.txt')

# import re
# import os
# import os.path as osp


# path_list = ['ta1-cadets-e3-official.json', 'ta1-cadets-e3-official-2.json', 'ta1-fivedirections-e3-official-2.json', 'ta1-theia-e3-official-1r.json', 'ta1-theia-e3-official-6r.json', 'ta1-trace-e3-official-1.json']

# pattern_uuid = re.compile(r'uuid\":\"(.*?)\"')
# pattern_src = re.compile(r'subject\":{\"com.bbn.tc.schema.avro.cdm18.UUID\":\"(.*?)\"}')
# pattern_dst1 = re.compile(r'predicateObject\":{\"com.bbn.tc.schema.avro.cdm18.UUID\":\"(.*?)\"}')
# pattern_dst2 = re.compile(r'predicateObject2\":{\"com.bbn.tc.schema.avro.cdm18.UUID\":\"(.*?)\"}')
# pattern_type = re.compile(r'type\":\"(.*?)\"')
# pattern_time = re.compile(r'timestampNanos\":(.*?),')
# # New pattern for extracting path information
# pattern_path = re.compile(r'"predicateObjectPath":\{"string":"(.*?)"\}')
# pattern_path2= re.compile(r'"predicateObject2Path":\{"string":"(.*?)"\}')


# notice_num = 1000000

# for path in path_list:
#     id_nodetype_map = {}
#     for i in range(100):
#         now_path = path + '.' + str(i)
#         if i == 0: now_path = path
#         if not osp.exists(now_path): break
#         with open(now_path, 'r') as f:
#             print(f"Processing file: {now_path}")
#             cnt = 0
#             for line in f:
#                 cnt += 1
#                 if cnt % notice_num == 0:
#                     print(f"Processed {cnt} lines")
#                 if 'com.bbn.tc.schema.avro.cdm18.Event' in line or 'com.bbn.tc.schema.avro.cdm18.Host' in line: continue
#                 if 'com.bbn.tc.schema.avro.cdm18.TimeMarker' in line or 'com.bbn.tc.schema.avro.cdm18.StartMarker' in line: continue
#                 if 'com.bbn.tc.schema.avro.cdm18.UnitDependency' in line or 'com.bbn.tc.schema.avro.cdm18.EndMarker' in line: continue
#                 if len(pattern_uuid.findall(line)) == 0:
#                     print(line)
#                     continue
#                 uuid = pattern_uuid.findall(line)[0]
#                 subject_type = pattern_type.findall(line)

#                 if len(subject_type) < 1:
#                     if 'com.bbn.tc.schema.avro.cdm18.MemoryObject' in line:
#                         id_nodetype_map[uuid] = 'MemoryObject'
#                         continue
#                     if 'com.bbn.tc.schema.avro.cdm18.NetFlowObject' in line:
#                         id_nodetype_map[uuid] = 'NetFlowObject'
#                         continue
#                     if 'com.bbn.tc.schema.avro.cdm18.UnnamedPipeObject' in line:
#                         id_nodetype_map[uuid] = 'UnnamedPipeObject'
#                         continue

#                 id_nodetype_map[uuid] = subject_type[0]

#     not_in_cnt = 0
#     for i in range(100):
#         now_path = path + '.' + str(i)
#         if i == 0: now_path = path
#         if not osp.exists(now_path): break
#         with open(now_path, 'r') as f, open(now_path + '.txt', 'w') as fw:
#             cnt = 0
#             for line in f:
#                 cnt += 1
#                 if cnt % notice_num == 0:
#                     print(f"Processed {cnt} lines")

#                 if 'com.bbn.tc.schema.avro.cdm18.Event' in line:
#                     edgeType = pattern_type.findall(line)[0]
#                     timestamp = pattern_time.findall(line)[0]
#                     srcId = pattern_src.findall(line)
#                     if len(srcId) == 0: continue
#                     srcId = srcId[0]
#                     if srcId not in id_nodetype_map.keys():
#                         not_in_cnt += 1
#                         continue
#                     srcType = id_nodetype_map[srcId]
#                     dstId1 = pattern_dst1.findall(line)
#                     dstId2 = pattern_dst2.findall(line)
#                     path_info = pattern_path.findall(line)
#                     path_info2 = pattern_path2.findall(line)
#                     path_info = path_info[0] if path_info else "N/A"
#                     path_info2 = path_info2[0] if path_info2 else "N/A"

#                     if len(dstId1) > 0 and dstId1[0] != 'null':
#                         dstId1 = dstId1[0]
#                         if dstId1 not in id_nodetype_map.keys():
#                             not_in_cnt += 1
#                             continue
#                         dstType1 = id_nodetype_map[dstId1]
#                         this_edge1 = f"{srcId}\t{srcType}\t{dstId1}\t{dstType1}\t{edgeType}\t{timestamp}\t{path_info}\n"
#                         fw.write(this_edge1)

#                     if len(dstId2) > 0 and dstId2[0] != 'null':
#                         dstId2 = dstId2[0]
#                         if dstId2 not in id_nodetype_map.keys():
#                             not_in_cnt += 1
#                             continue
#                         dstType2 = id_nodetype_map[dstId2]
#                         this_edge2 = f"{srcId}\t{srcType}\t{dstId2}\t{dstType2}\t{edgeType}\t{timestamp}\t{path_info2}\n"
#                         fw.write(this_edge2)
#             fw.close()
#             f.close()
# os.system('cp ta1-theia-e3-official-1r.json.txt theia_train.txt')
# os.system('cp ta1-theia-e3-official-6r.json.8.txt theia_test.txt')
# os.system('cp ta1-cadets-e3-official.json.1.txt cadets_train.txt')
# os.system('cp ta1-cadets-e3-official-2.json.txt cadets_test.txt')
# os.system('cp ta1-fivedirections-e3-official-2.json.txt fivedirections_train.txt')
# os.system('cp ta1-fivedirections-e3-official-2.json.23.txt fivedirections_test.txt')
# os.system('cp ta1-trace-e3-official-1.json.txt trace_train.txt')
# os.system('cp ta1-trace-e3-official-1.json.4.txt trace_test.txt')

#set up
import os

#step1: define environment variable GRAPHCHI_ROOT
#############################################
graphchi_root = os.path.abspath(os.path.join(os.getcwd(), 'graphchi-cpp-master'))
os.environ['GRAPHCHI_ROOT'] = graphchi_root



#step2: clean models directory ../models
#############################################
model_dir = 'models'
models = os.listdir(model_dir)
# for i in models:
# 	path = os.path.join(model_dir,i)
# 	os.system('rm ' + path)
# os.system('rm result_*')



## Train#########

import os.path as osp
import os
import argparse
import torch
import time
import torch.nn.functional as F
import numpy as np
from torch_geometric.datasets import Reddit
from torch_geometric.data import NeighborSampler, DataLoader
from torch_geometric.nn import SAGEConv, GATConv

from data_process_train import *
from data_process_test import *

import data_process_train
import data_process_test

"""#"""

import os.path as osp
import argparse
import torch
import time
import torch.nn.functional as F
from torch_geometric.datasets import Planetoid
import torch_geometric.transforms as T
from torch_geometric.nn import GCNConv, GAE, VGAE
from torch_geometric.data import Data, InMemoryDataset

def show(str):
	print (str + ' ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

class TestDatasetA(InMemoryDataset):
	def __init__(self, data_list):
		super(TestDatasetA, self).__init__('/tmp/TestDataset')
		self.data, self.slices = self.collate(data_list)

	def _download(self):
		pass
	def _process(self):
		pass

def MyDatasetA(path, model):
	graphId = model
	feature_num = 0
	label_num = 0
	f_feature = open('models/feature.txt', 'r')
	feature_map = {}
	for i in f_feature:
		temp = i.strip('\n').split('\t')
		feature_map[temp[0]] = int(temp[1])
		feature_num += 1
	f_feature.close()

	f_label = open('models/label.txt', 'r')
	label_map = {}
	for i in f_label:
		temp = i.strip('\n').split('\t')
		label_map[temp[0]] = int(temp[1])
		label_num += 1
	f_label.close()

	f_gt = open('groundtruth_uuid.txt', 'r')
	ground_truth = {}
	for line in f_gt:
		ground_truth[line.strip('\n')] = 1

	f_gt.close()
	node_cnt = 0
	nodeType_cnt = 0
	edgeType_cnt = 0
	provenance = []
	nodeType_map = {}
	edgeType_map = {}
	edge_s = []
	edge_e = []
	adj = {}
	adj2 = {}
	data_thre = 1000000
	fw = open('groundtruth_nodeId.txt', 'w')
	fw2 = open('id_to_uuid.txt', 'w')
	nodeId_map = {}
	cnt = 0
	nodeA = []
	for i in range(1):
		now_path = path
		show(now_path)
		f = open(now_path, 'r')
		for line in f:
			cnt += 1
			temp = line.strip('\n').split('\t')
			if not (temp[1] in label_map.keys()): continue
			if not (temp[3] in label_map.keys()): continue
			if not (temp[4] in feature_map.keys()): continue

			if not (temp[0] in nodeId_map.keys()):
				nodeId_map[temp[0]] = node_cnt
				fw2.write(str(node_cnt) + ' ' + temp[0] + '\n')

				if temp[0] in ground_truth.keys():
					fw.write(str(nodeId_map[temp[0]])+' '+temp[1]+' '+temp[0]+'\n')
					nodeA.append(node_cnt)
				node_cnt += 1

			temp[0] = nodeId_map[temp[0]]

			if not (temp[2] in nodeId_map.keys()):
				nodeId_map[temp[2]] = node_cnt
				fw2.write(str(node_cnt) + ' ' + temp[2] + '\n')

				if temp[2] in ground_truth.keys():
					fw.write(str(nodeId_map[temp[2]])+' '+temp[3]+' '+temp[2]+'\n')
					nodeA.append(node_cnt)
				node_cnt += 1
			temp[2] = nodeId_map[temp[2]]
			temp[1] = label_map[temp[1]]
			temp[3] = label_map[temp[3]]
			temp[4] = feature_map[temp[4]]
			edge_s.append(temp[0])
			edge_e.append(temp[2])
			if temp[2] in adj.keys():
				adj[temp[2]].append(temp[0])
			else:
				adj[temp[2]] = [temp[0]]
			if temp[0] in adj2.keys():
				adj2[temp[0]].append(temp[2])
			else:
				adj2[temp[0]] = [temp[2]]
			provenance.append(temp)
		f.close()
	fw.close()
	fw2.close()
	x_list = []
	y_list = []
	train_mask = []
	test_mask = []
	for i in range(node_cnt):
		temp_list = []
		for j in range(feature_num*2):
			temp_list.append(0)
		x_list.append(temp_list)
		y_list.append(0)
		train_mask.append(True)
		test_mask.append(True)

	for temp in provenance:
		srcId = temp[0]
		srcType = temp[1]
		dstId = temp[2]
		dstType = temp[3]
		edge = temp[4]
		x_list[srcId][edge] += 1
		y_list[srcId] = srcType
		x_list[dstId][edge+feature_num] += 1
		y_list[dstId] = dstType

	x = torch.tensor(x_list, dtype=torch.float)
	y = torch.tensor(y_list, dtype=torch.long)
	train_mask = torch.tensor(train_mask, dtype=torch.bool)
	test_mask = torch.tensor(test_mask, dtype=torch.bool)
	edge_index = torch.tensor([edge_s, edge_e], dtype=torch.long)
	data1 = Data(x=x, y=y,edge_index=edge_index, train_mask=train_mask, test_mask = test_mask)
	feature_num *= 2
	neibor = set()
	_neibor = {}
	for i in nodeA:
		neibor.add(i)
		if not i in _neibor.keys():
			templ = []
			_neibor[i] = templ
		if not i in _neibor[i]:
			_neibor[i].append(i)
		if i in adj.keys():
			for j in adj[i]:
				neibor.add(j)
				if not j in _neibor.keys():
					templ = []
					_neibor[j] = templ
				if not i in _neibor[j]:
					_neibor[j].append(i)
				if not j in adj.keys(): continue
				for k in adj[j]:
					neibor.add(k)
					if not k in _neibor.keys():
						templ = []
						_neibor[k] = templ
					if not i in _neibor[k]:
						_neibor[k].append(i)
		if i in adj2.keys():
			for j in adj2[i]:
				neibor.add(j)
				if not j in adj2.keys(): continue
				for k in adj2[j]:
					neibor.add(k)
	_nodeA = []
	for i in neibor:
		_nodeA.append(i)
	return [data1], feature_num, label_num, adj, adj2, nodeA, _nodeA, _neibor

import os.path as osp
import argparse
import torch
import time
import torch.nn.functional as F
from torch_geometric.datasets import Planetoid
import torch_geometric.transforms as T
from torch_geometric.nn import GCNConv, GAE, VGAE
from torch_geometric.data import Data, InMemoryDataset

class TestDataset(InMemoryDataset):
	def __init__(self, data_list):
		super(TestDataset, self).__init__('/tmp/TestDataset')
		self.data, self.slices = self.collate(data_list)

	def _download(self):
		pass
	def _process(self):
		pass

def MyDataset(path, model):
	graphId = model
	node_cnt = 0
	nodeType_cnt = 0
	edgeType_cnt = 0
	provenance = []
	nodeType_map = {}
	edgeType_map = {}
	edge_s = []
	edge_e = []
	data_thre = 1000000

	for out_loop in range(1):
		f = open(path, 'r')

		nodeId_map = {}

		for line in f:
			temp = line.strip('\n').split('\t')
			if not (temp[0] in nodeId_map.keys()):
				nodeId_map[temp[0]] = node_cnt
				node_cnt += 1
			temp[0] = nodeId_map[temp[0]]

			if not (temp[2] in nodeId_map.keys()):
				nodeId_map[temp[2]] = node_cnt
				node_cnt += 1
			temp[2] = nodeId_map[temp[2]]

			if not (temp[1] in nodeType_map.keys()):
				nodeType_map[temp[1]] = nodeType_cnt
				nodeType_cnt += 1
			temp[1] = nodeType_map[temp[1]]

			if not (temp[3] in nodeType_map.keys()):
				nodeType_map[temp[3]] = nodeType_cnt
				nodeType_cnt += 1
			temp[3] = nodeType_map[temp[3]]

			if not (temp[4] in edgeType_map.keys()):
				edgeType_map[temp[4]] = edgeType_cnt
				edgeType_cnt += 1

			temp[4] = edgeType_map[temp[4]]
			edge_s.append(temp[0])
			edge_e.append(temp[2])
			provenance.append(temp)

	f_train_feature = open('models/feature.txt', 'w')
	for i in edgeType_map.keys():
		f_train_feature.write(str(i)+'\t'+str(edgeType_map[i])+'\n')
	f_train_feature.close()
	f_train_label = open('models/label.txt', 'w')
	for i in nodeType_map.keys():
		f_train_label.write(str(i)+'\t'+str(nodeType_map[i])+'\n')
	f_train_label.close()
	feature_num = edgeType_cnt
	label_num = nodeType_cnt

	x_list = []
	y_list = []
	train_mask = []
	test_mask = []
	for i in range(node_cnt):
		temp_list = []
		for j in range(feature_num*2):
			temp_list.append(0)
		x_list.append(temp_list)
		y_list.append(0


		train_mask.append(True)
		test_mask.append(True)
	for temp in provenance:
		srcId = temp[0]
		srcType = temp[1]
		dstId = temp[2]
		dstType = temp[3]
		edge = temp[4]
		x_list[srcId][edge] += 1
		y_list[srcId] = srcType
		x_list[dstId][edge+feature_num] += 1
		y_list[dstId] = dstType

	x = torch.tensor(x_list, dtype=torch.float)
	y = torch.tensor(y_list, dtype=torch.long)
	train_mask = torch.tensor(train_mask, dtype=torch.bool)
	test_mask = train_mask
	edge_index = torch.tensor([edge_s, edge_e], dtype=torch.long)
	data1 = Data(x=x, y=y,edge_index=edge_index, train_mask=train_mask, test_mask = test_mask)
	feature_num *= 2
	return [data1], feature_num, label_num,0,0









from torch_geometric.data import NeighborSampler

thre_map = {"cadets":1.5,"trace":1.0,"theia":1.5,"fivedirections":1.0}

batch_size = 32

def show(*s):
	for i in range(len(s)):
		print (str(s[i]) + ' ', end = '')
	print (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))

####################Original######################################
# class SAGENet(torch.nn.Module):
# 	def __init__(self, in_channels, out_channels, concat=False):
# 		super(SAGENet, self).__init__()
# 		#self.conv1 = SAGEConv(in_channels, 32, normalize=False, concat=concat)
# 		#self.conv2 = SAGEConv(32, out_channels, normalize=False, concat=concat)
# 		self.conv1 = SAGEConv(in_channels, 32, normalize=False)
# 		self.conv2 = SAGEConv(32, out_channels, normalize=False)


# 	def forward(self, x, data_flow):
# 		data = data_flow[0]
# 		x = x[data.n_id]
# 		x = F.relu(self.conv1((x, None), data.edge_index, size=data.size,res_n_id=data.res_n_id))
# 		x = F.dropout(x, p=0.5, training=self.training)
# 		data = data_flow[1]
# 		x = self.conv2((x, None), data.edge_index, size=data.size,res_n_id=data.res_n_id)

# 		return F.log_softmax(x, dim=1)









#####################################################################
class SAGENet(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super(SAGENet, self).__init__()
        self.conv1 = SAGEConv(in_channels, out_channels)

    def forward(self, x, adjs):
        for i, (edge_index, _, size) in enumerate(adjs):
            x_target = x[:size[1]]  # Target nodes are always placed first.
            x = F.relu(self.conv1((x, x_target), edge_index, size=size))
            x = F.dropout(x, p=0.5, training=self.training)
        return F.log_softmax(x, dim=1)




########## Original ###############################################
# def train():
# 	model.train()
# 	total_loss = 0
# 	for data_flow in loader(data.train_mask):
# 		optimizer.zero_grad()
# 		out = model(data.x.to(device), data_flow.to(device))
# 		loss = F.nll_loss(out, data.y[data_flow.n_id].to(device))
# 		loss.backward()
# 		optimizer.step()
# 		total_loss += loss.item() * data_flow.batch_size
# 	return total_loss / data.train_mask.sum().item()
# #######################################################################
def train():
    model.train()
    total_loss = 0
    for batch_size, n_id, adjs in loader:
        # `adjs` holds a list of `(edge_index, e_id, size)` tuples.
        adjs = [adj.to(device) for adj in adjs]
        optimizer.zero_grad()
        out = model(data.x[n_id].to(device), adjs)
        loss = F.nll_loss(out, data.y[n_id[:batch_size]].to(device))
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * batch_size
    return total_loss / len(data.train_mask)









# def train():
#     model.train()
#     total_loss = 0
#     train_mask_long = data.train_mask.nonzero(as_tuple=False).view(-1).long()
#     loader = NeighborSampler(data.edge_index, node_idx=train_mask_long, sizes=[-1], batch_size=32, shuffle=True, num_workers=4)
#     for data_flow_tuple in loader:
#         print("Data flow tuple:", data_flow_tuple)
#         data_flow = data_flow_tuple[0]
#         print("Data flow:", data_flow)
#         optimizer.zero_grad()
#         edge_index = data_flow.edge_index.to(device)
#         out = model(data.x.to(device), edge_index)
#         loss = F.binary_cross_entropy_with_logits(out[data_flow.n_id[-1]], data.y[data_flow.n_id[-1]].to(device))
#         loss.backward()
#         optimizer.step()
#         total_loss += loss.item()
#     return total_loss / len(data.train_mask.nonzero(as_tuple=False))

















def test(mask):
	model.eval()
	correct = 0
	for data_flow in loader(mask):
		out = model(data.x.to(device), data_flow.to(device))
		pred = out.max(1)[1]
		pro  = F.softmax(out, dim=1)
		pro1 = pro.max(1)
		for i in range(len(data_flow.n_id)):
			pro[i][pro1[1][i]] = -1
		pro2 = pro.max(1)
		for i in range(len(data_flow.n_id)):
			if pro1[0][i]/pro2[0][i] < thre:
				pred[i] = 100
		correct += pred.eq(data.y[data_flow.n_id].to(device)).sum().item()
	return correct / mask.sum().item()

def final_test(mask):
	model.eval()
	correct = 0
	for data_flow in loader(mask):
		out = model(data.x.to(device), data_flow.to(device))
		pred = out.max(1)[1]
		pro  = F.softmax(out, dim=1)
		pro1 = pro.max(1)
		for i in range(len(data_flow.n_id)):
			pro[i][pro1[1][i]] = -1
		pro2 = pro.max(1)
		for i in range(len(data_flow.n_id)):
			if pro1[0][i]/pro2[0][i] < thre:
				pred[i] = 100
		for i in range(len(data_flow.n_id)):
			if data.y[data_flow.n_id[i]] != pred[i]:
				fp.append(int(data_flow.n_id[i]))
			else:
				tn.append(int(data_flow.n_id[i]))
		correct += pred.eq(data.y[data_flow.n_id].to(device)).sum().item()
	return correct / mask.sum().item()

def validate():
	global fp, tn
	global loader, device, model, optimizer, data

	show('Start validating')
	path = 'graphchi-cpp-master/graph_data/darpatc/' + args.scene + '_test.txt'
	data, feature_num, label_num, adj, adj2, nodeA, _nodeA, _neibor = MyDatasetA(path, 0)
	dataset = TestDatasetA(data)
	data = dataset[0]
	print(data)
	loader = NeighborSampler(data, sizes=[1, 1], num_hops=2, batch_size=b_size, shuffle=False, add_self_loops=True)
	device = torch.device('cpu')
	Net = SAGENet
# 	model1 = Net(feature_num, label_num).to(device)
	model1 = Net(dataset.num_features, dataset.num_classes).to(device)
	model = model1
	optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
	fp = []
	tn = []

	out_loop = -1
	while(1):
		out_loop += 1
		print('validating in model ', str(out_loop))
		model_path = 'models/model_'+str(out_loop)
		if not osp.exists(model_path): break
		model.load_state_dict(torch.load(model_path))
		fp = []
		tn = []
		auc = final_test(data.test_mask)
		print('fp and fn: ', len(fp), len(tn))
		_fp = 0
		_tp = 0
		eps = 1e-10
		tempNodeA = {}
		for i in nodeA:
			tempNodeA[i] = 1
		for i in fp:
			if not i in _nodeA:
				_fp += 1
			if not i in _neibor.keys():
				continue
			for j in _neibor[i]:
				if j in tempNodeA.keys():
					tempNodeA[j] = 0
		for i in tempNodeA.keys():
			if tempNodeA[i] == 0:
				_tp += 1
		print('Precision: ', _tp/(_tp+_fp))
		print('Recall: ', _tp/len(nodeA))
		if (_tp/len(nodeA) > 0.8) and (_tp/(_tp+_fp+eps) > 0.7):
			while (1):
				out_loop += 1
				model_path = 'models/model_'+str(out_loop)
				if not osp.exists(model_path): break
				print("123")
# 				os.system('rm ../models/model_'+str(out_loop))
# 				os.system('rm ../models/tn_feature_label_'+str(graphId)+'_'+str(out_loop)+'.txt')
# 				os.system('rm ../models/fp_feature_label_'+str(graphId)+'_'+str(out_loop)+'.txt')
			return 1
		if (_tp/len(nodeA) <= 0.8):
			return 0
		for j in tn:
			data.test_mask[j] = False

	return 0

from torch_geometric.utils import add_self_loops
edge_index_with_self_loops, _ = add_self_loops(data.edge_index)

def train_pro():
	global data, nodeA, _nodeA, _neibor, b_size, feature_num, label_num, graphId
	global model, loader, optimizer, device, fp, tn, loop_num
	os.system('python setup.py')
	path = 'graphchi-cpp-master/graph_data/darpatc/' + args.scene + '_train.txt'
	graphId = 0
	show('Start training graph ' + str(graphId))
	data1, feature_num, label_num, adj, adj2 = MyDataset(path, 0)
	dataset = TestDataset(data1)
	data = dataset[0]
	print(data)
	print('feature ', feature_num, '; label ', label_num)
	edge_index_with_self_loops, _ = add_self_loops(data.edge_index)
# 	loader = NeighborSampler(data, sizes=[1.0, 1.0], num_hops=2, batch_size=b_size, shuffle=False, add_self_loops=True)
	loader = NeighborSampler(data.edge_index, sizes=[1, 1], batch_size=b_size, shuffle=False)
	#loader = NeighborSampler(data, sizes=[1.0, 1.0], num_hops=2, batch_size=b_size, shuffle=False, add_self_loops=True)
	#loader = NeighborSampler(data.edge_index, sizes=[1.0, 1.0], num_hops=2, batch_size=b_size, shuffle=False, add_self_loops=True)

###############################
# def train_pro():
# 	global data, nodeA, _nodeA, _neibor, b_size, feature_num, label_num, graphId
# 	global model, loader, optimizer, device, fp, tn, loop_num
# 	os.system('python setup.py')
# 	path = 'graphchi-cpp-master/graph_data/darpatc/' + args.scene + '_train.txt'
# 	graphId = 0
# 	show('Start training graph ' + str(graphId))
# 	data1, feature_num, label_num, adj, adj2 = MyDataset(path, 0)
# 	dataset = TestDataset(data1)
# 	data = dataset[0]
# 	print(data)
# 	print('feature ', feature_num, '; label ', label_num)
# 	b_size = 512  # Define batch size
# 	loader = NeighborSampler(data.edge_index, sizes=[1, 1], batch_size=b_size, shuffle=False)



################################





	device = torch.device('cpu')
	Net = SAGENet
	model = Net(feature_num, label_num).to(device)
	optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

	for epoch in range(1, 30):
		loss = train()
		auc = test(data.test_mask)
		show(epoch, loss, auc)

	loop_num = 0
	max_thre = 3
	bad_cnt = 0
	while (1):
		fp = []
		tn = []
		auc = final_test(data.test_mask)
		if len(tn) == 0:
			bad_cnt += 1
		else:
			bad_cnt = 0
		if bad_cnt >= max_thre:
			break

		if len(tn) > 0:
			for i in tn:
				data.train_mask[i] = False
				data.test_mask[i] = False


			fw = open('models/fp_feature_label_'+str(graphId)+'_'+str(loop_num)+'.txt', 'w')
			x_list = data.x[fp]
			y_list = data.y[fp]
			print(len(x_list))

			if len(x_list) >1:
				sorted_index = np.argsort(y_list, axis = 0)
				x_list = np.array(x_list)[sorted_index]
				y_list = np.array(y_list)[sorted_index]

			for i in range(len(y_list)):
				fw.write(str(y_list[i])+':')
				for j in x_list[i]:
					fw.write(' '+str(j))
				fw.write('\n')
			fw.close()

			fw = open('models/tn_feature_label_'+str(graphId)+'_'+str(loop_num)+'.txt', 'w')
			x_list = data.x[tn]
			y_list = data.y[tn]
			print(len(x_list))

			if len(x_list) >1:
				sorted_index = np.argsort(y_list, axis = 0)
				x_list = np.array(x_list)[sorted_index]
				y_list = np.array(y_list)[sorted_index]

			for i in range(len(y_list)):
				fw.write(str(y_list[i])+':')
				for j in x_list[i]:
					fw.write(' '+str(j))
				fw.write('\n')
			fw.close()
			torch.save(model.state_dict(),'models/model_'+str(loop_num))
			loop_num += 1
			if len(fp) == 0: break
		auc = 0
		for epoch in range(1, 150):
			loss = train()
			auc = test(data.test_mask)
			show(epoch, loss, auc)
			if loss < 1: break
	show('Finish training graph ' + str(graphId))

def main():
	global b_size, args, thre
	parser = argparse.ArgumentParser()
	parser.add_argument('--model', type=str, default='SAGE')
	parser.add_argument('--scene', type=str, default='theia')
	args = parser.parse_args()
	assert args.model in ['SAGE']
	assert args.scene in ['cadets','trace','theia','fivedirections']
	b_size = 5000
	thre = thre_map[args.scene]
	os.system('cp groundtruth/'+args.scene+'.txt groundtruth_uuid.txt')
	while (1):
		train_pro()
		flag = validate()
		if flag == 1:
			break
		else:
			print("Done")
			os.system('rm ../models/model_*')
			os.system('rm ../models/tn_feature_label_*')
			os.system('rm ../models/fp_feature_label_*')

if __name__ == "__main__":
	graphchi_root = os.path.abspath(os.path.join(os.getcwd(), 'graphchi-cpp-master'))
	os.environ['GRAPHCHI_ROOT'] = graphchi_root

	main()

import argparse
import sys

sys.argv = ['train_darpatc.py', '--graphchi_root', '/path/to/graphchi', '--model', 'SAGE', '--scene', 'theia']

def main():
    global b_size, args, thre
    parser = argparse.ArgumentParser()
    parser.add_argument('--graphchi_root', type=str, default='')
    parser.add_argument('--model', type=str, default='SAGE')
    parser.add_argument('--scene', type=str, default='theia')
    args = parser.parse_args()
    assert args.model in ['SAGE']
    assert args.scene in ['cadets','trace','theia','fivedirections']
    b_size = 5000
    thre = thre_map[args.scene]
    os.environ['GRAPHCHI_ROOT'] = args.graphchi_root
    os.system('cp groundtruth/'+args.scene+'.txt groundtruth_uuid.txt')
    while (1):
        train_pro()
        flag = validate()
        if flag == 1:
            break
        else:
            print("Done")

if __name__ == "__main__":
    main()



