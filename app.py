"""The `app` module launch the 'BiblioMeter' application through `AppMain` class
of `main_page` module of `bmgui` package.
"""

# Local imports
from bmgui.main_page import AppMain

if __name__ == "__main__":
    app = AppMain()
    app.mainloop()
