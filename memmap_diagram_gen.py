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
    out_filename: str = ""
    node_info: Optional = ()
    label: Optional = ""
    mem=graphviz.Digraph('ivt-mem', filename=out_filename,format='png',
                 node_attr={'shape':'record', 'style':'filled',
                    'fillcolor':'green:pink', 'fontsize':'18', 
                    'fontname':'Fixedsys', 'fontweight':'12', 'padding':'10'})
    mem.attr(bgcolor='black', style='filled') 
    #mem.format = 'png'
    #def set_graph_attrs(node_info):
    #    for k,v in node_info.items():
    #        mem.attr(k=v)    

    @classmethod
    def from_input(cls, out_filename, nodeinfo, label):
        #info_new=[item[1] for item in info]
        return cls(out_filename, nodeinfo, label) 
    
    def add_node(self, nodeinfo, label):
        new_node=self.mem.node(name=nodeinfo, label=label)
#        self.mem.node_attr.update={'style':'filled', 'fillcolor':'lightblue:violet', 'width':'2'}
        return self.mem
    def add_edge(self, startnode, endnode):
        new_node=self.mem.edge(tail_name=startnode, head_name=endnode)
        self.mem.edge_attr.update(fontcolor='white', style='bold', weight='10', color='green')
        #new_node=self.mem.edge(tail_name=startnode, head_name=endnode, label=label)
       # self.mem.edge_attr={'style':'filled', 'fillcolor':'lightblue:violet', 'width':'2'}
        return self.mem
     
    def render(self):
        self.mem.render(outfile=self.out_filename)
        #self.mem.render(outfile=self.out_filename, format='png')
    
    def view(self):
        self.mem.view()
        #self.mem.view(outfile=self.out_filename)
        #return cls(output_filename, nodeinfo, label) 

def create_basic_graph(output_filename, jsonfile, node_info_list: Optional, node_labels: Optional):
    output_filename += '.png'
    print("output_filename: {0}".format(output_filename))
    graph_label="test_graph"    
    graph_info="test_graph"    
    if jsonfile == None:
        node_info = list(zip(node_info_list, node_labels))
        print("node_info: {0}".format(node_info))
        #output_filename += '.png'
        #print("output_filename: {0}".format(output_filename))
        #graph_label="test_graph"    
        #graph_info="test_graph"    
        graph_skeleton = Memmap_Entry.from_input(output_filename, graph_info, graph_label)
        graph_nodes = [[]] * len(node_info)
        print("graph_nodes: {0}".format(graph_nodes))
        for elem in node_info:
            print("elem {0}".format(elem))
            info=elem[0]
            label=elem[1]
            print("node_info: {0}, node_label: {1}".format(info,label))
            graph_with_node = graph_skeleton.add_node(info, label)
            #if graph_nodes != [] :
            #    graph_nodes.append(graph_node)
            #else:
            #    graph_nodes[0]=graph_node
            graph_skeleton.render()
            graph_skeleton.view()
    else:
        #graph_json={}
        graph_skeleton = Memmap_Entry.from_input(output_filename, graph_info, graph_label)
        with open(jsonfile, 'r') as j:
            try:
                graph_json=json.load(j)
                json_nodes=graph_json['Nodes']
                json_edges=graph_json['Edges']
                for node in json_nodes:
                    info=node['name']
                    label=node['label']
                    graph_with_node = graph_skeleton.add_node(info, label)
                for edge in json_edges:
                    startnode=edge['startnode']
                    endnode=edge['destnode']
                    #label=edge['label']
                    graph_with_edge = graph_skeleton.add_edge(startnode, endnode)
            except OSError as e:
                print(f"Error opening file: {0}", e)
    graph_skeleton.render()
    graph_skeleton.view()
    return graph_skeleton

def generate_nodenames(rangevals, ivtnodename_entries, curr_f_index):
    minval, maxval=rangevals[0], rangevals[1]
    maxval -= 1
    nodeentry_index=0
    i=minval
    f_index=curr_f_index
    while i <= maxval:
        ivtnodename_part='<f'+ f"{f_index:d}" +'>IVT\[' +f"{i:02X}" +'\]' + r"\n"
        if i < maxval:
            ivtnodename_part += '|'
        ivtnodename_entries[nodeentry_index]=str(ivtnodename_part)
        i+=1
        nodeentry_index += 1
        f_index += 1
    
    ivt_nodename_composite=''.join(str(elem) for elem in ivtnodename_entries)
    return ivt_nodename_composite, f_index


def generate_memmap(output_filename, idx_ranges: Optional, node_labels: Optional):
    mem=graphviz.Digraph('ivt-mem', filename=output_filename,
                 node_attr={'shape':'record', 'style':'filled',
                    'fillcolor':'green:pink', 'fontsize':'18', 
                    'fontname':'Fixedsys', 'fontweight':'12', 'padding':'10'})
    mem.attr(bgcolor='black', style='filled', 
#         label='Interrupt Vector Table and Interrupt Service Routines', 
         label=r'\n\nModifying control flow of Interrupt Service Routines by hooking the IVT with a TSR', 
#         label=r'\n\nTypical code flow of executing an Interrupt Service Routine\n on MS-DOS by invoking a system call', 
         fontcolor='white', fontsize='24', fontname='Fixedsys')
