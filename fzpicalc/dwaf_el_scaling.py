

def scale_it(p_mins,p_maxs,p_names):
    p_mins_sc=[]
    p_maxs_sc=[]
    for no, pmin in enumerate(p_mins):
        if p_names[no] == 'k_matrix' or p_names[no] == 'k_fault':
            min_sc = p_mins[no]*1e+6
            max_sc = p_maxs[no]*1e+6
            p_mins_sc.append(min_sc)
            p_maxs_sc.append(max_sc)
        elif p_names[no] == 'visocisty':
            p_mins_sc.append(p_mins[no])
            p_maxs_sc.append(p_maxs[no])            
        elif p_names[no] == 'S_matrix' or p_names[no] == 'S_fault':
            min_sc = p_mins[no]*1e+6*3e+4*3e+4
            max_sc = p_maxs[no]*1e+6*3e+4*3e+4
            p_mins_sc.append(min_sc)
            p_maxs_sc.append(max_sc)            
        elif p_names[no] == 'rate':
            min_sc = p_mins[no]/(9.7182e+2*3e+4)
            max_sc = p_maxs[no]/(9.7182e+2*3e+4)
            p_mins_sc.append(min_sc)
            p_maxs_sc.append(max_sc)    
        else:
            print('found variable name for which no scaling rule exists, check script!')    
    return p_mins_sc, p_maxs_sc 
    

def result_sclaing(RB_ouptuts,
                   p0 = 0.1,
                   z =  -500,
                   GW = 3000,
                   rho = 971.82,
                   char_stress = 1e+6):

    g = 9.81
    scale = p0 - rho*g*(z-GW)/char_stress
    
    p_correct = RB_ouptuts + scale

    return p_correct


def storage_sc(value,direction='normal'):
    
    if direction=='normal':
        value = value
        value_scaled = value * 1e+6 * 3e+4 * 3e+4
        return value_scaled
    
    if direction=='reverse':
        value_scaled = value
        value_unscaled = value_scaled / (1e+6 * 3e+4 * 3e+4)
        return value_unscaled



def perm_sc(value,direction='normal'):
    
    if direction=='normal':
        value = value
        value_scaled = value * 1e+6
        return value_scaled
    
    if direction=='reverse':
        value_scaled = value
        value_unscaled = value_scaled / 1e+6
        return value_unscaled



def rate_sc(value,direction='normal'):
    
    if direction=='normal':
        value = value
        value_scaled = value / (9.7182e+2 * 3e+4)
        return value_scaled
    
    if direction=='reverse':
        value_scaled = value
        value_unscaled = value_scaled * 9.7182e+2 * 3e+4
        return value_unscaled



def scale_array(values, names, direction='reverse'):
    values_s = []
    for i, name in enumerate(names):
        if name == 'rate':
            new_val = rate_sc(values[i],direction=direction)
        elif name == 'k_matrix' or name == 'k_fault':
            new_val = perm_sc(values[i],direction=direction)
        elif name == 'S_matrix' or name == 'S_fault':
            new_val = storage_sc(values[i],direction=direction)
        else:
            new_val = values[i]
        values_s.append(new_val)
    return values_s


def spec_stor_calc(value,inputtype='poro',Kf=5e+8):
    if inputtype=='poro':
        return value/Kf
    if inputtype=='ss':
        return value*Kf









