

import fzpicalc.pi as pri
import fzpicalc.progressbar as progressbar
import fzpicalc.rb_ouput_conversion as cv
import fzpicalc.load_all_RB_models as modelzzzzzz
import fzpicalc.dwaf_el_scaling as scale
import fzpicalc.verify_input as vf
import numpy as np
import pandas as pd
import os
from datetime import datetime
from time import time
import fzpicalc.basic_func as basic_func
print('\n')








########################################
########################################
########################################
########################################
#USER INPUT:
input_filename = 'extreme_100m_0.0001_highkm_2e-12ss.csv'
save_pressure_curves = True
plotting = True # this will enable pressure curve and derivative plots as well as PI calculation plot as .png
#addtional plotting output formats will be generated if set True:
plotting_pdf=False
plotting_html=True
########################################
########################################
########################################
########################################










#loading input
input_data_set = pd.read_csv(input_filename)



########################################
########################################
# generating scaled input arrays from input data
# and use correct fz model for calculation


#the order of these parameter names is hardcoded(defined during RB model generation) into the RB model solve and must always be the same
p_names=['k_matrix','k_fault','viscosity','S_matrix','S_fault','rate']
df_params = pd.DataFrame(columns=p_names)
#filling param df with unscaled values:
df_params['k_matrix'] = input_data_set['k_matrix']
df_params['viscosity'] = input_data_set['viscosity']
df_params['k_fault'] = input_data_set['k_fault']
df_params['S_matrix'] = input_data_set['S_matrix']
df_params['S_fault'] = input_data_set['S_fault']
df_params['rate'] = input_data_set['rate']
#scale param_comb
df_params_scaled = df_params.copy()
df_params_scaled['S_fault'] = scale.storage_sc(df_params_scaled['S_fault'])
df_params_scaled['S_matrix'] = scale.storage_sc(df_params_scaled['S_matrix'])
df_params_scaled['k_fault'] = scale.perm_sc(df_params_scaled['k_fault'])
df_params_scaled['k_matrix'] = scale.perm_sc(df_params_scaled['k_matrix'])
df_params_scaled['rate'] = scale.rate_sc(df_params_scaled['rate'])

#transform to np.array for RB model input:
np_params_scaled = df_params_scaled.values
np_params = df_params.values



########################################
########################################
# calculation of all input param combs


#making RB modelz accessable
modelz_dict = modelzzzzzz.models_dict

#load matrix model once:
matrix_model = modelz_dict['matrix']



#getting current time and use it as ouput folder name:
now = datetime.now()
dt_string = now.strftime("%d_%m_%Y-%H_%M_%S")
os.mkdir('./'+dt_string)
print('\n')
print('output directory '+dt_string+' created')
print('\n')
ouput_dir = './'+dt_string

l = len(input_data_set)

t = time()

#iterate over input data and calculate pressure curves:
for ei, each_input in input_data_set.iterrows():
    input_ok = vf.check_input(each_input, ei)
    if input_ok == True:
        fz_th = str(int(each_input['fz_thickness']))
        #load correct RB models:
        fz_model = modelz_dict[fz_th]

        #fetch param setting and prepare it for fz and matrix calculation:
        online_mu_parameters_fz = np_params_scaled[ei]
        online_mu_parameters_matrix = np.delete(online_mu_parameters_fz,[1,4])

        #solve RB models:
        #matrix
        RB_out_matrix = matrix_model.transient_rb_solve_without_error_bound(online_mu_parameters_matrix)
        df_m_out = cv.prep_rb_out_base(RB_out_matrix)
        #fault zone
        RB_out_fz = fz_model.transient_rb_solve_without_error_bound(online_mu_parameters_fz)
        df_fz_out = cv.prep_rb_out_base(RB_out_fz)

        #generate param dict:
        paramdict = each_input.to_dict()



        ########################################
        ########################################
        #analyize model output with PTA:
        ########################################
        ########################################

        current_identifier = ei #this identifier is printed to consle if no obvious flow type for pressure curve was determined

        #make Pi_change calculations
        #Pi_change = dp/Q = MPa/l/s
        (Pi_change_si,
        delta_p_m_fz,
        Pi_change_rel,
        Pi_picktime,
        Ref_Pi_matrix,
        Ref_Pi_matrix_picktime,
        P_refMatrix,
        df_fz_out,
        df_m_out,
        mft_fz,
        mft_m,
        neg_pressure) = pri.try_to_get_pi(df_fz_out,
                                         df_m_out,
                                         paramdict,
                                         current_identifier,
                                         ouput_dir,
                                         plotting_pdf=plotting_pdf,
                                         plotting_html=plotting_html,
                                         fontpath=os.path.join('fzpicalc','FiraMono-Medium.otf'),
                                         plotting=plotting)



        ########################################
        ########################################
        ########################################
        ########################################



        #if saving of pressure curves is enabled save to output folder:
        if save_pressure_curves == True:
            matrix_save_name = str(ei)+'_matrix.csv'
            fz_save_name = str(ei)+'_'+str(fz_th)+'m_faultzone.csv'
            df_m_out.to_csv(os.path.join(dt_string,matrix_save_name), index = False)
            df_fz_out.to_csv(os.path.join(dt_string,fz_save_name), index = False)

        #writing PTA results into input_data_set:
        input_data_set.loc[ei,'main flow type - matrix'] = mft_m
        input_data_set.loc[ei,'main flow type - fault zone'] = mft_fz
        input_data_set.loc[ei,'Pi_ref Matrix [l/s/MPa]'] = Ref_Pi_matrix
        input_data_set.loc[ei,'P_ref pick time [h]'] = Ref_Pi_matrix_picktime
        input_data_set.loc[ei,'Rel. fault zone PI influence [-]'] = Pi_change_rel
        input_data_set.loc[ei,'Pi change FZ [l/s/MPa]'] = Pi_change_si
        input_data_set.loc[ei,'dP change FZ [MPa]'] = delta_p_m_fz
        input_data_set.loc[ei,'Reference Matrix P[MPa]'] = P_refMatrix
        input_data_set.loc[ei,'Pi change pick time [h]'] = Pi_picktime

    else: #if input check fails line will is not evaluated
        input_data_set.loc[ei,'Rel. fault zone PI influence [-]'] = 'input not valid, skipped'




    #update progressbar:
    progressbar.print_progress(ei + 1, l, prefix = 'Progress:', suffix = 'Complete', bar_length = 50)

t_consumed = time() - t
av_time_per_param = basic_func.tidy((t_consumed/l), 3)
print('\n')
print('calculations finished with an average calculation speed per parameter combination (= 2 simulations) of '+str(av_time_per_param)+' seconds')
print('\n')
#saving results:
stor_name = 'calculated_'+input_filename
input_data_set.to_csv(os.path.join(dt_string,stor_name), index = False)
