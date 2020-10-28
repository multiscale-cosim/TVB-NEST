import numpy as np
from timer.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import copy
from matplotlib.path import Path
import matplotlib.patches as patches
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def print_data_time(data_time, id_TR_N_to_T, id_TR_T_to_N):
    # https://github.com/w-klijn/cascaded_exploding_bar_chart
    space_legend = 0.2
    names = []
    handles = []
    legend = []
    plt.figure(figsize=(20,8))
    # nest (position : 1 )
    data_nest = []
    data_nest_name = []
    for i in data_time.get('Nest').child:
        data_nest.append(i.time)
        data_nest_name.append('Nest: '+i.name)
    data_nest = np.cumsum(data_nest)
    handles_nest = []
    for times in np.flip(data_nest):
        bar=plt.bar(1,times)
        handles_nest.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
    data_nest_name.reverse()
    names += data_nest_name
    handles += handles_nest
    legend.append(plt.legend(handles_nest,data_nest_name,bbox_to_anchor=(0., -0.05), loc='upper left'))


    # TVB ( position : 2 )
    data_tvb = []
    data_tvb_name = []
    for i in data_time.get('TVB').child:
        data_tvb.append(i.time)
        data_tvb_name.append('TVB: '+i.name)
    data_tvb = np.cumsum(data_tvb)
    handles_tvb = []
    for times in np.flip(data_tvb):
        bar = plt.bar(2,times)
        handles_tvb.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
    data_tvb_name.reverse()

    data_tvb_sim = []
    data_tvb_sim_name =[]
    tvb = data_time.get('TVB')
    for i in tvb.get('simulation').child:
        data_tvb_sim.append(i.time)
        data_tvb_sim_name.append('TVB sim:'+i.name)
    data_tvb_sim = np.cumsum(data_tvb_sim) + data_tvb[tvb.get_position('simulation')-len(data_tvb)-1]
    handles_tvb_sim = []
    for times in np.flip(data_tvb_sim):
        bar = plt.bar(2,times,width=0.6)
        handles_tvb_sim.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
    data_tvb_sim_name.reverse()
    handles_tvb += handles_tvb_sim
    data_tvb_name += data_tvb_sim_name

    data_tvb_sim_rec = []
    data_tvb_sim_rec_name =[]
    tvb_sim = data_time.get('TVB').get('simulation')
    for i in tvb_sim.get('receive data').child:
        data_tvb_sim_rec.append(i.time)
        data_tvb_sim_rec_name.append('TVB sim receive: '+i.name)
    if tvb_sim.get_position('receive data') == 0:
        add = data_tvb[tvb.get_position('simulation')-len(data_tvb)-1]
    else:
        add = data_tvb[tvb_sim.get_position('receive data')-len(data_tvb)-1]
    data_tvb_sim_rec = np.cumsum(data_tvb_sim_rec) + add
    handles_tvb_sim_rec = []
    for times in np.flip(data_tvb_sim_rec):
        bar = plt.bar(2,times,width=0.6)
        handles_tvb_sim_rec.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
    data_tvb_sim_rec_name.reverse()
    handles_tvb += handles_tvb_sim_rec
    data_tvb_name += data_tvb_sim_rec_name

    names += data_tvb_name
    handles += handles_tvb
    legend.append(plt.legend(handles_tvb,data_tvb_name,bbox_to_anchor=(space_legend, -0.05), loc='upper left'))


    # Translator TVB to Nest
    for index_tr,nb_TR in enumerate(id_TR_T_to_N):
        data_TR = []
        data_TR_name = []
        for i in data_time.get('Translation TVB to Nest '+str(index_tr)).child:
            data_TR.append(i.time)
            data_TR_name.append('TR T to N '+str(nb_TR)+': '+i.name)
        data_TR = np.cumsum(data_TR)
        handles_TR = []
        for times in np.flip(data_TR):
            bar = plt.bar(3+index_tr,times)
            handles_TR.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
        data_TR_name.reverse()

        data_TR_send = []
        data_TR_send_name = []
        TR_sim = data_time.get('Translation TVB to Nest '+str(index_tr)).get('simulation')
        for i in TR_sim.get('send thread').child:
            data_TR_send.append(i.time)
            data_TR_send_name.append('TR T to N '+str(nb_TR)+' send : '+i.name)
        data_TR_send = np.cumsum(data_TR_send) + data_TR[0]
        handles_TR_send = []
        for times in np.flip(data_TR_send):
            bar = plt.bar(2.8+index_tr,times,width=0.4)
            handles_TR_send.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
        data_TR_send_name.reverse()
        data_TR_name += data_TR_send_name
        handles_TR += handles_TR_send

        data_TR_receive = []
        data_TR_receive_name = []
        TR_sim = data_time.get('Translation TVB to Nest '+str(index_tr)).get('simulation')
        for i in TR_sim.get('receive thread').child:
            data_TR_receive.append(i.time)
            data_TR_receive_name.append('TR T to N '+str(nb_TR)+' receive : '+i.name)
        data_TR_receive = np.cumsum(data_TR_receive) + data_TR[0]
        handles_TR_receive = []
        for times in np.flip(data_TR_receive):
            bar = plt.bar(3.2+index_tr,times,width=0.4)
            handles_TR_receive.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
        data_TR_receive_name.reverse()
        data_TR_name += data_TR_receive_name
        handles_TR += handles_TR_receive


        names += data_TR_name
        handles += handles_TR
        legend.append(plt.legend(handles_TR,data_TR_name,bbox_to_anchor=((index_tr+2)*space_legend, -0.05), loc='upper left'))




    for index_tr,nb_TR in enumerate(id_TR_N_to_T):
        data_TR = []
        data_TR_name = []
        for i in data_time.get('Translation Nest to TVB '+str(index_tr)).child:
            data_TR.append(i.time)
            data_TR_name.append('TR N to T '+str(nb_TR)+': '+i.name)
        data_TR = np.cumsum(data_TR)
        handles_TR = []
        for times in np.flip(data_TR):
            bar = plt.bar(3+len(id_TR_T_to_N)+index_tr,times)
            handles_TR.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
        data_TR_name.reverse()

        data_TR_send = []
        data_TR_send_name = []
        TR_sim = data_time.get('Translation Nest to TVB '+str(index_tr)).get('simulation')
        for i in TR_sim.get('send thread').child:
            data_TR_send.append(i.time)
            data_TR_send_name.append('TR T to N '+str(nb_TR)+' send : '+i.name)
        data_TR_send = np.cumsum(data_TR_send) + data_TR[0]
        handles_TR_send = []
        for times in np.flip(data_TR_send):
            bar = plt.bar(2.8+len(id_TR_T_to_N)+index_tr,times,width=0.4)
            handles_TR_send.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
        data_TR_send_name.reverse()
        data_TR_name += data_TR_send_name
        handles_TR += handles_TR_send

        data_TR_receive = []
        data_TR_receive_name = []
        TR_sim = data_time.get('Translation Nest to TVB '+str(index_tr)).get('simulation')
        for i in TR_sim.get('receive thread').child:
            data_TR_receive.append(i.time)
            data_TR_receive_name.append('TR T to N '+str(nb_TR)+' receive : '+i.name)
        data_TR_receive = np.cumsum(data_TR_receive) + data_TR[0]
        handles_TR_receive = []
        for times in np.flip(data_TR_receive):
            bar = plt.bar(3.2+len(id_TR_T_to_N)+index_tr,times,width=0.4)
            handles_TR_receive.append(plt.Rectangle((0,0),1,1, color=bar[0].get_facecolor()))
        data_TR_receive_name.reverse()
        data_TR_name += data_TR_receive_name
        handles_TR += handles_TR_receive


        names += data_TR_name
        handles += handles_TR
        legend.append(plt.legend(handles_TR,data_TR_name,bbox_to_anchor=((index_tr+2+len(id_TR_T_to_N))*space_legend, -0.05), loc='upper left'))

    # plt.legend(handles,names,bbox_to_anchor=(1.05, 1), loc='upper left')
    for leg in legend:
        plt.gca().add_artist(leg)
    plt.subplots_adjust(left=0.1,right=0.8)
    plt.show()

