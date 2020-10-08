
import numpy as np
import pandas as pd
from time import time


def time_s_to_h(t_s,t_ini): #Berechne Zeitschritte in dt seit Foerderbeginn in Stunden um
    t_h = (t_s-t_ini)/3600.0
    return t_h


def calc_dP(P_trans,P_ini): #Berechne Druckaenderung seit Foerderbeginn
    dP = P_ini-P_trans
    return dP


def calc_DER(dP_before,dP_after,th_before,th_after): #Berechne Druck-Derivat
    DER = (dP_after-dP_before)/(np.log(th_after)-np.log(th_before)) #np.log = ln ; np.lo10 = log
    return DER

def calc_storage(poro,kfl=5.0e+8):     #berechne den speicherkoeffizienten aus fixed kfl 5e8 und input poro
    stor = (poro)/(kfl)    #spk=p/kfl einheit:Pa
    return stor

def calc_ratio(vm,vf):      # berechne das Verhaeltnis einer matrixvariablen zu einer stoerungsvariablen
    r = vf/(vm+vf)               #r>1 bedeutet matrixvariable groeser als stoerungsvariable
    return r

def calc_logslope(y1,y2,x1,x2):    #berechnet die Steigung im Doppellogplot
    slope = (np.log10(y1) - np.log10(y2)) / (np.log10(x1) - np.log10(x2))
    return slope

def calc_semilogslope(y1,y2,x1,x2):    #berechnet die Steigung im Semilogplot
    slope = (y1 - y2) / (np.log10(x1) - np.log10(x2))
    return slope

def calc_linearslope(y1,y2,x1,x2):    #berechnet die Steigung im normalen linearen Plot
    slope = (y1 - y2) / (x1 - x2)
    return slope




def append_linear_slope(df,variablename):
    entry_length = len(df)
    n = 1
    df.loc[:,variablename+'_slope'] = np.nan
    while n < (entry_length - 1):
        y1 = df[variablename][n-1]
        y2 = df[variablename][n+1]
        t1 = df['t_hour'][n-1]
        t2 = df['t_hour'][n+1]
        slope = calc_linearslope(y1,y2,t1,t2)
        #df['DER_slope'][n] = derivative_slope
        df.loc[n,variablename+'_slope'] = slope
        n += 1
    return df




def append_th_file(df):
    entry_length = len(df)
    n = 0
    b = df['time'][0]
    df.loc[:,'t_hour'] = np.nan
    while n < entry_length:
        a = df['time'][n]
        t_h = time_s_to_h(a,b)
        df.loc[n,'t_hour'] = t_h
        n += 1
    return df

def fast_append_th_file(df):
    b = df['time'][0]
    df['t_hour'] = df.apply(lambda row: time_s_to_h(row['time'],b), axis=1)
    return df


def append_dP_file(df):
    entry_length = len(df)
    n = 1  # 1 hier weil ich dp = 0 in der Liste haben moechte! Zur spaeteren Darstellung!
    b = df['FoerderDruck'][0]
    df.loc[:,'DruckAenderung'] = np.nan
    while n < entry_length:
        a = df['FoerderDruck'][n]
        dP = calc_dP(a,b)
        #df['DruckAenderung'][n] = dP
        df.loc[n,'DruckAenderung'] = dP
        n += 1
    return df

def fast_append_dP_file(df):
    b = df['FoerderDruck'][0]
    df['DruckAenderung'] = df.apply(lambda row: calc_dP(row['FoerderDruck'],b), axis=1)
    return df

def append_DER_file(df):
    entry_length = len(df)
    n = 2
    df.loc[:,'DER'] = np.nan
    df.loc[:,'dP_slope'] = np.nan
    df.loc[:,'dP_slope_semilog'] = np.nan
    while n < entry_length: #the 2 was changed from 1 due to RBoutput drop at last points
        p1 = df['DruckAenderung'][n-1]
        p2 = df['DruckAenderung'][n+1]
        t1 = df['t_hour'][n-1]
        t2 = df['t_hour'][n+1]

        if n < (entry_length - 2):
            df.loc[n,'DER'] = calc_DER(p1,p2,t1,t2)

        if n > 1 and n < (entry_length - 1):
            df.loc[n,'dP_slope'] = calc_logslope(p1,p2,t1,t2)
            df.loc[n,'dP_slope_semilog'] = calc_semilogslope(p1,p2,t1,t2)

        n += 1
    return df

