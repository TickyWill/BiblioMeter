""" The `BiblioSys` module is a set of system-management functions
for running BiblioAnalysis on different operating systems.
"""

__all__ = ['add_site_packages_path',
           'DISPLAYS',
           'GUI_DISP',]

# Globals used from BiblioAnalysis_Utils.BiblioGeneralGlobals: IN_TO_MM


def add_site_packages_path(venv = False ):
    ''' The function `add_site_packages_path` adds `site_packages` path to `sys.path`
    for MacOs when not working with virtual environment.
    
    Args:
        os_name (str): name of the operating system ('Darwin' or 'Windows')
        venv (bool): status of virtual environment use.
        
    '''
    # To Do: convert prints and inputs to gui displays and inputs
    
    # Standard library imports
    import os
    import sys
    
    ## Get the information of current operating system
    if venv==False:
        # Add path of 'site-packages' where useful packages are stored on MacOS;
        # no impact for Windows
        packages_dir = 'site-packages'
        search_path = '/Library/Frameworks/Python.framework/Versions/current/lib'
        for root, dirs, files in os.walk(search_path):
            list_packages = [os.path.abspath(os.path.join(root, name)) for name in dirs if name == packages_dir ]
            if list_packages != []: mac_packages = list_packages[0]   
        sys.path.append(mac_packages)
        print('Added paths:         ',mac_packages)
        

def _get_displays(in_to_mm=None): 
    
    ''' The function `get_displays` allows to identify the set of displays
        available within the user hardware and to get their parameters.
        If the width or the height of a display are not available in mm 
        through the `get_monitors` method (as for Darwin platforms), 
        the user is asked to specify the displays diagonal size to compute them.
        
    Returns:
        `list`: list of dicts with one dict per detected display,
                each dict is keyed by 8 display parameters.   
    '''
    # To Do: convert prints and inputs to gui displays and inputs
    
    # Standard library imports
    import math
    
    # 3rd party imports
    from screeninfo import get_monitors
    
    # Local imports
    from BiblioAnalysis_Utils.BiblioGeneralGlobals import IN_TO_MM

    if in_to_mm==None: in_to_mm = IN_TO_MM
    
    displays = [{'x':m.x,'y':m.y,'width':m.width,
                 'height':m.height,'width_mm':m.width_mm,
                 'height_mm':m.height_mm,'name':m.name,
                 'is_primary':m.is_primary} for m in get_monitors()]
    

    print('Number of detected displays:',len(displays))
    
    for disp in range(len(displays)):
        width_px = displays[disp]['width']
        height_px = displays[disp]['height']
        diag_px = math.sqrt(int(width_px)**2 + int(height_px)**2)    
        width_mm = displays[disp]['width_mm']
        height_mm = displays[disp]['height_mm']
        if width_mm is None or height_mm is None: 
            diag_in = float(input('Enter the diagonal size of the screen n°' + str(disp) + ' (inches)'))
            width_mm = round(int(width_px) * (diag_in/diag_px) * in_to_mm,1)
            height_mm = round(int(height_px) * (diag_in/diag_px) * in_to_mm,1)
            displays[disp]['width_mm'] = str(width_mm)
            displays[disp]['height_mm'] = str(height_mm)
        else:
            diag_in = math.sqrt(float(width_mm) ** 2 + float(height_mm) ** 2) / in_to_mm
        displays[disp]['ppi'] = round(diag_px/diag_in,2)
        
    return displays

######################## Definition of globals ###########################

DISPLAYS = _get_displays()

   # Get the prime display choice
   # TO DO: replace input by a GUI to select the gui display for the whole run of BiblioAnalysis
displays_nb = len(DISPLAYS)
GUI_DISP = [i for i in range(displays_nb) if DISPLAYS[i]['is_primary']][0]
if displays_nb>1:
    disp_select = input('\nSelect Id of gui prime-display '+
                       '(value: 0 to '+ str(displays_nb-1)+
                      '; default:'+ str(GUI_DISP)+')')
    if disp_select: GUI_DISP = int(disp_select)  