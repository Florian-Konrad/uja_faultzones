


import numpy as np
import pandas as pd
from fzpicalc.flow_type_cat_simpl import determine_main_flow_type_light
from fzpicalc.dwaf_el_scaling import result_sclaing




#calculate timesteps and times once:
t_list = [0.0,1.0]
dt=1
t=1
for i in range(125):
    dt=dt*1.1
    t+=dt
    t_list.append(t)
t_list.append(1.8e6)


def prep_rb_out(inputarray,SIparams_dict,verb=1):
    if type(inputarray) is np.ndarray and len(inputarray[0]) == 128:

        if verb == 2:
            print('RB online input array detected')

        df = pd.DataFrame()
        df['time'] = t_list
        df['t_hour'] = df['time']/3600
        df['RB_out']= abs(pd.melt(pd.DataFrame(inputarray)).drop(['variable'],axis=1))
        RB_backscaled = result_sclaing(inputarray)
        df['FoerderDruck']= pd.melt(pd.DataFrame(RB_backscaled)).drop(['variable'],axis=1)

        #first row not needed, dublicate specific to RB online stage ouput, remove:
        df.drop(df.index[0],inplace=True)
        df.reset_index(drop=True,inplace=True)
    else:
        if verb == 1:
            print('input array does not meet criteria needed, please check length=128 and type=np.ndarray')
        return

    #do all the classic PTA calcuations on the df:
    df_calc,df_mft = determine_main_flow_type_light(df,SIparams_dict)

    return df_calc,df_mft


def prep_rb_out_base(inputarray,verb=1):
    if type(inputarray) is np.ndarray and len(inputarray[0]) == 128:

        if verb == 2:
            print('RB online input array detected')

        df = pd.DataFrame()
        df['time'] = t_list
        df['t_hour'] = df['time']/3600
        df['RB_out']= abs(pd.melt(pd.DataFrame(inputarray)).drop(['variable'],axis=1))
        RB_backscaled = result_sclaing(inputarray)
        df['FoerderDruck']= pd.melt(pd.DataFrame(RB_backscaled)).drop(['variable'],axis=1)

        #first row not needed, dublicate specific to RB online stage ouput, remove:
        df.drop(df.index[0],inplace=True)
        df.reset_index(drop=True,inplace=True)
    else:
        if verb == 1:
            print('input array does not meet criteria needed, please check length=128 and type=np.ndarray')
        return

    return df
