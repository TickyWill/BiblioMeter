# Application Release Backlog

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