def print_tree_data(data_time, id_TR_N_to_T, id_TR_T_to_N):
    # https://github.com/w-klijn/cascaded_exploding_bar_chart
    # nest (position : 1 )

    values = []
    labels = []
    parents = []
    values_nest,labels_nest, parents_nest = data_time.get('Nest').to_array_for_print()
    values.append(values_nest)
    labels.append(labels_nest)
    parents.append(parents_nest)
    values_tvb,labels_tvb, parents_tvb = data_time.get('TVB').to_array_for_print()
    values.append(values_tvb)
    labels.append(labels_tvb)
    parents.append(parents_tvb)
    for index_tr, i in enumerate(id_TR_N_to_T):
        TR = data_time.get('Translation<br>Nest to TVB '+str(index_tr))
        values_TR,labels_TR, parents_TR = TR.to_array_for_print()
        values.append(values_TR)
        labels.append(labels_TR)
        parents.append(parents_TR)

    for index_tr, i in enumerate(id_TR_T_to_N):
        TR = data_time.get('Translation<br>TVB to Nest '+str(index_tr))
        values_TR,labels_TR, parents_TR = TR.to_array_for_print()
        values.append(values_TR)
        labels.append(labels_TR)
        parents.append(parents_TR)

    for labels_sim in labels:
        if np.unique(labels_sim).shape[0] != len(labels_sim):
            count = np.unique(labels_sim,return_counts=True)[1]
            print(np.array(np.unique(labels_sim))[np.where(count!=1)])
            raise Exception('error label not unique in : '+str(labels_sim))

    nb_element = len(labels)
    fig = make_subplots(
    rows = 1, cols = nb_element,
    column_widths = np.repeat([1/nb_element],nb_element).tolist(),
    specs = [np.repeat([{'type': 'treemap', 'rowspan': 1}],nb_element).tolist()],
    vertical_spacing=0.1,
    horizontal_spacing=0.0001,
    )
    for i in range(nb_element):
        trace = go.Treemap(
        labels = labels[i],
        values = values[i],
        parents = parents[i],
        branchvalues='total',
        textinfo = "label+value+percent entry",
        )
        trace.marker.pad.update({'t':70.0})
        fig.add_trace(trace, col = i+1, row = 1)

    fig.update_layout(height=1100, width=1800, title_text="Simulation 10000 neurons MPI=8 time_syn=3.5",uniformtext_minsize=50,font={'size':40})
    fig.update_layout(uniformtext = dict(minsize = 20,mode= 'hide'))
    fig.show()

    # value_root = 0.0
    # values_all = []
    # labels_all = []
    # parents_all=[]
    # for i in values:
    #     value_root += i[0]
    #     values_all +=i
    # for i in labels:
    #     labels_all+=i
    # for i in parents:
    #     i[0]='root'
    #     parents_all+=i
    # values_all.insert(0,value_root)
    # labels_all.insert(0,'root')
    # parents_all.insert(0,'')
    #
    # fig_all = go.Figure(
    #     go.Treemap(
    #     labels = labels_all,
    #     values = values_all,
    #     parents = parents_all,
    #     branchvalues='total',
    #
    #     ),
    # )
    # fig_all.show()



if __name__ == '__main__':
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/10000_7/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/8/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/3.5/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_1/5/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_1/delay_vp/10/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_2/delay_vp/1000/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_3/delay_vp/1000/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_4/delay_vp/1000/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_5/delay_vp/1000/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_6/delay_vp/10000/_g_1.0_mean_I_ext_0.0/')
    # dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_7/delay_vp/10000/_g_1.0_mean_I_ext_0.0/')
    dict_time, index = get_dictionnary('/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/test_8/delay_vp/10000/_g_1.0_mean_I_ext_0.0/')
    # print_data_time(dict_time,index[0],index[1])
    print_tree_data(dict_time,index[0],index[1])
    print('end')
