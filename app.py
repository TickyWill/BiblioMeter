"""
The `app` module launch the 'BiblioMeter' application through `AppMain` class
of `main_page` module of `bmgui` package.
"""


# Local imports
from bmgui.main_page import AppMain

try:
    app = AppMain()
    app.mainloop()
except Exception as err:
    print(err)
