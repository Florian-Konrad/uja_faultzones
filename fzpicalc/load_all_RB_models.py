

import numpy as np
from time import time
import os
import fzpicalc.RB_model as rbm

maindir = os.getcwd()

#########################################################
#########################################################
## define stuff from DwfEl input file:
#########################################################
#########################################################

q_a = 3 #anzahl komponenten stiffness matrix matrix+fz+dynvisc=3
q_f = 2 #anzahl componenten load vector: matrix+fz=2    #alt + liftingfunc+prodrate
q_l = 1 #dimension des ouputs
q_m = 3
n_outputs = 1
n_timesteps = 127
dt = 1.0
euler_theta = 1.0 #backward euler
growth_rate = 1.1
start_time = 1.0
end_time = 1.8e6
varying_timesteps = True
time_dependent_parameters = True
ID_param = [5]
#online_mu_parameters = np.array([1.0e-09, 1.0e-04, 0.00028974, 1.8e3, 1.8e3, 1.0289971393879524e-06])
#([perm_matrix, perm_fault, mu, specific storage_matrix, specific storage_fault, production rate])

#load all fault zone models:
os.chdir(os.path.join(maindir,'fzpicalc'))
modelnames = os.listdir('modelz')
modelnames.remove('matrix')
models = []
for eachdir in modelnames:
    path = os.path.join('modelz',eachdir,'offline_data')
    t = time()
    model = rbm.model_from_offline_data(path,
                                     q_a,q_f,q_l,q_m,
                                     n_outputs, 
                                     n_timesteps,
                                     dt,
                                     euler_theta,
                                     varying_timesteps = varying_timesteps,
                                     growth_rate = growth_rate,
                                     time_dependent_parameters = time_dependent_parameters,
                                     ID_param = ID_param, start_time = start_time,
                                     end_time = end_time)
    t_model_gen = time()- t
    print(str(t_model_gen)+'s elapsed to add the '+eachdir+' model!')
    models.append(model)

#add matrix model:
modelnames.append('matrix')
t = time()
matrix_model = rbm.model_from_offline_data(os.path.join('modelz','matrix','offline_data'),
                                     2,2,q_l,2,
                                     n_outputs, 
                                     n_timesteps,
                                     dt,
                                     euler_theta,
                                     varying_timesteps = varying_timesteps,
                                     growth_rate = growth_rate,
                                     time_dependent_parameters = time_dependent_parameters,
                                     ID_param = [3], start_time = start_time,
                                     end_time = end_time)
models.append(matrix_model)
t_model_gen = time()- t
print(str(t_model_gen)+'s elapsed to add the matrix model!')


#generate dicitonary with all RB models loaded as objects
models_dict = dict(zip(modelnames,models))


#calculate timesteps and times once:
t_list = [0.0,1.0]
dt=1
t=1
for i in range(125):
    dt=dt*1.1
    t+=dt
    t_list.append(t)
t_list.append(1.8e6)
os.chdir(maindir)

'''
#example usage:

RB_outputs_fz100 = load_all_RB_models.models_dict['100'].transient_rb_solve_without_error_bound(online_mu_parameters_fz)
RB_outputs_matrix = load_all_RB_models.models_dict['matrix'].transient_rb_solve_without_error_bound(online_mu_parameters_matrix)

df_fz100 = pd.melt(pd.DataFrame(RB_outputs_fz100)).drop(['variable'],axis=1)
df_fmatrix = pd.melt(pd.DataFrame(RB_outputs_matrix)).drop(['variable'],axis=1)
df_out = pd.concat([df_fz100, df_fmatrix], axis=1)
'''