def fast_append_DER_file(df):
    ddP = df.loc[:,'DruckAenderung'].values
    th = df.loc[:,'t_hour'].values
    DER = [np.nan]*len(th)
    dP_slope = [np.nan]*len(th)
    dP_slope_semilog = [np.nan]*len(th)
    for i, eachDER in enumerate(DER,start=2):
        if i < (len(DER)-1):
            p1 = ddP[i-1]
            p2 = ddP[i+1]
            t1 = th[i-1]
            t2 = th[i+1]
            if i < len(DER)-2:
                DER[i] = calc_DER(p1,p2,t1,t2)
            if i > 1:
                dP_slope[i] = calc_logslope(p1,p2,t1,t2)
                dP_slope_semilog[i] = calc_semilogslope(p1,p2,t1,t2)
    df.loc[:,'DER'] = DER
    df.loc[:,'dP_slope'] = dP_slope
    df.loc[:,'dP_slope_semilog'] = dP_slope_semilog
    return df



def append_slope_file(df):
    entry_length = len(df)
    n = 3
    df.loc[:,'DER_slope'] = np.nan
    while n < (entry_length - 3):
        y1 = df['DER'][n-1]
        y2 = df['DER'][n+1]
        t1 = df['t_hour'][n-1]
        t2 = df['t_hour'][n+1]
        derivative_slope = calc_logslope(y1,y2,t1,t2)
        #df['DER_slope'][n] = derivative_slope
        df.loc[n,'DER_slope'] = derivative_slope
        n += 1
    return df

def fast_append_slope_file(df):
    DER = df.loc[:,'DER'].values
    th = df.loc[:,'t_hour'].values
    DER_slope = [np.nan]*len(th)
    for i, eachDERslope in enumerate(DER_slope,start=3):
        if i < len(DER)-3:
            p1 = DER[i-1]
            p2 = DER[i+1]
            t1 = th[i-1]
            t2 = th[i+1]
            DER_slope[i] = calc_logslope(p1,p2,t1,t2)
    df.loc[:,'DER_slope'] = DER_slope
    return df

def append_pressure_slope_file(df):
    entry_length = len(df)
    n = 2
    df.loc[:,'dP_slope'] = np.nan
    df.loc[:,'dP_slope_semilog'] = np.nan
    while n < (entry_length - 1):
        y1 = df['DruckAenderung'][n-1]
        y2 = df['DruckAenderung'][n+1]
        t1 = df['t_hour'][n-1]
        t2 = df['t_hour'][n+1]
        dP_slope = calc_logslope(y1,y2,t1,t2)
        dP_slope_semilog = calc_semilogslope(y1,y2,t1,t2)
        #df['dP_slope'][n] = dP_slope
        df.loc[n,'dP_slope'] = dP_slope
        df.loc[n,'dP_slope_semilog'] = dP_slope_semilog
        n += 1
    return df







#LINEAR
def real_linear_marker(df,slope=0.5,delta=0.1):
    entry_length = len(df)
    n = 0
    df.loc[:,'real_linear_marker'] = 0.0
    while n < (entry_length):
        if df['dP_slope'][n] > (slope-(delta+0.025)) and df['dP_slope'][n] < (slope+delta) and df['DER_slope'][n] > (slope-(delta+0.025)) and df['DER_slope'][n] < (slope+delta):
                #df['real_linear_marker'][n] = df['DER_slope'][n]
                df.loc[n,'real_linear_marker'] = df['DER_slope'][n]
        n += 1
    return df

