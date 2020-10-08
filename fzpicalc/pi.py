

import numpy as np
import fzpicalc.plotting_stuff as pls
import fzpicalc.flow_type_cat_simpl as ftcs
import fzpicalc.basic_func as basic_func

  
def calc_pi_curve(df,q):
    
    df['Pi']=q/df['Pi']
    
    return df


def try_to_get_pi(df_fz,
                  df_m,
                  param_dict,
                  index_of_headline,
                  plotdir,
                  fontpath,
                  plotting=False,
                  plotting_pdf=False,
                  plotting_html=False,
                  verb=0):

    
    
    Q = param_dict['rate']

    indv_plotname = str(index_of_headline)+'_no_param'
    if 'output_fname' in param_dict.keys():
        indv_plotname = param_dict['output_fname']
        del param_dict['output_fname']
    if 'folder' in param_dict.keys():
        del param_dict['folder']
        

    df_fz, mft_fz, faultzone_bd_detected = ftcs.determine_main_flow_type_light(df_fz,param_dict,index_of_headline,verb=1)
    df_m, mft_m, faultzone_bd_detected = ftcs.determine_main_flow_type_light(df_m,param_dict,index_of_headline,verb=1)

    #safty checks mf==raidal
    if mft_m != 'radial':
        if verb > 0:
            print('WARNING: Matrix Main Flow Type NOT Radial!!!!')
            print(param_dict)
    
    
    #extract P_ref from matrix pressure curve and calculate Pi_m:
    #locate latest radial point and get p_ref there:
    radial_df = df_m.loc[(df_m['flowtype'] == 'radial'),'RB_out']
    radial_indices = radial_df.index.values.tolist()
    #see if last 7 radial points are consecutive:
    if list(range(radial_indices[-7],radial_indices[-1]+1)) == radial_indices[-7:]:
        p_ref_index = radial_indices[-2]
    #secondary search: coming from the front
        pref_secondary_search = False
    else:
        #this triggers if short period radial flow is found at the end
        # which is associated with DER bending into negative due to RB model charackteristics
        # this wouldnt happen with FE model
        print('\n')
        print('secondary search for p_ref')
        pref_secondary_search = True
        for ix, each_i in enumerate(radial_indices):
            if ix < len(radial_indices)-1 and ix > 30:
                if each_i + 1 == radial_indices[ix+1]:
                    last_radial_index = radial_indices[ix+1]
        p_ref_index = last_radial_index

    #get time of current point:
    Ref_Pi_matrix_picktime = df_m.loc[p_ref_index,'t_hour']
    
    #check if timestampt is greater than ref point time:
    #value derived from latest possible picktime with previous algo
    norm_time = 342.76
    if Ref_Pi_matrix_picktime < norm_time :  
        #calculate ref point from radial flow DER     
        radial_DER_value = df_m.loc[p_ref_index,'DER']
        #during radial flow DER needs to be constant
        #using the DER calculation formula to extrapolate p at norm_time
        #needed for comparisson between rel_Pi_change[-] over param space
        #otherwise boundary effects are seen in results
        P_ref = (radial_DER_value*(np.log(norm_time)-np.log(Ref_Pi_matrix_picktime)))+df_m.loc[p_ref_index,'RB_out']
        Ref_Pi_matrix_picktime = norm_time
    else:
        P_ref = df_m.loc[p_ref_index,'RB_out']
        
    Ref_Pi_matrix = Q/P_ref
    
    
    #calc Pi and add to both dfs:
    df_fz.loc[:,'Pi[l/s/MPa]'] = Q/df_fz['DruckAenderung']
    df_m.loc[:,'Pi[l/s/MPa]'] = Q/df_m['DruckAenderung']
    
    Pi_change_si = Pi_change_rel = Pi_picktime = delta_p_m_fz = np.nan
    #calc dp_all, save to both dfs
    df_fz.loc[:,'delta_p_m_fz'] = df_m['DruckAenderung']-df_fz['DruckAenderung']
    df_fz.loc[:,'Pi_fz_versusRef[l/s/MPa]'] = Q/(P_ref-df_fz['delta_p_m_fz'])
    df_fz.loc[:,'Pi_change_fz_versusRef[l/s/MPa]'] = df_fz['Pi_fz_versusRef[l/s/MPa]']-(Q/P_ref)
    df_fz.loc[:,'rel_Pi_change[-]'] = df_fz['Pi_change_fz_versusRef[l/s/MPa]']/(Q/P_ref)
    df_fz = ftcs.append_linear_slope(df_fz,'rel_Pi_change[-]')
    for ix, each_slope in enumerate(df_fz['rel_Pi_change[-]_slope']):
        
        #check if matrix permeability is > 5e-15 --> boundary becomes important
        #exclude more points at the end and request radial flow close by
        if param_dict['k_matrix'] > 5e-15 and pref_secondary_search == True:
            #radial after 20h impossible as bc is present, if radial is found its due to the RB model
            if abs(each_slope) < 5e-5 and ix < (len(df_fz)-15) and ix > 30 and df_fz.loc[ix,'flowtype'] not in ['negative','other']:
                previous_point_slope = df_fz['rel_Pi_change[-]_slope'][ix-1]
                previous_previous_point_slope = df_fz['rel_Pi_change[-]_slope'][ix-2]
                #check ifthe 2 previous points have same sign and similar order of magnitude:
                if (previous_point_slope*each_slope > 0 
                    and previous_previous_point_slope*previous_point_slope > 0 
                    and abs(basic_func.magnitude(each_slope)-basic_func.magnitude(previous_point_slope)) <= 1):
                    
                    Pi_change_si = df_fz.loc[ix,'Pi_change_fz_versusRef[l/s/MPa]']
                    Pi_change_rel = df_fz.loc[ix,'rel_Pi_change[-]']
                    Pi_picktime = df_fz.loc[ix,'t_hour']
                    delta_p_m_fz = df_fz.loc[ix,'delta_p_m_fz']
                    break
        elif param_dict['k_matrix'] > 5e-15:
            if abs(each_slope) < 5e-5 and ix < (len(df_fz)-2) and ix > 30:
                previous_point_slope = df_fz['rel_Pi_change[-]_slope'][ix-1]
                previous_previous_point_slope = df_fz['rel_Pi_change[-]_slope'][ix-2]
                #check ifthe 2 previous points have same sign and similar order of magnitude:
                if (previous_point_slope*each_slope > 0 
                    and previous_previous_point_slope*previous_point_slope > 0 
                    and abs(basic_func.magnitude(each_slope)-basic_func.magnitude(previous_point_slope)) <= 1):
                    
                    Pi_change_si = df_fz.loc[ix,'Pi_change_fz_versusRef[l/s/MPa]']
                    Pi_change_rel = df_fz.loc[ix,'rel_Pi_change[-]']
                    Pi_picktime = df_fz.loc[ix,'t_hour']
                    delta_p_m_fz = df_fz.loc[ix,'delta_p_m_fz']
                    break  
        else:
            #5e-5 means less than 0.005% value change per hour 
            #and not look at the last few data points because they can have numerical artifacts
            #and look only after t_hour 0.5, cant be before that
            #current slope and the one before must both be negative to prevent detection of truning points
            if abs(each_slope) < 5e-5 and ix < (len(df_fz)-2) and ix > 60:
                previous_point_slope = df_fz['rel_Pi_change[-]_slope'][ix-1]
                previous_previous_point_slope = df_fz['rel_Pi_change[-]_slope'][ix-2]
                #check ifthe 2 previous points have same sign and similar order of magnitude:
                if (previous_point_slope*each_slope > 0 
                    and previous_previous_point_slope*previous_point_slope > 0 
                    and abs(basic_func.magnitude(each_slope)-basic_func.magnitude(previous_point_slope)) <= 1):
                    
                    Pi_change_si = df_fz.loc[ix,'Pi_change_fz_versusRef[l/s/MPa]']
                    Pi_change_rel = df_fz.loc[ix,'rel_Pi_change[-]']
                    Pi_picktime = df_fz.loc[ix,'t_hour']
                    delta_p_m_fz = df_fz.loc[ix,'delta_p_m_fz']
                    break


    #check for reasonability of PI calc --> 100% fault case
    #check if parametersetting causes matrix case to get neg. pressure inside well:
    neg_pressure = False
    if df_m.loc[df_m['FoerderDruck']<1.0,['FoerderDruck']].any()[0] == True: 
        if verb > 0:
            print
            print('Matrix only --> neg. pressure detected in well during drawdown!')
            print('current row id of paramset: '+str(index_of_headline))
        neg_pressure = True
        
        
    
    if plotting == True:
        
        if plotting_pdf == True:
            pdf=True
        else:
            pdf=False
        if plotting_html == True:
            html = True
        else:
            html = False
        
        param_dict['rel_Pi_change[-]'] = Pi_change_rel
        param_dict['main flow type - fault zone'] = mft_fz
        
        #format matrix param dict
        param_dict_matrix = param_dict.copy()
        del param_dict_matrix['k_fault']
        del param_dict_matrix['S_fault']
        param_dict_matrix['fz_thickness'] = 0

        
        #Pi comparisson
        Pi_m_ref_list = [Ref_Pi_matrix_picktime,Ref_Pi_matrix]
        
        parameter_text_annotation = pls.make_basic_text_annotation_from_dict(param_dict,x=0.5,y=0.9)
        
        pls.plot_pi_comp(df_fz,
                         df_m,
                         indv_plotname+'_PI_plot',
                         plotdir,
                         Pi_m_ref_list,
                         plottitle='PI and Fault Zone Influence Evolution',
                         fontpath=fontpath,
                         optional_annotation=[parameter_text_annotation],
                         auto_open=False,
                         pdf=pdf,
                         png=True,
                         html=html)

        #fault zone and matrix dp and DER plot
        pls.plot_pressure([df_fz,df_m],
                         [param_dict,param_dict_matrix],
                         [param_dict['fz_thickness'],param_dict_matrix['fz_thickness']],
                         compare_annotation=False,
                         itype=['preped_df','preped_df'],
                         newfoldername = 'p_data_plots',
                         DERplot=[True,True],
                         indv_plotname = str(index_of_headline)+'_p_data_combined',
                         xtyp='log',
                         ytyp='log',
                         plotdir = plotdir,
                         auto_open=False,
                         html=html,
                         png=True,
                         pdf=pdf)
        
    return Pi_change_si,delta_p_m_fz,Pi_change_rel,Pi_picktime,Ref_Pi_matrix,Ref_Pi_matrix_picktime,P_ref,df_fz,df_m,mft_fz,mft_m,neg_pressure























