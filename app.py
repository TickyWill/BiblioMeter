"""The `app` module launch the 'BiblioMeter' application through `AppMain` class
of `main_page` module of `bmgui` package.
"""

# Local imports
from bmgui.main_page import AppMain

def run_application():
    """ Main function used for starting the BiblioMeter application.
    """
    app = AppMain()
    app.mainloop()

if __name__ == "__main__":
    run_application()
