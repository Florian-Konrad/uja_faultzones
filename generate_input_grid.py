
########################################
########################################
# generate an input file:
########################################
########################################
import fzpicalc.gen_RB_params as gen








########################################
########################################
########################################
########################################
#USER INPUT:

    
#define parameter ranges
p_names=['k_matrix','k_fault','viscosity','S_matrix','S_fault','rate','fz_thickness'] #order is important name order must correspond to min max lists and fz_thickness must be last
p_mins=[1.0e-15,1.0e-14,1.0e-4,2.0e-12,2.0e-12,20] #m²,m²,Pa*s,1/Pa,1/Pa,l/s
p_maxs=[1.0e-11,1.0e-09,3.0e-4,1.6e-10,1.6e-10,20] #m²,m²,Pa*s,1/Pa,1/Pa,l/s
fzthickness_vals = [15,75,200] #m from the possible discrete values defined in the RB models: [15,20,35,50,75,100,200,300]


log_status=[True,True,False,False,False,False] #specify if the parameter grid sampling should be linear=False or logarythmically=True
#define gridsteps over input space (for fz_thickness not necessary since only discrete values are allowed)
p_steps=[3,3,2,2,2,1]


# Tipp: same location in all lists belong together! 
# example: k_matrix will be sampled from 1.0e-12 - 1.0e-17 in 5 logarythmically equal steps
# --> p_names[0] sampled from min p_mins[0]-p_maxs[0] logarythmically=log_status[0] in p_steps[0] steps


# should only parameter combinations be generated where fault zone has better hydraulic properties than matrix?
only_fault_better = True


#define output .csv filename:
output_filename = 'test_input_set.csv'

########################################
########################################
########################################
########################################










df_params = gen.gen_input_df(p_mins,p_maxs,p_steps,p_names,log_status,fzthickness_vals=fzthickness_vals)

if only_fault_better == True:
    #remove all combinations where m_kf > f_kf:
    remove = df_params.loc[(df_params['k_matrix'] >= df_params['k_fault']),].index.tolist()
    df_params = df_params.drop(remove)
    df_params = df_params.reset_index(drop=True)
    #remove all combinations where m_kf > f_kf:
    remove = df_params.loc[(df_params['S_matrix'] > df_params['S_fault']),].index.tolist()
    df_params = df_params.drop(remove)
    df_params = df_params.reset_index(drop=True)
    
df_params.to_csv(output_filename, index = False)




