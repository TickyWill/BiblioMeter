# Application Release Backlog

## Release 6.0.0 - 2024/12/16
* **Summary**: This release corresponds to the deep update of the code allowing the attribution of the OTPs at either the laboratory level or the department level of the Institute. In addition, it corresponds to a code refactory distributing existing functions in different specific modules.
* **Features**:
  - Feature 1: Creation of functions allowing attribution of OTPs at laboratory level with upgrade of the "<institute>Org_config.json" config file.
  - Feature 2: Creation of "format_files" module of functions for formatting openpyxl workbooks.
  - Feature 3: Creation of "use_homonyms" module of functions for homonymies resolution and its history keeping and use.
  - Feature 4: Creation of "build_otps_info" module of functions for building OTPs info.
  - Feature 5: Creation of "add_otps" module of functions to help the user adding OTP attribute to each publication with info given at laboratory level or at department level.
  - Feature 6: Creation of "use_otps" module of functions for setting and using history of OTPs attribution.
  - Feature 7: Creation of "add_ifs" module of functions for adding impact-factor to each publication.
  - Feature 8: Redistribution of "pub_analysis" module into the specialized modules "coupling_analysis", "impact_factors_analysis" and "keywords_analysis" complementing the "authors_analisis" module.
* **Improvements**:
  - Improvement 1: Management of setting OTPs info at laboratory level or at department level depending on Institute choice.
  - Improvement 2: Introduction of building OTPs info from a structured EXCEL file specific to the Institute.
  - Improvement 3: Update of code docstrings.
  - Improvement 4: Use of enhanced functions for formatting openpyxl workbooks to save results.
  - Improvement 5: Set of default working folder taking into account the application version.
* **Bug Fixes**:
  - None.
* **Known Issues**:
  - Issue 1: Displaying Sphinx documentation correctly on GitHub repository.
* **API Changes**:
  - None.
* **Deprecated Features**:
  - None.
* **Contributors**: Amal Chabli.
* **Acknowledgments**: Thanks to Baptiste Refalo for pull requests review.

## Release 5.1.0 - 2024/11/12
* **Summary**: This release corresponds to the deep update of the code allowing an enhanced analysis of the authors affiliations and attributes. In addition, it allows to display progress bars within the GUI and to edit infos on the code through docstrings and Sphinx documentation.
* **Features**:
  - Feature 1: Addition of scientifique production by authors.
  - Feature 2: Use of progress bars displaying data processing tasks in progress.
  - Feature 3: Complementary authors attributes to the Institute authors list.
  - Feature 4: Use of 'Insitute_Country_towns.xlsx' file to parse affiliations for the coupling analysis according to the selected Institute.
  - Feature 5: Set of ad-hoc rawdata in the working folder using an updated folder architecture based on 3 combination types of data.
* **Improvements**:
  - Improvement 1: Introduction of standardization of last names of authors and employees for better efficiency in similarity tests for merge of employees information in publications list and therfore get more efficient automatic reduction of orphan authors list.
  - Improvement 2: Addition of tools for building Sphinx documentation.
  - Improvement 3: Code docstrings added.
  - Improvement 4: Enhancement by saving invalid-publications list.
  - Improvement 5: Final save of deduplication-parsing results for each combination of data type.
  - Improvement 6: Removed production of graphical representations of analysis results.
  - Improvement 7: Deep modification of Institute authors identification based on new parsing of authors with institutions in BiblioParsing package.
* **Bug Fixes**:
  - Bug 1: Fixed a bug in homonyms management when several authors of the same publication have homonyms through refactoring of `set_saved_homonyms`  function in `use_pub_attributes` module.
* **Known Issues**:
  - Issue 1: Displaying Sphinx documentation correctly on GitHub repository.
* **API Changes**:
  - None.
* **Deprecated Features**:
  - Feature 1: Creation of html-plots files and wordcloud-plots files in `pub_analysis` module.
* **Contributors**: Amal Chabli, Baptiste Refalo and François Bertin.
* **Acknowledgments**: Thanks to Ludovic Desmeuzes for the initial developpement of the GUI package.

---
```
(Repeat the above structure for each release, with the most recent releases at the top of the file.)
```

