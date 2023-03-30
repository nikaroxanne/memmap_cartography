#!/bin/python3
import os, sys
import argparse
import graphviz
import re
import json
from dataclasses import dataclass
from typing import Optional

##############################################################################################
#   ralf2int.py - generates a composite JSON file of all MS-DOS interrupts
#
#   for other modules (i.e. r2_16bitCOM.py) that generate assembly analysis commands for r2
##############################################################################################

def int_range(input_str_tuple: str):
	input_str_tuple.replace("(", "").replace(")","")
	range_str=[int(elem) for elem in input_str_tuple.split(",")]
	return range_str


@dataclass
class Memmap_Entry:
    nodeinfo: str = ""
    label: Optional = ""

    @classmethod
    def from_opcodes(cls, nodeinfo, label):
        info_new=[item[1] for item in info]
        return cls(info_new) 



def generate_nodenames(rangevals, ivtnodename_entries, curr_f_index):
	minval, maxval=rangevals[0], rangevals[1]
	maxval -= 1
	nodeentry_index=0
	i=minval
	f_index=curr_f_index
	while i <= maxval:
		ivtnodename_part='<f'+ f"{f_index:d}" +'>IVT\[' +f"{i:02X}" +'\]'
		if i < maxval:
			ivtnodename_part += '|'
		ivtnodename_entries[nodeentry_index]=str(ivtnodename_part)
		i+=1
		nodeentry_index += 1
		f_index += 1
	
	ivt_nodename_composite=''.join(str(elem) for elem in ivtnodename_entries)
	return ivt_nodename_composite, f_index


def generate_memmap(output_filename, idx_ranges: Optional):
	mem=graphviz.Digraph('ivt-mem', filename=output_filename,
				 node_attr={'shape':'record', 'style':'filled',
					'fillcolor':'green:pink', 'fontsize':'24', 
					'fontname':'Fixedsys', 'fontweight':'12'})
	mem.attr(bgcolor='black', style='filled', 
		 label='Interrupt Vector Table and Interrupt Service Routines', 
		 fontcolor='white', fontsize='30', fontname='Fixedsys', rankdir='LR')
	#mem.format = 'svg'
	mem.format = 'png'
	#mem.format = 'jpeg'

	intcallingnode='INT 21h call'
	mem.node(intcallingnode, label=intcallingnode, style='filled', fillcolor='lightblue:violet')

	nodename_entries_total=[[]] * len(idx_ranges)
	nodename_composite_entries=[[]] * len(idx_ranges)
	for j,idx_range in enumerate(idx_ranges):
		nodename_entries_total[j]=[0] * (idx_range[1] - idx_range[0])
		nodename_composite_entries[j]=(idx_range, nodename_entries_total[j]) 
	#range_start=(0,1)
	#range_mid=(33,34)
	#range_end=(255,256) ##end of IVT, entries 0xFD-0xFF

	#ivtnodename_entries_0=[0] * range_start[1]
	#ivtnodename_entries_1=[0] * (range_mid[1]-range_mid[0])
	#ivtnodename_entries_2=[0] * (range_end[1]-range_end[0])

	#ivtnodename_composite_entries=[(range_start, ivtnodename_entries_0), 
	#				   (range_mid, ivtnodename_entries_1), 
	#				   (range_end, ivtnodename_entries_2)]

	num_groups= len(nodename_composite_entries)
	final_nodename_entries=[''] * num_groups
	num_intermediate_entries= num_groups - 1
	intermediate_nodename_entries=[''] * num_intermediate_entries
	current_f_index=0

	for i,entry  in enumerate(nodename_composite_entries):
		rangevals=entry[0]
		target_nodenames=entry[1]
		final_nodename_entries[i],maxval=generate_nodenames(rangevals,target_nodenames,current_f_index)
		current_f_index=maxval
		if i < num_intermediate_entries:
			intermediate_entry='|<f'+ f"{current_f_index:d}" +'>...|'
			intermediate_nodename_entries[i]=intermediate_entry
		current_f_index+=1

	nodename_combined=[elem for sublist in list(zip(final_nodename_entries,intermediate_nodename_entries)) for elem in sublist]
	nodename_combined += [final_nodename_entries[num_intermediate_entries]]
	nodename_final=[item for sublist in nodename_combined for item in sublist]
	final_ivt_nodename_composite=''.join(str(elem) for elem in nodename_combined)

	with mem.subgraph(name='IVT') as ivt:
		ivt.node('IVT', final_ivt_nodename_composite)
		ivt.node_attr.update(size='12')
		ivt.attr(label='Interrupt Vector Table') 

	targetint=33
	labeltext='ISR \[INT '+f"{targetint:02x}"+'\]'
	isrnodename='ISR-'+f"{targetint:02x}"
	isrnodelabel='ISR INT '+f"{targetint:02x}"+'h'
	ivtindexnum=targetint-1
	ivtsourcenode='IVT:f5'
	ivtlabeltext='IVT \[INT '+f"{targetint:02x}"+'\]'
