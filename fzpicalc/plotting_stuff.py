
import plotly.graph_objs as go
import plotly
import plotly.io as pio
import os
import numpy as np
import pandas as pd
from PIL import ImageFont
import ntpath
import math
import matplotlib.cm as cm
from fzpicalc.flow_type_cat_simpl import determine_main_flow_type_light
from fzpicalc.dwaf_el_scaling import result_sclaing
import fzpicalc.basic_func as basic_func
from fzpicalc.dwaf_el_scaling import scale_array

#calculate timesteps and times once:
t_list = [0.0,1.0]
dt=1
t=1
for i in range(125):
    dt=dt*1.1
    t+=dt
    t_list.append(t)
t_list.append(1.8e6)


def make_basic_text_annotation_from_dict(dikt,
                                         x=0.50,
                                         y=0.1,
                                         fontpath='./fzpicalc/FiraMono-Medium.otf'):
    
    names = dikt.keys()
    values = dikt.values()
    
    text = ''
    
    for val,name in zip(values,names):
        if isinstance(val, str) == True:
            text += str(name)+'='+val+'<br>'
        else:
            text += str(name)+'='+str(basic_func.tidy(val,3))+'<br>'
            
    an = dict(x=x,
              y=y,
              showarrow=False,
              text=text,
              bgcolor='rgb(255,255,255)',
              opacity=0.8,
              bordercolor='#000000',
              borderwidth=1,
              align='center',
              xref='paper',
              yref='paper',
              font =dict(family=fontpath, 
                         size=10, 
                         color='#000000'))
                         
    return an

def gen_xaxis_dict(title,typ='log',rang=[-14,-9], dtick=1,showticklabels=True,showgrid=True):
    xaxis =dict(
                title=title,
                titlefont=dict(
                        size=15
                        ),
                type=typ,
                showline=True,
                gridcolor='rgb(71,71,71)',
                linewidth=0.5,
                linecolor='#454545',
                showgrid=showgrid,
                mirror=True,
                zeroline=False,
                ticks='outside',
                showticklabels=showticklabels,
                tickcolor='#000000',
                autorange=False,
                range = rang, #log
                dtick = dtick,
                tickformat="g",
                tickfont=dict(
                        size=13
                        ),
                )
    return xaxis

def gen_yaxis_dict(title,typ='log',rang=[-17,-12], dtick=1,tickformat="1.2f",ticks='outside',showticklabels=True,showgrid=True):
    yaxis =dict(
                title=title,
                titlefont=dict(
                        size=15
                        ),
                type=typ,
                showline=True,
                gridcolor='rgb(71,71,71)',
                linewidth=0.5,
                linecolor='#454545',
                showgrid=showgrid,
                mirror=True,
                zeroline=False,
                ticks=ticks,
                showticklabels=showticklabels,
                tickcolor='#000000',
                autorange=False,
                range = rang, #log
                dtick = dtick,
                tickformat=tickformat,
                tickfont=dict(
                        size=13
                        ),
                )
    return yaxis

def saveplot_routine(fig,indv_plotname,plotdir,newfoldername,auto_open=True,pdf=False,png=False,html=True):
    #generating plot dir for semilog plots:

    if os.path.isdir(os.path.join(plotdir,newfoldername)) == False:
        os.mkdir(os.path.join(plotdir,newfoldername))
        print('directory '+newfoldername+' created')
    plotpath = os.path.join(plotdir,newfoldername)
    
    filename_html = indv_plotname + '.html'
    filename_png = indv_plotname + '.png'
    filename_pdf = indv_plotname + '.pdf'
    
    filenamepath = os.path.join(plotpath,filename_html)
    
    if html == True:
        plotly.offline.plot(fig, filename=filenamepath, auto_open=auto_open)
    if png == True:
        pio.write_image(fig, os.path.join(plotpath,filename_png))
    if pdf == True:
        pio.write_image(fig, os.path.join(plotpath,filename_pdf))





