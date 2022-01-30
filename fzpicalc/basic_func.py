

import re
import numpy as np
import sys,math

def getNumbers(str): 
    array = re.findall(r'[0-9]+', str) 
    return array 

def normalize(inputvalue, valuemin, valuemax): 
    if valuemax == valuemin:
        print('warning: normalisation returned 0: max and min are the same')
        return 0
    else:
        return (inputvalue - valuemin) / float(valuemax - valuemin)
   
def tidy( x, n):
    
    """Return 'x' rounded to 'n' significant digits."""
    
    if np.isnan(x) == True: 
        return np.NaN
    
    y=abs(x)
    
    if y <= sys.float_info.min: 
        return 0.0
    
    return round( x, int( n-math.ceil(math.log10(y)) ) )

def colorize_a_value(value,v_min,v_max,colormap):
    normalized_value = normalize(value,v_min,v_max)
    c = colormap(normalized_value,1)
    rgb = c[:3]
    rgb = "rgb(%s, %s, %s)" % (int(rgb[0]*255),int(rgb[1]*255),int(rgb[2]*255))
    return rgb

def matplotlib_to_plotly(cmap, pl_entries=255):
    h = 1.0/(pl_entries-1)
    pl_colorscale = []

    for k in range(pl_entries):
        C = map(np.uint8, np.array(cmap(k*h)[:3])*255)
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale

def colorlookup_mft(name):
    name_to_color = {
                     'linear':'#FF7A03',
                     'bilinear':'#FFDF00',
                     'radial':'#00ADB0',
                     'steep':'#D60301',
                     'unspecifiable_hydr_changes':'#C5D9D9'}
    return name_to_color[name]

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

def magnitude (value):
    if (value == 0): return 0
    return int(math.floor(math.log10(abs(value))))


