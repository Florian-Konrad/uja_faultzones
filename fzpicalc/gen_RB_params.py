

import pandas as pd
import numpy as np
import itertools as it



def gen_input_df (p_mins,p_maxs,p_steps,p_names,log_status,fzthickness_vals=False,uniquezz=False):
    
    '''#example usage:
    p_names=['f_poro','f_k','m_poro','f_th']
    p_mins=[1,-12,3,15]
    p_maxs=[5,-5,9,300]
    p_steps=[5,3,15,5]
    log_status=[False,True]
    df = gen_input_df(p_mins,p_maxs,p_steps,p_names)'''
    
    if not len(p_mins) == len(p_maxs) == len(p_steps):
        print('Lists for parameter range minima, maxima, steps need to be of same length! Returning...')
        return
    
    # construct ranges from user input
    vall=[]
    i = 0
    for pmin, pmax, pstep, log_stat in zip(p_mins,p_maxs,p_steps,log_status):
        
        if log_stat == True:
            pmin = np.log10(pmin)
            pmax = np.log10(pmax)
            
        vals = np.linspace(pmin,pmax,pstep)
        
        if uniquezz != False:
            vals = np.concatenate((vals,uniquezz[i]))
            vals = np.unique(vals)

        
        
        if log_stat == True:
            vals = [10**y for y in vals]
            
        vall.append(vals)
        
        i+=1
    
    if fzthickness_vals != False:
        vall.append(fzthickness_vals)
    
    dic = dict(zip(p_names,vall))
    combinations = list(it.product(*(dic[name] for name in p_names)))
    
    # write all possible combinations of ranges into df
    df = pd.DataFrame(data=combinations,columns=p_names)
    
    return df






