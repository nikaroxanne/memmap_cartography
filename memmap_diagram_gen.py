#!/bin/python3
import os, sys
import argparse
import graphviz

mem=graphviz.Digraph('ivt-mem', filename='ivt-mem-graph.gv',
                     node_attr={'shape':'record', 'style':'filled',
                                'fillcolor':'green:pink', 'fontsize':'24', 
                                'fontname':'Fixedsys', 'fontweight':'12'})
mem.attr(bgcolor='black', style='filled', 
         label='Interrupt Vector Table and Interrupt Service Routines', 
         fontcolor='white', fontsize='30', fontname='Fixedsys', rankdir='LR')
mem.format = 'svg'


range_start=(0,12)
range_mid=(33,37)
range_end=(253,256) ##end of IVT, entries 0xFD-0xFF

ivtnodename_entries_0=[0] * range_start[1]
ivtnodename_entries_1=[0] * (range_mid[1]-range_mid[0])
ivtnodename_entries_2=[0] * (range_end[1]-range_end[0])

def generate_ivtnodenames(rangevals, ivtnodename_entries,curr_f_index):
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


ivtnodename_composite_entries=[(range_start, ivtnodename_entries_0), 
                               (range_mid, ivtnodename_entries_1), 
                               (range_end, ivtnodename_entries_2)]

num_groups= len(ivtnodename_composite_entries)
final_ivtnodename_entries=[''] * num_groups
num_intermediate_entries= num_groups - 1
intermediate_ivtnodename_entries=[''] * num_intermediate_entries
current_f_index=0

for i,entry  in enumerate(ivtnodename_composite_entries):
    rangevals=entry[0]
    target_ivtnodenames=entry[1]
    final_ivtnodename_entries[i],maxval=generate_ivtnodenames(rangevals,target_ivtnodenames,current_f_index)
    current_f_index=maxval
    if i < num_intermediate_entries:
        intermediate_entry='|<f'+ f"{current_f_index:d}" +'>...|'
        intermediate_ivtnodename_entries[i]=intermediate_entry
    current_f_index+=1

ivtnodename_combined=[elem for sublist in list(zip(final_ivtnodename_entries,intermediate_ivtnodename_entries)) for elem in sublist]
ivtnodename_combined += [final_ivtnodename_entries[num_intermediate_entries]]
ivtnodename_final=[item for sublist in ivtnodename_combined for item in sublist]
final_ivt_nodename_composite=''.join(str(elem) for elem in ivtnodename_combined)

with mem.subgraph(name='IVT') as ivt:
    ivt.node('IVT', final_ivt_nodename_composite)
    ivt.node_attr.update(size='12')
    ivt.attr(label='Interrupt Vector Table') 

for i in range(5):
    labeltext='ISR \[INT '+f"{i:02x}"+'\]'
    nodename='ISR-'+f"{i:02x}"
    ivtsourcenode='IVT:f'+f"{i:d}"
    mem.node(nodename, label=labeltext, style='filled', fillcolor='lightblue:violet')
    mem.edge(ivtsourcenode,nodename)
    mem.edge_attr.update(style='filled', fillcolor='pink', weight='10', color='pink')

if __name__=='__main__':
    mem.view()
    mem.render()