#         fontcolor='white', fontsize='30', fontname='Fixedsys', rankdir='LR')
    #mem.format = 'svg'
    mem.format = 'png'
    #mem.format = 'jpeg'

    intcallingnode='INT 21h call'
    mem.node(intcallingnode, label=intcallingnode, style='filled', fillcolor='lightblue:violet', shape='Mdiamond')

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
    #                   (range_mid, ivtnodename_entries_1), 
    #                   (range_end, ivtnodename_entries_2)]

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
        #ivt.node_attr.update(fixedsize='true', width='1.2')
        ivt.attr(label='Interrupt Vector Table', style='filled', fillcolor='green:pink', fontsize="16", width='4') 

    targetint=33
    #targetint_hex=int(33, 16)
    labeltext='ISR \[INT '+f"{targetint:02x}"+'\]'
    isrnodename='ISR-'+f"{targetint:02x}"
    isrnodelabel='ISR INT '+f"{targetint:02x}"+'h'
    ivtindexnum=targetint-1
    #ivtsourcenode='IVT:f5'
    ivtsourcenode='IVT:f0'
    #ivtsourcenode='IVT:f' + f"{targetint:0x}"
    ivtlabeltext='IVT \[INT '+f"{targetint:02x}"+'\]'
#    mem.node(isrsourcenode, label=ivtlabeltext, style='filled', fillcolor='lightblue:violet')
    mem.node(isrnodename, label=isrnodelabel, style='filled', fillcolor='lightblue:violet', width="2")
    mem.edge(intcallingnode, ivtsourcenode,label=r'System call, \njumps to INT21h IVT entry',fontcolor='white', fontsize='16', fontname='Fixedsys')
    #ivtsourcenode='IVT:f'+f"{ivtindexnum:d}"
#    mem.edge(ivtsourcenode,isrnodename, label='Jump to address of\n INT 21h ISR \n(retrieved from IVT),\n execute ISR',fontcolor='white', fontsize='16', fontname='Fixedsys')
    
    

    ##TSR Hook nodes + edges
    vxint21hook=r'TSR INT 21h hook routine'
    vxint21hooklabel=r'TSR INT 21h\n hook routine:\n checks INT 21h params\n for call to\nsubfunction 4B (EXEC)'
    vxint21isr='TSR ISR'
    mem.node(vxint21hook, label=vxint21hooklabel, style='filled', fillcolor='violet:red', shape='Msquare')
    mem.node(vxint21isr, label=vxint21isr, style='filled', fillcolor='violet:red', shape='Msquare')
#
    mem.edge(ivtsourcenode, vxint21hook, label='INT21 hook',fontcolor='white', fontsize='16', fontname='Fixedsys', style='bold', color='red')
    mem.edge(vxint21hook,vxint21isr, label='Condition met, jump to new ISR',fontcolor='white', fontsize='16', fontname='Fixedsys', style='bold', color='red')
    mem.edge(vxint21hook,isrnodename, label=r'Condition not met,\n jump to saved address \nof original INT 21h ISR',fontcolor='white', fontsize='16', fontname='Fixedsys')
    mem.edge(vxint21isr,isrnodename, label=r'Jump back to saved address \nof original INT 21h ISR',fontcolor='white', fontsize='16', fontname='Fixedsys', style='bold', color='red')
    mem.edge(isrnodename, intcallingnode, label=r'Return to calling function \nafter execution of ISR chain',fontcolor='white', fontsize='16', fontname='Fixedsys')
    
#    mem.edge(isrnodename, intcallingnode, label=r'Return to calling function \nafter execution of ISR',fontcolor='white', fontsize='16', fontname='Fixedsys')
    mem.edge_attr.update(style='bold', weight='10', color='green')
#
#    for i in range(33,34):
#        labeltext='ISR \[INT '+f"{i:02x}"+'\]'
#        nodename='ISR-'+f"{i:02x}"
#        ivtsourcenode='IVT:f'+f"{i:d}"
#        intcallingnode='IVT:f'+f"{i:d}"
#        mem.node(nodename, label=labeltext, style='filled', fillcolor='lightblue:violet')
#        mem.edge(ivtsourcenode,nodename)
#        mem.edge_attr.update(style='filled', fillcolor='pink', weight='10', color='pink')
    return mem

################################################################################################################
#        Argparse template - more detailed/fine-grained command line controls
#
################################################################################################################

def setup_options():
    parser = argparse.ArgumentParser(description='A utility for creating aesthetic data visualizations/diagrams of memory maps')
    parser.add_argument('-filename', nargs=1, type=str, help='Filename of output SVG image file generated by this script')
    parser.add_argument('-ranges', nargs='?', type=int_range, help='A list of one or more strings of integer ranges (i.e. memory addresses), each entry of which follows the format "start-range, end-range" where startrange and endrange are both integers')
    parser.add_argument('-labels', nargs='+', type=str, help='A list of one or more strings of labels for graph nodes; each entry of which is a raw string which will be printed as the node label on the final graph')
    parser.add_argument('-info', nargs='+', type=str, help='A list of one or more strings of information corresponding to the attributes of graph nodes; each entry of which contains strings for the following values: fontcolor, fontsize, fontname, style, weight, color')
    parser.add_argument('-jsonfile', nargs='?', type=str, help='A JSON file with definitions for graph nodes and edges')
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
    else:
        mem_ranges=None
    if args.labels:    
        node_labels=args.labels
    if args.info:    
        node_info=args.info
    if args.jsonfile:    
        jsonfile=args.jsonfile
    else:
        jsonfile=None
    mem=create_basic_graph(outfile, jsonfile, node_info, node_labels)
    #mem=generate_memmap(outfile, mem_ranges, node_labels)
#    mem.view()
#    mem.render()

