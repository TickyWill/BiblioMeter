"""The `app` module launch the 'BiblioMeter' application through `AppMain` class
of `main_page` module of `bmgui` package.
"""


# Local imports
from bmgui.main_page import AppMain

def run_bibliometer():
    """
    Main function used for starting the BiblioMeter application
    """
    try:
        app = AppMain()
        app.mainloop()
    except Exception as err:
        print(err)

if __name__ == "__main__":
    run_bibliometer()