def layout_f_plotly(xaxis,
                    yaxis,
                    llegendword='insert lleg word',
                    width=1050,
                    height=1050,
                    annotations=[],
                    fontsize=13,
                    fontpath='./fzpicalc/FiraMono-Medium.otf'):
    font = ImageFont.truetype(fontpath, fontsize)
    size = font.getsize(llegendword)
    x = 1.0- (float(size[0])/width + 0.15)
    y = float(size[1])/height + 0.05
    layout=dict(font=dict(family=fontpath, 
                          size=fontsize, 
                          color='#000000'),
                width=width,
                height=height,
                showlegend=True,
                plot_bgcolor='rgb(255,255,255)',
                #paper_bgcolor='rgb(155,155,155)',
                legend=dict(x=x,
                            y=y,
                            tracegroupgap=20,
                            bgcolor='rgba(255,255,255,0.8)',
                            bordercolor='rgba(0,0,0,1.0)',
                            borderwidth=1),
                dragmode='pan',
                autosize=False)
    #append axes and annotations to dict:
    layout['annotations']=annotations
    layout['xaxis']=xaxis
    layout['yaxis']=yaxis
    
    return layout


def gen_axis_dict(title,typ,rang,dtick = 1,showticklabels=True,showgrid=True,tickformat=".2f"):
    axis =dict(
                title=title,
                titlefont=dict(
                        size=16
                        ),
                type=typ,
                showgrid=showgrid,
                mirror=True,
                showline=True,
                linecolor='rgb(0,0,0)',
                gridcolor='rgb(0,0,0)',
                ticks='outside',
                showticklabels=showticklabels,
                tickcolor='rgb(0,0,0)',
                autorange=False,
                range = rang, #log
                dtick = dtick,
                zeroline=False,
                tickformat=tickformat,
                tickfont=dict(
                        size=15
                        ),
                )
    return axis



