"""The `app` module launch the 'BiblioMeter' application through `app_main` class
of `Page_Classes` module of `BiblioMeter_GUI` package.
"""

# !/usr/bin/env python
# coding: utf-8

# In[ ]:

# Local imports
from bmgui.main_page import AppMain

try:
    app = AppMain()
    app.mainloop()
except Exception as err:
    print(err)
# In[ ]:
