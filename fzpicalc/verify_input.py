
import numpy as np
import fzpicalc.basic_func as basic_func

param_range_min = {"k_matrix":1.0e-17,
                   "k_fault":1.0e-14,
                   "viscosity":1.0e-4,
                   "S_matrix":2.0e-12,
                   "S_fault":2.0e-12,
                   "rate":10.0}

param_range_max = {"k_matrix":2.0e-11,
                   "k_fault":1.0e-9,
                   "viscosity":3.0e-4,
                   "S_matrix":1.6e-10,
                   "S_fault":1.6e-10,
                   "rate":20.0}

required_params = ['k_matrix','k_fault','viscosity','S_matrix','S_fault','rate','fz_thickness']



def check_input(row_dict,row_index):
    check = True
    for each_req in required_params:
        if each_req not in row_dict.keys():
            print('\n')
            print('INPUT ERROR: '+each_req+' is missing in parameter set '+str(row_index)+' (row no. starting with 0)')
            print('\n')
            check = False
        else: 
            if each_req == 'fz_thickness':
                if row_dict[each_req] not in [15,20,35,50,75,100,200,300]:
                    print('\n')
                    print('INPUT ERROR: '+each_req+' in line '+str(row_index)+' invalid must be one of the following values: 15, 20, 35, 50, 75, 100, 200, 300 (row no. starting with 0)')
                    print('\n')
                    check = False
            else:
                if (basic_func.tidy(row_dict[each_req],10) > param_range_max[each_req] 
                or basic_func.tidy(row_dict[each_req],10) < param_range_min[each_req]
                or np.isnan(row_dict[each_req])):
                    print('\n')
                    print('INPUT ERROR: '+each_req+' in line '+str(row_index)+' invalid must be in valid range: '+str(param_range_min[each_req])+' - '+str(param_range_max[each_req])+' (row no. starting with 0)')
                    print('\n')
                    check = False
    return check
        
        