def plot_pressure(ipath_arr,
                 SIparams_dict,
                 fthickness,
                 compare_annotation=True,
                 itype=['golem'],
                 additionaltrace=[],
                 optional_annotation=[],
                 DERplot=[False],
                 indv_plotname = 'semilog_plot',
                 newfoldername = 'error_plots',
                 plotdir = os.getcwd(),
                 xtyp='log',
                 xtitle='time [h]',
                 ytyp='log',
                 ytitle='dp [MPa]',
                 auto_open=True,
                 pdf=True,
                 png=False,
                 html=False,
                 fontpath='./fzpicalc/FiraMono-Medium.otf',
                 identifier='identifier_str'):
    
    '''
    
    input documentation:
        
    ipath_arr = list of path to csv or np.array
    SIparams_dict = list of dictionary of parametersetting in SI units and names like this:
        {'S_fault': 2e-12,
         'S_matrix': 2e-12,
         'k_fault': 1e-10,
         'k_matrix': 1e-13,
         'rate': 20,
         'visocisty': 0.00028974}
    fthickness = list of strings string containing fault zone thickness in meters eg. ['50']
    itype = list of Datasources: 
        Dwarfelephant online stage output array = 'rb' 
        Dwarfelephant single FE csv = 'rb_fe' 
        GOLEM = 'golem'
        tickcolor='rgb(0,0,0)'
    additionaltrace = any kind of trace that should be plotted additionally to input csv can be provided here
    DERplot = list of booleans, if True the DER curve will also be plotted
    plotdir = set directory in which a plotting folder will be saved with the plots inside
    
    example usage:
        
    pls.plot_pressure([RB_outputs,
                       '/home/hombre/Desktop/VGL/1_base_FZ_out.csv',
                       '/home/hombre/Desktop/VGL/1_base_FZ_nolengthscale_out.csv'],
                     [parm_dict,parm_dict,parm_dict],
                     ['100','50','50'],
                     itype=['rb','golem','golem'],
                     additionaltrace=[],
                     optional_annotation=[],
                     DERplot=[False,False,False],
                     indv_plotname = 'testing shit',
                     xtyp='log',
                     ytyp='linear',
                     plotdir = plotdir)
    
    '''
    #integrate input check for correct types here:
    
    
    
    
    
    
    
    #generating plotlabel and checking for differences:
    
    differences={}
    if compare_annotation == True:
        if len(SIparams_dict) > 1:
            #check if dics are the same:
            SIparams_dict_same = True
            
            for eachdict in SIparams_dict:
                if SIparams_dict[0] != eachdict:
                    SIparams_dict_same = False
                    #calculate differences in dictionaries
                    diff =  set(SIparams_dict[0].items()) ^ set(eachdict.items())
                    differences.update(diff)
            #check if fault thicknesses are the same:
            SIparams_fz_same = True
            for eachthickness in fthickness:
                if fthickness[0] != eachthickness:
                    SIparams_fz_same = False
                    
        
        if len(SIparams_dict) == 1:
            parametertext1 = '<b>'+str(fthickness[0])+'m fault thickness</b>'
            p_names = SIparams_dict[0].keys()
            parms_SI = SIparams_dict[0].values()
            parms_scaled = scale_array(parms_SI,p_names,direction='normal')
            parametertext2='<br><b>name=SI/scaled</b><br><br>'
            for val,valscaled,name in zip(parms_SI,parms_scaled,p_names):
                if isinstance(val, str) == True:
                    parametertext2 += str(name)+'='+val+'<br>'
                else:
                    parametertext2 += str(name)+'='+str(basic_func.tidy(val,7))+'/'+str(basic_func.tidy(valscaled,7))+'<br>'
        elif len(SIparams_dict) > 1:
            parametertext1 = '<b>fault thicknesses [m]: </b><br>'
            if SIparams_fz_same == False:
                for each in fthickness:
                    parametertext1 += str(each)+', '
                parametertext1=parametertext1[:-2]
            else:
                parametertext1 += str(fthickness[0])
            if SIparams_dict_same == True:
                p_names = SIparams_dict[0].keys()
                parms_SI = SIparams_dict[0].values()
                parms_scaled = scale_array(parms_SI,p_names,direction='normal')
                parametertext2='<br><br><b>name=SI/scaled</b><br>'
                for val,valscaled,name in zip(parms_SI,parms_scaled,p_names):
                    if isinstance(val, str) == True:
                        parametertext2 += str(name)+'='+val+'<br>'
                    else:
                        parametertext2 += str(name)+'='+str(basic_func.tidy(val,7))+'/'+str(basic_func.tidy(valscaled,7))+'<br>'
            else:
                parametertext2='<br><br>curve differences:<br>'
                p_names = differences.keys()
                parms_SI = differences.values()
                parms_scaled = scale_array(parms_SI,p_names,direction='normal')
                for val,valscaled,name in zip(parms_SI,parms_scaled,p_names):
                    parametertext2 += str(name)+', '
                parametertext2=parametertext2[:-2]
        
        if len(differences)>0:
            diff_keys=differences.keys()
            
    else:
        parametertext1 = '<b>'+str(fthickness[0])+'m fault thickness</b>'
        p_names = SIparams_dict[0].keys()
        parms_SI = SIparams_dict[0].values()
        parametertext2='<br><b>parameter=SI units</b><br>'
        for val,name in zip(parms_SI,p_names):
            if isinstance(val, str) == True:
                parametertext2 += str(name)+'='+val+'<br>'
            else:
                parametertext2 += str(name)+'='+str(basic_func.tidy(val,7))+'<br>'
        
        
    
    #initialze empty traces that will be plottet
    traces = []
    #add optional traces here already
    for eachtrace in additionaltrace:
        traces.append(eachtrace)
    #print
    #print('loading data:')
    
    filenames=[]
    ymaxvals=[]
    yminvals=[]
    
    
    #setting up categorical colors:
    if len(ipath_arr) > 1:
        n_min=0
        n_max=len(ipath_arr)-1 
        cma = cm.rainbow

    for index,eachinput in enumerate(ipath_arr):
        if len(ipath_arr) > 1:
            cn=basic_func.normalize(index,n_min,n_max)
            c = cma(cn,1)
            rgb = c[:3]
            rgb = "rgb(%s, %s, %s)" % (int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
            #'rgba(255,255,255,0.8)'
        else:
            rgb = '#2B4369'
        #checking and preparation for further well test analysis:
        if itype[index] == 'rb_fe':
            pta = True
            #setting filename:
            filename = ntpath.basename(eachinput)
            df = pd.read_csv(eachinput)
            if 'rb_dp' not in df.columns:
                print('wrong input csv type set or input file broken')
                return 
            #print('RB_FE input csv detected')
            
            df.loc[:,'FoerderDruck'] = result_sclaing(df.loc[:,'rb_dp'])
            
        elif itype[index] == 'golem':
            pta = True
            #setting filename:
            filename = ntpath.basename(eachinput)            
            df = pd.read_csv(eachinput)
            if 'FoerderDruck' not in df.columns:
                print('wrong input csv type set or input file broken')
                return 
            #print('GOLEM input csv detected')
            
        elif itype[index] == 'rb':
            pta = True
            if type(eachinput) is np.ndarray and len(eachinput[0]) == 128:
                
                #setting filename:
                filename = 'rb online stage output'
                   
                #print('RB online input array detected')
                
                df = pd.DataFrame()
                df['time'] = t_list
                df['t_hour'] = df['time']/3600
                df['RB_out']= abs(pd.melt(pd.DataFrame(eachinput)).drop(['variable'],axis=1))
                RB_backscaled = result_sclaing(eachinput)
                df['FoerderDruck']= abs(pd.melt(pd.DataFrame(RB_backscaled)).drop(['variable'],axis=1))
                
                #first row not needed, dublicate specific to RB online stage ouput, remove:
                df.drop(df.index[0],inplace=True)
                df.drop(df.tail(1).index,inplace=True) # drop last n rows
                df.reset_index(drop=True,inplace=True)
            else:
                print('input array does not meet criteria needed, please check length=128 and type=np.ndarray')
                return
        elif itype[index] == 'preped_df':
            df = eachinput
            filename = 'preped df'
            pta = False
            
            
        else:
            print('input type not recognised... aborting!')
            return
        #print('data loaded to df')
        
        filenames.append(filename)
        
        if pta == True:
            #well testing data calculation and flow type evaluation:
            if len(SIparams_dict) > 1:
                df_calc,df_mft,faultzone_bd_detected = determine_main_flow_type_light(df,SIparams_dict[index],identifier)
            else:
                df_calc,df_mft,faultzone_bd_detected = determine_main_flow_type_light(df,SIparams_dict[0],identifier)
    
        #set data for traces:
        x=df.loc[1:,'t_hour']
        y=df.loc[1:,'DruckAenderung']
        y_extreme1 = abs(y).max()
        ymaxvals.append(y_extreme1)
        
        y_extreme2 = abs(y).min()
        if np.allclose(y_extreme2,0.0) == True:
            y_qunatile = y.quantile(0.20)
            yminvals.append(y_qunatile)
        else:
            yminvals.append(y_extreme2)
            
        #if differences exist in inputparams then put them into hover info:
        if len(SIparams_dict) > 1:
            current_dict = SIparams_dict[index]
            diff_string = '<br>'+'FZ_th='+str(fthickness[index])+'m'
            difftext = 'FZ_th='+str(fthickness[index])+'m'
        else:
            current_dict = SIparams_dict[0]
            diff_string = '<br>'+'FZ_th='+str(fthickness[index])+'m'
            difftext = 'FZ_th='+str(fthickness[index])+'m'
        
        if len(differences)>0:    
            for eachkey in diff_keys:
                if eachkey in current_dict.keys():
                    diff_string += '<br>'+str(eachkey)+'='+str(current_dict[eachkey])
                    difftext += '<br>'+str(eachkey)+'='+str(current_dict[eachkey])

            
        
        #generate trace and add to traces
        p_trace=go.Scatter(showlegend=True,
                            x=x,
                            y=y,
                            name='dP '+filename+diff_string,
                            hoverinfo = 'y+name+text',
                            text=difftext,
                            mode = 'lines+markers',
                            line=dict(color=rgb,
                                      width=2,
                                      dash = 'solid'),
                            marker=dict(size=1,
                                        opacity=0,
                                        color=rgb,
                                        ),
                            )
        traces.append(p_trace)
        
        if DERplot[index] == True:
            x=df.loc[2:124,'t_hour']
            y=df.loc[2:124,'DER']
            
            
            flowtype_list=df.loc[2:124,'flowtype']
            flowtype_list=[letters[:3] for letters in flowtype_list]
            flowtype_label= [None]*len(flowtype_list) 
            flowtype_label[::3]=flowtype_list[::3]


            
            #generate trace and add to traces
            p_trace=go.Scatter(showlegend=False,
                                x=x,
                                y=y,
                                name='DER '+filename+diff_string,
                                hoverinfo = 'y+name+text',
                                text=flowtype_label,
                                textposition='top center',
                                mode = 'markers+text',
                                textfont=dict(size=7),
                                line=dict(color=rgb,
                                          width=2,
                                          dash = 'dot'),
                                marker=dict(size=3,
                                            opacity=1.0,
                                            color=rgb,
                                            ),
                                )
            traces.append(p_trace)
            
            #adding minimum of DER to adjust scale of y axis
            y_extreme3 = abs(y).min()
            if np.allclose(y_extreme3,0.0) == True:
                y_qunatile = y.quantile(0.20)
                yminvals.append(y_qunatile)
            else:
                yminvals.append(y_extreme3)
        
   
    #determin longest filename:
    lname = max(filenames, key=len) + ' DER'
    

    # setting x-axis:
    if xtyp == 'log':
        xmax=math.ceil(np.log10(df['t_hour'].max()))
        xmin=math.floor(np.log10(df['t_hour'][1]))  
        xaxis1=gen_xaxis_dict(title=xtitle,typ=xtyp,rang=[xmin,xmax])
    elif xtyp == 'linear':
        xmax=math.ceil(df['t_hour'].max())
        xmin=math.floor(df['t_hour'].min())
        dx = basic_func.tidy(xmax-xmin,1)/10
        xaxis1=gen_xaxis_dict(title=xtitle,typ=xtyp,rang=[xmin,xmax],dtick=dx)     


    #setting y-axis:
    if ytyp == 'linear':
        #calculate y-axis limits and steps
        ymax = max(ymaxvals)*1.1
        dy=basic_func.tidy(ymax,1)/10
        if True in DERplot:
            yaxis1=gen_yaxis_dict(title=ytitle+' / DER',typ=ytyp,rang=[0,ymax],dtick=dy,tickformat="1.3f")
        else:
            yaxis1=gen_yaxis_dict(title=ytitle,typ=ytyp,rang=[0,ymax],dtick=dy,tickformat="1.3f")
    
    elif ytyp == 'log':
        logmax=np.log10(max(ymaxvals))
        for i, eachy in enumerate(yminvals):
            if np.allclose(eachy,0.0) == True:
                del yminvals[i]
        logmin=np.log10(min(yminvals))
        ymax=math.ceil(logmax)
        
        #if double log plot make show same amount of log cycles on each axis
        if xtyp == 'log':
            ymin=ymax-abs(xmin-xmax)
        else:
            ymin=math.floor(logmin)   
            
            
        if True in DERplot:
            yaxis1=gen_yaxis_dict(title=ytitle+' / DER',typ=ytyp,rang=[ymin,ymax],tickformat="1.3f")
        else:
            yaxis1=gen_yaxis_dict(title=ytitle,typ=ytyp,rang=[ymin,ymax],tickformat="1.3f")        
    
       
        
    annotations=[]
    an = dict(x=0.50,
              y=0.95,
              showarrow=False,
              text=parametertext1,
              bgcolor='rgb(255,255,255)',
              opacity=0.8,
              bordercolor='#000000',
              borderwidth=1,
              align='center',
              xref='paper',
              yref='paper',
              font =dict(family=fontpath, 
                         size=17, 
                         color='#000000'))
    annotations.append(an)
    
    an = dict(x=0.50,
          y=0.1,
          showarrow=False,
          text=parametertext2,
          bgcolor='rgb(255,255,255)',
          opacity=0.8,
          bordercolor='#000000',
          borderwidth=1,
          align='center',
          xref='paper',
          yref='paper',
          font =dict(family=fontpath, 
                     size=10, 
                     color='#000000'))
    annotations.append(an)
    
    #adding optional annotations here:
    if len(optional_annotation) != 0:
        for eachan in optional_annotation:
            annotations.append(eachan)
    
    #setting layout here:
    layout = layout_f_plotly(xaxis1,yaxis1,llegendword=lname,annotations=annotations)
    
                                
    #plot construction and saving:
    fig = dict(data=traces, layout=layout)
    
    saveplot_routine(fig,indv_plotname,plotdir,newfoldername,auto_open,pdf,png,html)

    




def make_scatter_traces_withconfidence(traces,x,y,y_conf,name,rgb,style='solid'):
    p_trace=go.Scatter(showlegend=True,
                        x=x,
                        y=y,
                        error_y=dict(type='data',
                                     array=np.array(y_conf)/2,
                                     color=rgb,
                                     visible=True),
                        name=name,
                        hoverinfo = 'y+name',
                        mode = 'lines+markers',
                        line=dict(color=rgb,
                                  width=2,
                                  dash = style),
                        marker=dict(size=1,
                                    opacity=0,
                                    color=rgb,
                                    ),
                        )
    traces.append(p_trace)
    return traces



def make_scatter_traces_normal(traces,x,y,name,rgb,style='solid'):
    p_trace=go.Scatter(showlegend=True,
                        x=x,
                        y=y,
                        name=name,
                        hoverinfo = 'y+name',
                        mode = 'lines+markers',
                        line=dict(color=rgb,
                                  width=2,
                                  dash = style),
                        marker=dict(size=1,
                                    opacity=0,
                                    color=rgb,
                                    ),
                        )
    traces.append(p_trace)
    return traces

def add_point_traces(traces,x,y,name,rgb,size=5):
    p_trace=go.Scatter(showlegend=True,
                        x=x,
                        y=y,
                        name=name,
                        hoverinfo = 'y+name',
                        mode = 'markers',
                        marker=dict(size=size,
                                    opacity=1,
                                    color=rgb,
                                    ),
                        )
    traces.append(p_trace)
    return traces


def plot_sobol(df_S1,
               df_S1_conf,
               df_ST,
               df_ST_conf,
               indv_plotname,
               workingdir,
               plottitle='Global Sensitivity Analysis',
               plot_ST=True,
               plot_S1=False,
               fontpath='./FiraMono-Medium.otf'):
    
    #read x values = sample size which is in headers:
    x = df_S1.columns.tolist()
    del x[0:2]
    x = [float(i) for i in x]
    
    x_sorted = sorted(x)
    
    sortingindex = []
    for each in x_sorted:
        sortingindex.append(x.index(each))
        
    #get variable names:
    l_names = df_S1['names'].tolist()
    
    traces = []
    cma = cm.rainbow
    
    for index,eachname in enumerate(l_names):
        y_S1 = df_S1.loc[df_S1['names']==eachname,:].drop(df_S1.columns[[0,1]], axis=1).values.flatten().tolist()
        y_S1 = [y_S1[i] for i in sortingindex]
        
        y_S1_conf = df_S1_conf.loc[df_S1_conf['names']==eachname,:].drop(df_S1_conf.columns[[0,1]], axis=1).values.flatten().tolist()
        y_S1_conf = [y_S1_conf[i] for i in sortingindex]
        
        y_ST = df_ST.loc[df_ST['names']==eachname,:].drop(df_ST.columns[[0,1]], axis=1).values.flatten().tolist()
        y_ST = [y_ST[i] for i in sortingindex]
        
        y_ST_conf = df_ST_conf.loc[df_ST_conf['names']==eachname,:].drop(df_ST_conf.columns[[0,1]], axis=1).values.flatten().tolist()
        y_ST_conf = [y_ST_conf[i] for i in sortingindex]
        
        cn=basic_func.normalize(index,0,len(l_names)-1 )
        c = cma(cn,1)
        rgb = c[:3]
        rgb = "rgb(%s, %s, %s)" % (int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
        
        if plot_S1 == True:
            traces = make_scatter_traces_withconfidence(traces,x_sorted,y_S1,y_S1_conf,eachname+'_S1',rgb,style='dash')
        if plot_ST == True: 
            traces = make_scatter_traces_withconfidence(traces,x_sorted,y_ST,y_ST_conf,eachname+'_ST',rgb,style='solid')
    
    
    xaxis =dict(
                title='no. of samples',
                titlefont=dict(size=15),
                type='linear',
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                tickformat="g",
                tickfont=dict(size=13),
                )
    
    
    yaxis =dict(
                title='sensitivity index',
                titlefont=dict(size=15),
                type='linear',
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                tickformat="1.2f",
                tickfont=dict(size=13),
                )
    
    annotations=[]
    an = dict(x=0.50,
              y=0.95,
              showarrow=False,
              text=plottitle,
              bgcolor='rgb(255,255,255)',
              opacity=0.8,
              bordercolor='#000000',
              borderwidth=1,
              align='center',
              xref='paper',
              yref='paper',
              font =dict(family=fontpath, 
                         size=17, 
                         color='#000000'))
    annotations.append(an)
    
    
    layout = layout_f_plotly(xaxis,yaxis,annotations=annotations)
    
    fig1 = dict(data=traces, layout=layout)
    
    saveplot_routine(fig1,indv_plotname,workingdir,'sobol_plots')     
    return     




def plot_dpfzm_slope (df_fz,
                      indv_plotname,
                      workingdir,
                      plottitle='Pressure Comparisson FZ and Matrix-only',
                      fontpath='./FiraMono-Medium.otf',
                      optional_annotation=[],
                      auto_open=True,
                      pdf=True,
                      png=False,
                      html=False,
                      xtype='log',
                      ytype='linear'):
    
    x = df_fz['t_hour']
    y1 = df_fz['dp_fz_m']
    y2 = df_fz['dp_fz_m_slope']
    
    traces = []
    make_scatter_traces_normal(traces,x,y1,'dp_fz_m',rgb='black')
    make_scatter_traces_normal(traces,x,y2,'dp_fz_m_slope',rgb='red')
    
    xaxis =dict(
                title='time [h]',
                titlefont=dict(size=15),
                type=xtype,
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                tickformat="g",
                tickfont=dict(size=13),
                )
    
    
    yaxis =dict(
                title='dp/dp_slope',
                titlefont=dict(size=15),
                type=ytype,
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                tickformat="1.2f",
                tickfont=dict(size=13),
                )
    
    annotations=[]
    an = dict(x=0.50,
              y=0.95,
              showarrow=False,
              text=plottitle,
              bgcolor='rgb(255,255,255)',
              opacity=0.8,
              bordercolor='#000000',
              borderwidth=1,
              align='center',
              xref='paper',
              yref='paper',
              font =dict(family=fontpath, 
                         size=17, 
                         color='#000000'))
    annotations.append(an)
    
    #adding optional annotations here:
    if len(optional_annotation) != 0:
        for eachan in optional_annotation:
            annotations.append(eachan)
    
    
    layout = layout_f_plotly(xaxis,yaxis,annotations=annotations,fontpath=fontpath)
    
    fig1 = dict(data=traces, layout=layout)
    
    saveplot_routine(fig1,indv_plotname,workingdir,'dp_diff_plots',auto_open,pdf,png,html) 
    
    return






def plot_pi_comp (df_fz,
                    df_m,
                      indv_plotname,
                      workingdir,
                      pointlist=False,
                      plottitle='Pressure Comparisson FZ and Matrix-only',
                      fontpath='./FiraMono-Medium.otf',
                      optional_annotation=[],
                      auto_open=True,
                      pdf=True,
                      png=False,
                      html=False):
    
    x = df_fz['t_hour']
    y1 = df_fz['Pi[l/s/MPa]']
    #y2 = df_m['Pi[l/s/MPa]']
    y3 = df_fz['rel_Pi_change[-]']
    
    #ymax = 2*(max([np.median(y1),np.median(y2),np.median(y3)]))
    
    traces = []
    make_scatter_traces_normal(traces,x,y1,'Pi Fault zone [l/s/MPa]',rgb='black',style='solid')
    #make_scatter_traces_normal(traces,x,y2,'Pi Matrix [l/s/MPa]',rgb='black',style='dash')
    make_scatter_traces_normal(traces,x,y3,'Rel. FZ Influnce vs Ref. M. Pi [-]',rgb='orange')
    if pointlist != False:
        add_point_traces(traces,[pointlist[0]],[pointlist[1]],'Ref. Matrix Pi',rgb='red',size=15)

    xaxis =dict(
                title='time [h]',
                titlefont=dict(size=15),
                type='linear',
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                tickformat="g",
                tickfont=dict(size=13),
                )
    
    
    yaxis =dict(
                title='Pi/dp_diff',
                titlefont=dict(size=15),
                type='log',
                showgrid=True,
                mirror=True,
                showline=True,
                zeroline=False,
                gridcolor='#000000',
                ticks='outside',
                showticklabels=True,
                tickcolor='#000000',
                autorange=True,
                #range=[0,ymax],
                tickformat="1.2f",
                tickfont=dict(size=13),
                )
    
    annotations=[]
    an = dict(x=0.50,
              y=0.95,
              showarrow=False,
              text=plottitle,
              bgcolor='rgb(255,255,255)',
              opacity=0.8,
              bordercolor='#000000',
              borderwidth=1,
              align='center',
              xref='paper',
              yref='paper',
              font =dict(family=fontpath, 
                         size=17, 
                         color='#000000'))
    annotations.append(an)
    
    #adding optional annotations here:
    if len(optional_annotation) != 0:
        for eachan in optional_annotation:
            annotations.append(eachan)
    
    layout = layout_f_plotly(xaxis,yaxis,annotations=annotations,fontpath=fontpath)
    
    fig1 = dict(data=traces, layout=layout)
    
    saveplot_routine(fig1,indv_plotname,workingdir,'Pi_plots',auto_open,pdf,png,html) 
    
    return