def fast_linear_bilinear_steep_neg_pos_marker(df):
    linear_slope = 0.5
    linear_delta = 0.1
    bilinear_slope = 0.25
    bilinear_delta = 0.1
    steep_slope_min = 0.6
    dP_slope = df.loc[:,'dP_slope'].values
    DER_slope = df.loc[:,'DER_slope'].values
    real_linear_marker = [0.0]*len(DER_slope)
    bilinear_marker = [0.0]*len(DER_slope)
    greater_than = [0.0]*len(DER_slope)
    DER_slope_neg = [0.0]*len(DER_slope)
    DER_slope_pos = [0.0]*len(DER_slope)

    BC_slope = [0.0]*len(DER_slope)
    boundary_DER_slope_min = 0.6
    boundary_dP_slope_max = 0.25
    boundary_found = False

    well_slope = [0.0]*len(DER_slope)
    well_minslope = 0.75



    for i,each in enumerate(dP_slope):
        #linear
        #dp slope between 0.25 and 0.6
        #DER slope between 0.375 and 0.6
        if each > (linear_slope-(linear_delta+0.15)) and each < (linear_slope+linear_delta) and DER_slope[i] > (linear_slope-(linear_delta+0.025)) and DER_slope[i] < (linear_slope+linear_delta):
            real_linear_marker[i] = DER_slope[i]
        #additional linear marker for tight dp_slope range
        #dp slope btween 0.45 and 0.55
        #Der slope between 0.5 and 0.73
        if each > (0.45) and each < (0.55) and DER_slope[i] > (0.5) and DER_slope[i] < (0.73):
            real_linear_marker[i] = DER_slope[i]

        #additional linear marker
        #DER slope between 0.375 and 0.6
        #and dP slope similar (7%) to DER slope
        if DER_slope[i] > (linear_slope-(linear_delta+0.025)) and DER_slope[i] < (linear_slope+linear_delta) and np.isclose(each,DER_slope[i],rtol=0.07) == True:
            real_linear_marker[i] = DER_slope[i]

        #bilinear
        #dp slope between 0.15 and 0.375
        #DER slope between 0.13 and 0.45
        if each > (bilinear_slope-bilinear_delta) and each < (bilinear_slope+(bilinear_delta+0.025)) and DER_slope[i] > (bilinear_slope-(bilinear_delta+0.02)) and DER_slope[i] < (bilinear_slope+(0.2)):
            bilinear_marker[i] = DER_slope[i]
        #steep
        #if each >= steep_slope_min and DER_slope[i] >= steep_slope_min:
        if DER_slope[i] >= steep_slope_min:
            greater_than[i] = DER_slope[i]

        #find wellstorage-like effects similar to steep
        if np.isclose(DER_slope[i], each, rtol=0.1) ==True and each > well_minslope:
                well_slope[i] = DER_slope[i]

        #model boundary cant be in early time region --> t_hour > 0.1h:
        if i > 36:
            if boundary_found == False:
                #boundary_effect search:
                # DER slope > 0.6
                # dP slope < 0.25
                # no bilinear marker
                if DER_slope[i] > boundary_DER_slope_min and each < boundary_dP_slope_max and bilinear_marker[i] == 0:
                    BC_slope[i:] = DER_slope[i:]
                    boundary_found = True

            #find end of boundary marking
            if boundary_found == True:

                if DER_slope[i] <= boundary_DER_slope_min:
                    #if end found check if model boundary end is not at pumping test end
                    # which means that it is not really a model boundary effect
                    # since this would last until pump test end except for rb error hump
                    if i < 60:
                        #resetting BC_slope completely
                        BC_slope = [0.0]*len(DER_slope)
                        boundary_found = False
                    else:
                        BC_slope[i:] = [0.0]*len(BC_slope[i:])
                        #set to false again so another boundary effect can be detected
                        boundary_found = False


        #neagtive DER slope
        if DER_slope[i] < 0:
            DER_slope_neg[i] = DER_slope[i]

        #positive DER slope
        if DER_slope[i] > 0:
            DER_slope_pos[i] = DER_slope[i]


    #check for well-like and steep combinations and extened well-like


    df.loc[:,'real_linear_marker'] = real_linear_marker
    df.loc[:,'bilinear_marker'] = bilinear_marker
    df.loc[:,'greater_than_0.6'] = greater_than
    df.loc[:,'DER_slope_neg'] = DER_slope_neg
    df.loc[:,'DER_slope_pos'] = DER_slope_pos
    df.loc[:,'BC_slope'] = BC_slope
    df.loc[:,'well_slope'] = well_slope
    return df

#BILINEAR
def bilinear_marker(df,slope=0.25,delta=0.1):
    entry_length = len(df)
    n = 0
    df.loc[:,'bilinear_marker'] = 0.0
    while n < (entry_length):
        if df['dP_slope'][n] > (slope-delta) and df['dP_slope'][n] < (slope+(delta+0.025)) and df['DER_slope'][n] > (slope-(delta+0.02)) and df['DER_slope'][n] < (0.7):
                #df['bilinear_marker'][n] = df['DER_slope'][n]
                df.loc[n,'bilinear_marker'] = df['DER_slope'][n]
        n += 1
    return df


