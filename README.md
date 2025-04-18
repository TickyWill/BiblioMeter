# BiblioMeter
## Description
Python application for bibliometric purpose based on analysis of publications metadata extracted from databases such as Scopus and WoS.<br />
More specifically:<br />
- Parse Scopus and WoS corpuses;
- Merge Scopus and WoS corpuses taking care of the duplicates;
- Recursively dispatch the articles per department using the employees database;
- Take care of the authors homonimies (user action required);
- Take care of the authors affiliated to the Institute but not found in the employees database;
- Computes key performance indicators (impact factors, collaborations and keywords occurrences...).

## Installation
Run the following command to get a repository clone of the orphan_treatment_enhancement branch:
```
git clone https://github.com/TickyWill/BiblioMeter.git@main
```

## Requirements
Ensure that your environment complies with the requirements given in the following file:
<p><a href=https://github.com/TickyWill/BiblioMeter/blob/main/requirements.txt>BiblioMeter requirements file
</a></p>

## Documentation building
Run the following commands to build the sphinx documentation:
- Only in case of a previous building
```
docs\make.bat clean
```
- Then
```
docs\make.bat html
```

## Documentation edition
Open the following BiblioMeter sphinx-documentation html file:
>docs/docbuild/html/index.html

## Building executable
Either run the following batch file:
<p><a href=https://github.com/TickyWill/BiblioMeter/blob/main/BiblioMeterBuildExe.bat>BiblioMeter executable-building batch file
</a></p>
Or refer to the following manual:
<p><a href=https://github.com/TickyWill/BiblioMeter/blob/main/BiblioMeterBuildExeManual-Fr.pdf>BiblioMeter executable-building manual
</a></p>
<span style="color:red">BEWARE:</span> Some security softwares (eg. McAfee) could place the .exe file in quarantine. If so you have to manually authorized the .exe file.

## Usage example
```python
# Local imports
from bmgui.main_page import AppMain

app = AppMain()
app.mainloop()
```

**for more details on application usage refer to the user manual:** 
<p><a href=https://github.com/TickyWill/BiblioMeter/blob/main/BiblioMeterUserManual-Fr.pdf>BiblioMeter user manual
</a></p>

# Release History
- 1.0.0 first release
- 1.1.0 code refactoring release
- 4.0.0 Extension to different institutes
- 5.0.0 Introduction of progress bars, pylint refactoring of code and Sphynx documentation
- 5.1.0 Enhanced orphan authors treatment
- 6.0.0 Enhanced OTPs treatment
- 6.1.0 Enhanced collaborations analysis

# Meta
	- authors: BiblioAnalysis team

Distributed under the [MIT license](https://mit-license.org/)