#	mem.node(isrsourcenode, label=ivtlabeltext, style='filled', fillcolor='lightblue:violet')
	mem.edge(intcallingnode, ivtsourcenode,label='System call, jumps to INT21h IVT entry',fontcolor='white', fontsize='14', fontname='Fixedsys')
	#ivtsourcenode='IVT:f'+f"{ivtindexnum:d}"
	
	vxint21hook='TSR INT 21h hook'
	vxint21isr='TSR ISR'
	mem.node(vxint21hook, label=vxint21hook, style='filled', fillcolor='violet:red')
	mem.node(vxint21isr, label=vxint21isr, style='filled', fillcolor='violet:red')

	#mem.edge(ivtsourcenode,isrnodename, label='Jump to address of ISR (retrieved from IVT), execute ISR',fontcolor='white', fontsize='14', fontname='Fixedsys')
	mem.edge(ivtsourcenode, vxint21hook, label='INT21 hook',fontcolor='white', fontsize='14', fontname='Fixedsys')
	mem.edge(vxint21hook,vxint21isr, label='Condition met, jump to new ISR',fontcolor='white', fontsize='14', fontname='Fixedsys')
	mem.edge(vxint21hook,isrnodename, label='Condition not met,\n jump to address of saved original INT 21h ISR',fontcolor='white', fontsize='14', fontname='Fixedsys')
	mem.edge(vxint21isr,isrnodename, label='Jump back to saved address of original INT21 ISR',fontcolor='white', fontsize='14', fontname='Fixedsys')
	mem.edge(isrnodename, intcallingnode, label='Return to calling function after execution of ISR',fontcolor='white', fontsize='14', fontname='Fixedsys')
	mem.edge_attr.update(style='filled', fillcolor='pink', weight='10', color='pink')
#
#	for i in range(33,34):
#		labeltext='ISR \[INT '+f"{i:02x}"+'\]'
#		nodename='ISR-'+f"{i:02x}"
#		ivtsourcenode='IVT:f'+f"{i:d}"
#		intcallingnode='IVT:f'+f"{i:d}"
#		mem.node(nodename, label=labeltext, style='filled', fillcolor='lightblue:violet')
#		mem.edge(ivtsourcenode,nodename)
#		mem.edge_attr.update(style='filled', fillcolor='pink', weight='10', color='pink')
	return mem

################################################################################################################
#		Argparse template - more detailed/fine-grained command line controls
#
################################################################################################################

def setup_options():
	parser = argparse.ArgumentParser(description='A utility for creating aesthetic data visualizations/diagrams of memory maps')
	parser.add_argument('-filename', nargs=1, type=str, help='Filename of output SVG image file generated by this script')
	parser.add_argument('-ranges', nargs='+', type=int_range, help='A list of one or more strings of integer ranges (i.e. memory addresses), each entry of which follows the format "start-range, end-range" where startrange and endrange are both integers')
	args = parser.parse_args()
	return parser, args

################################################################################################################
#
################################################################################################################


if __name__ == '__main__':
	parser,args=setup_options()
	outfile=args.filename[0]
	outfile += "-memmap"
	if args.ranges:	
		mem_ranges=args.ranges
	mem=generate_memmap(outfile, mem_ranges)
	mem.view()
	mem.render()

