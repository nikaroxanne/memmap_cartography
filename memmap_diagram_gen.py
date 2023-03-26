#!/usr/bin/python

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
    #for i in range(minval, maxval):
        #f_index=curr_f_index+i
        ivtnodename_part='<f'+ f"{f_index:d}" +'>IVT\[' +f"{i:02X}" +'\]'
        if i < maxval:
            ivtnodename_part += '|'
        #elif i == maxval:
        #    ivtnodename_part += '>'
        ivtnodename_entries[nodeentry_index]=str(ivtnodename_part)
        print("IVT Nodename entry at index {0}: {1}".format(i,ivtnodename_part))
        i+=1
        nodeentry_index += 1
        f_index += 1
    ivt_nodename_composite=''.join(str(elem) for elem in ivtnodename_entries)
    print("IVT Nodename composite: {0}".format(ivt_nodename_composite))
    return ivt_nodename_composite, f_index




#print("IVT Nodename entries initial: {0}".format(ivtnodename_entries))
#ivtnodename_entries[0]='<f0>IVT\[00h\]|'
#print("IVT Nodename entries, with first entry: {0}".format(ivtnodename_entries))
ivtnodename_composite_entries=[(range_start, ivtnodename_entries_0), 
                               (range_mid, ivtnodename_entries_1), 
                               (range_end, ivtnodename_entries_2)]

num_groups= len(ivtnodename_composite_entries)
print("number of nodename groups: {0}".format(num_groups))
final_ivtnodename_entries=[''] * num_groups
num_intermediate_entries= num_groups - 1
print("number of intermediate entries: {0}".format(num_intermediate_entries))
intermediate_ivtnodename_entries=[''] * num_intermediate_entries
print("Intermediate IVT Nodename entries: {0}".format(intermediate_ivtnodename_entries))
current_f_index=0
for i,entry  in enumerate(ivtnodename_composite_entries):
    print("value of i, index in ivtnodename_composite_entries list: {0}".format(i))
    print("current_f_index: {0}".format(current_f_index))
    rangevals=entry[0]
    target_ivtnodenames=entry[1]
    #ivtnodename_entries_0[0]='<f0>IVT\[00h\]|'
    final_ivtnodename_entries[i],maxval=generate_ivtnodenames(rangevals,target_ivtnodenames,current_f_index)
    print("IVT Nodename entries group: {0}".format(final_ivtnodename_entries[i]))
    current_f_index=maxval
    print("current_f_index: {0}".format(current_f_index))
    if i < num_intermediate_entries:
        intermediate_entry='|<f'+ f"{current_f_index:d}" +'>...|'
        #current_f_index+=1
        #intermediate_entry_end='<f'+ f"{current_f_index:d}" +'>|'
        #intermediate_ivtnodename_entries[i]=''.join((intermediate_entry_start, intermediate_entry_end))
        intermediate_ivtnodename_entries[i]=intermediate_entry
        print("Intermediate IVT Nodename: {0}".format(intermediate_ivtnodename_entries[1]))
    current_f_index+=1
    #current_f_index=maxval+1

ivtnodename_combined=[elem for sublist in list(zip(final_ivtnodename_entries,intermediate_ivtnodename_entries)) for elem in sublist]
#list((a,b) for a,b in final_ivtnodename_entries[i],intermediate_ivtnodename_entries[i] for i in range(num_intermediate_entries)) 
ivtnodename_combined += [final_ivtnodename_entries[num_intermediate_entries]]
ivtnodename_final=[item for sublist in ivtnodename_combined for item in sublist]
#print("zipped IVT nodename list: {0}".format(ivtnodename_combined))
#print("final IVT nodename list: {0}".format(ivtnodename_final))
final_ivt_nodename_composite=''.join(str(elem) for elem in ivtnodename_combined)
print("final IVT Nodename composite: {0}".format(final_ivt_nodename_composite))


with mem.subgraph(name='IVT') as ivt:
    #ivt.node('IVT', '<f0>IVT\[00h\]|<f1>IVT\[01h\]|<f2>IVT\[02h\]|<f3>IVT\[03h\]|<f4>IVT\[04h\]|<f5>...|<f6>IVT\[FFh\]')
    ivt.node('IVT', final_ivt_nodename_composite)
    ivt.node_attr.update(size='12')
    ivt.attr(label='Interrupt Vector Table') 

for i in range(5):
    labeltext='ISR \[INT '+f"{i:02x}"+'\]'
    nodename='ISR-'+f"{i:02x}"
    ivtsourcenode='IVT:f'+f"{i:d}"
    print("labeltext at index {0}: {1}".format(i, labeltext))
    print("nodename at index {0}: {1}".format(i, nodename))
    mem.node(nodename, label=labeltext, style='filled', fillcolor='lightblue:violet')
    mem.edge(ivtsourcenode,nodename)
    mem.edge_attr.update(style='filled', fillcolor='pink', weight='10', color='pink')
#mem.node('ISR-0', label='ISR[INT 00h]', style='filled', fillcolor='lightblue:violet')
#mem.edge('IVT:f0','ISR-0')
#mem.node('ISR-1', label='ISR[INT 01h]')
#mem.edge('IVT:f1','ISR-1')
#mem.node('ISR-2', label='ISR[INT 02h]')
#mem.edge('IVT:f2','ISR-2')
#mem.node('ISR-3', label='ISR[INT 03h]')
#mem.edge('IVT:f3','ISR-3')
#mem.node('ISR-4', label='ISR[INT 04h]')
#mem.edge('IVT:f4','ISR-4')

if __name__=='__main__':
    mem.view()
    mem.render()