#STEEP
def greater_than_andsame_marker(df,min_slope=0.6):
    entry_length = len(df)
    n = 0
    df.loc[:,'greater_than_0.6'] = 0.0
    while n < (entry_length):
        rangemax = df['dP_slope'][n]+0.1
        rangemin = df['dP_slope'][n]-0.1
        if df['dP_slope'][n] >= (min_slope) and df['DER_slope'][n] >= (min_slope) and df['DER_slope'][n] < (rangemax) and df['DER_slope'][n] > (rangemin):
                #df['greater_than_0.6'][n] = df['DER_slope'][n]
                df.loc[n,'greater_than_0.6'] = df['DER_slope'][n]
        n += 1
    return df

#POSITIVE
def append_pos_slop_fil(df):
    entry_length = len(df)
    n = 0
    df.loc[:,'DER_slope_pos'] = 0.0
    while n < (entry_length):
        if df['DER_slope'][n] > 0:
            #df['DER_slope_pos'][n] = df['DER_slope'][n]
            df.loc[n,'DER_slope_pos'] = df['DER_slope'][n]
        n += 1
    return df

def append_pos_slop_fil_fast(df):
    df.loc[:,'DER_slope_pos'] = 0.0
    for index, row in df.iterrows():
        if row['DER_slope'] > 0:
            df.at[index,'DER_slope_pos'] = row['DER_slope']
    return df


#NEGATIVE
def append_neg_slop_fil(df):
    entry_length = len(df)
    n = 0
    df.loc[:,'DER_slope_neg'] = 0.0
    while n < (entry_length):
        if df['DER_slope'][n] < 0:
            #df['DER_slope_neg'][n] = df['DER_slope'][n]
            df.loc[n,'DER_slope_neg'] = df['DER_slope'][n]
        n += 1
    return df

def append_neg_slop_fil_fast(df):
    df.loc[:,'DER_slope_pos'] = 0.0
    for index, row in df.iterrows():
        if row['DER_slope'] < 0:
            df.at[index,'DER_slope_neg'] = row['DER_slope']
    return df

#MODEL BOUNDARY
def identify_bc(df):
    entry_length = len(df)
    n = entry_length - 1
    df.loc[:,'DER_slope_BC'] = 0.0
    while n >= (entry_length - 10):
        #dpmax = df['dP_slope'][n]+0.1
        if df['DER_slope'][n] >= 0.6:
            l = n
            while df['DER_slope'][l] >= 0.1:
                #df['DER_slope_BC'][l] = df['DER_slope'][l]
                df.loc[l:(entry_length - 1),'DER_slope_BC'] = df['DER_slope'][l]
                l -= 1
        n -= 1
    return df



#RADIAL
def identify_radial(df):
    entry_length = len(df)
    n = 3
    df.loc[:,'DER_slope_radial'] = 99.0
    while n < (entry_length - 2):
        if df['DER_slope'][n] > -0.08 and df['DER_slope'][n] < 0.03:
            #df['DER_slope_radial'][n] = df['DER_slope'][n]
            df.loc[n,'DER_slope_radial'] = df['DER_slope'][n]
        n += 1

    #set all isolated single radial points Blackwing Lair to positive:
    n = 1
    while n < (entry_length-2):
        if (np.isclose(df['DER_slope_radial'][n],99.0) == False
            and np.isclose(df['DER_slope_radial'][n-1],99.0) == True
            and np.isclose(df['DER_slope_radial'][n+1],99.0) == True):
            df.loc[n,'DER_slope_radial'] = 99.0
        n += 1
    return df

