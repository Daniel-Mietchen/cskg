import sys
sys.path.append('../')
from extraction import config
import json
import pandas as pd
import os
from kgtk.cskg_utils import collapse_identical_nodes, deduplicate_with_transformations
from shutil import copyfile

def normalize_dicts(d):
	new_d={}
	d=eval(d)
	for ad in d:
		elem=eval(ad)
		if type(elem)==list:
			for e in elem:
				for k,v in e.items():
					new_d[k]=v
		else:
			for k,v in elem.items():
				new_d[k]=v
	return new_d

def normalize_rows(nodes):
	new_rows=[]
	err_num=0
	for i, row in nodes.iterrows():
		all_labels=row['label'].split(',') + row['aliases'].split(',')
		all_labels=list(set(all_labels))
		filtered=[s for s in all_labels if s]
		if len(filtered):
			main_label, *aliases=filtered
			row['label']=main_label
			row['aliases']=','.join(aliases)
		try:
			row['other']=normalize_dicts(row['other'])
		except:
			row['other']={}
			err_num+=1
		new_rows.append(row)
		if i%100000==0: print('processed', i)
	print('Errors', err_num)
	return pd.DataFrame(new_rows, columns=config.nodes_cols)

VERSION=config.VERSION
cskg_dir='../output_v%s/cskg-refined' % VERSION
output_merged_dir='../output_v%s/cskg' % VERSION

cskg_nodes_file='%s/nodes_v%s.csv' % (cskg_dir, VERSION)
merged_nodes_file='%s/nodes.tsv' % output_merged_dir

cskg_edges_file='%s/edges_v%s.csv' % (cskg_dir, VERSION)
merged_edges_file='%s/edges.tsv' % output_merged_dir


copyfile(cskg_edges_file, merged_edges_file)

exit(0)

if not os.path.exists(output_merged_dir):
    os.makedirs(output_merged_dir)

nodes_df=pd.read_csv(cskg_nodes_file, sep='\t', header=0, converters={5: eval}, na_filter=False)

NODE_COLS=config.nodes_cols
for c in NODE_COLS:
    nodes_df[c]=nodes_df[c].astype('str')

nodes_df=normalize_rows(nodes_df)
nodes_df.sort_values('id').to_csv(merged_nodes_file, index=False, sep='\t')