#APPEND FLOW TYPE TO DruckAenderung.csv
def append_flow_typ(df,matrix_perm):
    entry_length = len(df)
    df.loc[:,'flowtype'] = 'other'


    n = 0
    while n < (entry_length):
        if df['DER_slope_pos'][n] != 0:
            df.loc[n,'flowtype'] = 'positive'
        n += 1

    n = 0
    while n < (entry_length):
        if df['DER_slope_neg'][n] != 0:
            df.loc[n,'flowtype'] = 'negative'
        n += 1

    n = 0
    while n < (entry_length):
        #only use if more then two consecutive points show bilinear behavior
        if df['bilinear_marker'][n] != 0 and len(df.loc[n-2:n+2].loc[df['bilinear_marker'] > 0.0]) > 2:

            #safty check slopes must be similar:
            DER_dP_comp_n = np.isclose(df['DER_slope'][n],df['dP_slope'][n],rtol=0.15)
            DER_dP_comp_n1 = np.isclose(df['DER_slope'][n+1],df['dP_slope'][n+1],rtol=0.15)
            DER_dP_comp_n2 = np.isclose(df['DER_slope'][n+2],df['dP_slope'][n+2],rtol=0.15)
            if DER_dP_comp_n == True and DER_dP_comp_n1 == True and DER_dP_comp_n2 == True:
                #more safty: DER and dP can't be to far away from each other
                if df['DruckAenderung'][n] < 5*df['DER'][n]:
                    df.loc[n,'flowtype'] = 'bilinear'
        n += 1

    n = 0
    while n < (entry_length):
        if df['greater_than_0.6'][n] != 0:
            df.loc[n,'flowtype'] = 'steep'
        n += 1

    n = 0
    while n < (entry_length):
        if df['BC_slope'][n] != 0:
            df.loc[n,'flowtype'] = 'model_boundary'
        n += 1

    n = 0
    while n < (entry_length):
        if (matrix_perm < 1e-14) & (df['BC_slope'][n] != 0):
            df.loc[n,'flowtype'] = 'steep'
        n += 1

    n = 1
    while n < (entry_length):
        if df['well_slope'][n] != 0:
            df.loc[n,'flowtype'] = 'well_effect'
        else:
            # check if current n is already clasified as steep
            # but one index previous it was still well_effect
            # change to well_effect since its just a transition
            if df.loc[n-1,'flowtype'] == 'well_effect' and df.loc[n,'flowtype'] == 'steep':
                df.loc[n,'flowtype'] = 'well_effect'
        n += 1

    #if we have well_effect following steep change all well_effect to steep
    # only if dP solpe in the beginning  flat (<0.3) --> fault zone has matrix boundary
    # if it is not flat it still is a well effect

    #to do : change 0.3 to 0.7 or check for no of well_effect > 50 --> steep
    if (df.loc[:44,'dP_slope'] < 0.3).any() == True or len(df.loc[df['flowtype']=='well_effect']) > 50:
        n = 10
        while n < (entry_length):
            if df['flowtype'][n] == 'well_effect' and df['flowtype'][n-1] == 'steep':
                # if true go forward and replace until well effect stops
                d_n = n
                while d_n < (entry_length):
                    if df['flowtype'][d_n] == 'well_effect':
                        df.loc[d_n,'flowtype'] = 'steep'
                        d_n += 1
                    else:
                        #will be triggert if well effect stops --> stopping replacement completely
                        d_n = entry_length
                #then stop outer search:
                n = entry_length
            else:
                #continue only until first well_effect after steep was found
                n += 1



    n = 0
    while n < (entry_length):
        if df['DER_slope_radial'][n] != 99:
            #df['flowtype'][n] = 'radial'
            df.loc[n,'flowtype'] = 'radial'
        n += 1

    n = 0
    while n < (entry_length):
        #only use if more then two consecutive points show linear behavior
        if df['real_linear_marker'][n] != 0 and len(df.loc[n-2:n+2].loc[df['real_linear_marker'] > 0.0]) > 2:
            #safty check slopes must be similar:
            DER_dP_comp_n = np.isclose(df['DER_slope'][n],df['dP_slope'][n],rtol=0.15)
            DER_dP_comp_n1 = np.isclose(df['DER_slope'][n+1],df['dP_slope'][n+1],rtol=0.15)
            if DER_dP_comp_n == True and DER_dP_comp_n1 == True:
                if matrix_perm > 1e-14:
                    #check if model boundary found before this point, if yes --> RB model behavior no real linear flow
                    if not (df.loc[10:n,'flowtype'] == 'model_boundary').any():
                        df.loc[n,'flowtype'] = 'linear'
                else:
                    df.loc[n,'flowtype'] = 'linear'
        n += 1

    # check last points of already specified flowtype and check if type changes more than three times
    # --> looks like reduced basis method error
    # should be removed and changed to other:
    #last_n_rows = 15
    #if len(df.tail(last_n_rows)['flowtype'].unique()) > 3:
    #    df.iloc[-last_n_rows:,df.columns.get_loc('flowtype')].loc[df['flowtype']!='model_boundary'] = 'other'

    # secondary check necessary
    # above check can fail  --> then model_bd + other + e.g. linear flow type can be
    # at the end of df
    # check last 22 rows to see if they contain model_boundary
    # if so change other flowtypes to other:
    last_n_rows = 22
    if 'model_boundary' in df.tail(last_n_rows)['flowtype'].to_list():
        df.iloc[-last_n_rows:,df.columns.get_loc('flowtype')].loc[df['flowtype']!='model_boundary'] = 'other'



    #repair bi-/linear after steep stiuations
    #where fz reacts first as bc but the stabilzes in bilinear or linear flow regime
    #happens only with t_hour > 0.2 = index > 44
    #account only for situations with more than 6 points of bi-/linear flow



    #df_m.loc[0:3,]
    #df = df_m



    # search and pick bi-/linear parts after steep

    #if found this will store all lists relevant index ranges
    #type list of lists
    potential_indexlist_list = []
    keywords = ['linear','bilinear']
    n = 44
    while n < (entry_length-1):

        if df['flowtype'][n] == 'steep':
            #CHECK THE FOLLOWING POINT
            start_i = 0
            end_i = 0
            for each_key in keywords:
                if df['flowtype'][n+1] == each_key:
                    #criterium found now endpoint of found flowregime
                    local_i = n+1
                    start_i = local_i
                    while local_i < (entry_length):
                        if df['flowtype'][local_i] == each_key:
                            local_i += 1
                        else:
                            #flow type not found anymore --> take index befor and save as last flowtype entry
                            end_i = local_i-1
                            #end local search
                            local_i = entry_length
                            #skip steep search for these lines since its not necesarry
                            n = end_i
                            #now check if more than 6 points in that flow regime follow
                            if end_i-start_i+1 > 6:
                                c_indexlist = range(start_i,end_i+1)
                                potential_indexlist_list.append(c_indexlist)
                    break

            #often it is the case that steep is followed by positive and then bi-/linear
            if df['flowtype'][n+1] == 'positive':
                local_i = n+2 #+2 to check cell after the detected 'positive'
                while local_i < (entry_length-1):
                    for each_key in keywords:
                        if df['flowtype'][local_i] == each_key:
                            start_i = local_i
                            local_local_i = local_i
                            while local_local_i < (entry_length):
                                if df['flowtype'][local_local_i] == each_key:
                                    local_local_i += 1
                                else:
                                    #flow type not found anymore --> take index befor and save as last flowtype entry
                                    end_i = local_local_i-1
                                    #end local local search
                                    local_local_i = entry_length
                                    local_i = entry_length
                                    #skip steep search for these lines since its not necesarry
                                    n = end_i
                                    #now check if more than 6 points in that flow regime follow
                                    if end_i-start_i+1 > 3:
                                        c_indexlist = range(start_i,end_i+1)
                                        potential_indexlist_list.append(c_indexlist)
                            break
                        else:
                            #end local search
                            local_i += 1

        #if one range has been found n will be set to end and search can continue
        # so it is possible to find more than one range of indices
        n += 1


    confirmed_index_lists = []

    # check for those points if dp_slope changes less than 0.001 in more than 2 obersvations
    if len(potential_indexlist_list) > 0:
        for each in potential_indexlist_list:
            df_isolated = df.loc[each].reset_index()

            #calc dP_slope_slope:
            append_linear_slope(df_isolated,'dP_slope')

            #check if DER slope and dP slope are similar
            DER_dP_comp = np.isclose(df_isolated['DER_slope'],df_isolated['dP_slope'],rtol=0.15)

            if len(each) > 10:
                #test criteria:
                testing_confirmation = abs(df_isolated['dP_slope_slope']) < 0.02
                if True in testing_confirmation.to_list() and True in DER_dP_comp:
                    if testing_confirmation.value_counts()[True] > 1:
                        confirmed_index_lists.append(each)
            else:
                #test criteria:
                testing_confirmation = abs(df_isolated['dP_slope_slope']) < 0.001
                if True in testing_confirmation.to_list() and True in DER_dP_comp:
                    if testing_confirmation.value_counts()[True] > 1:
                        confirmed_index_lists.append(each)



    faultzone_bd_detected = False

    if len(confirmed_index_lists) > 0:

        faultzone_bd_detected = True

        for each in confirmed_index_lists:
            #get original df index of first bi-/linear flow entry
            rep_i = rep_end = each[0]-1
            rep_start = 0
            #go back over original df, find indices to repair:
            while rep_i > 0:
                if df['flowtype'][rep_i] == 'steep' and df['flowtype'][rep_i-1] != 'steep':
                    rep_start = rep_i
                    rep_i = 0
                else:
                    rep_i -=1

            #take rep_indices and change entries to positive flowtype:
            rep_indices = range(rep_start,rep_end+1)
            df.loc[rep_indices,'flowtype'] = 'positive'

            #print('repair done')



    return df, faultzone_bd_detected





def classify_datapoints(df_p_curve,params_for_p_curve):
    df = df_p_curve
    if not 't_hour' in list(df_p_curve.columns):
        #df = append_th_file(df)
        df = fast_append_th_file(df)
    if not 'DruckAenderung' in list(df_p_curve.columns):
        #df = append_dP_file(df)
        df = fast_append_dP_file(df)
    #df = append_DER_file(df)
    df = fast_append_DER_file(df)
    #df = append_slope_file(df)
    df = fast_append_slope_file(df)
    #df = append_pressure_slope_file(df) #not neede anymore got integrated into append_DER_file()

    #df = real_linear_marker(df)
    #df = bilinear_marker(df)
    #df = greater_than_andsame_marker(df)
    #df = append_pos_slop_fil(df)
    #df = append_pos_slop_fil_fast(df)
    #df = append_neg_slop_fil(df)

    df = fast_linear_bilinear_steep_neg_pos_marker(df)
    #df = identify_bc(df)
    df = identify_radial(df)
    df, faultzone_bd_detected = append_flow_typ(df,params_for_p_curve['k_matrix'])
    return df, faultzone_bd_detected




def determine_main_flow_type_light(df_p_curve,params_for_p_curve,index_of_headline='not given',verb=0):

    df, faultzone_bd_detected = classify_datapoints(df_p_curve,params_for_p_curve)

    #skip early time for interpretation:
    start_index = 44 #corresponds to 0.199 hours
    sens_start_index = 35
    if (df.loc[start_index:,'flowtype'] == 'steep').any():
        main_flow_type = 'steep'
    elif (df.loc[sens_start_index:,'flowtype'] == 'linear').any() and (df.loc[sens_start_index:,'flowtype'] == 'bilinear').any():
        #check if only one linear but multiple bilinear
        #if true set to bilinear:
        list_linear_true = df.loc[sens_start_index:,'flowtype'] == 'linear'
        if list_linear_true.value_counts()[True] > 3:
            main_flow_type = 'linear'
        else:
            main_flow_type = 'bilinear'
    elif (df.loc[sens_start_index:,'flowtype'] == 'linear').any():
        list_linear_true = df.loc[sens_start_index:,'flowtype'] == 'linear'
        if list_linear_true.value_counts()[True] > 1:
            main_flow_type = 'linear'
    elif (df.loc[sens_start_index:,'flowtype'] == 'bilinear').any():
        list_bilinear_true = df.loc[sens_start_index:,'flowtype'] == 'bilinear'
        if list_bilinear_true.value_counts()[True] > 1:
            main_flow_type = 'bilinear'
    elif (df.loc[30:,'flowtype'] == 'radial').any():
        main_flow_type = 'radial'
    elif (df.loc[start_index:,'flowtype'] == 'well_effect').any():
        main_flow_type = 'steep'
    else:
        #safty for strange param combs with no obvious flow type
        if (df.loc[:,'flowtype'] == 'positive').any():
            main_flow_type = 'unspecifiable_hydr_changes'
        else:
            main_flow_type = 'not_determined'

            if verb == 1:
                print('could not determine main_flow_type_doublecheck')
                print(params_for_p_curve)
                print('current row id of paramset: '+str(index_of_headline))


    return df, main_flow_type, faultzone_bd_detected


'''
#example usage
p_curve_params = {"k_matrix":1.0e-13,
                  "matrix_poro":0.001,
                  "fault_permeability":1.0e-9,
                  "fault_poro":0.001,
                  "fault_thickness":20.0,
                  "production_rate":30.0,
                  "fluid_viscosity":0.00028974
                  }


df = pd.read_csv('/media/hombre/Dropbox_SSD/Dropbox/Work-Folder/3_Prom/12_STZ_2.0/2_Stz_productivity_study/2_Python/test_files/V1_STZ2.0_with_stressscaling_out.csv')

df, main_flow_type = determine_main_flow_type(df,p_curve_params)
'''
