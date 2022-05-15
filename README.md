# The Owl House Character Dialogue Search 

**Version 1.0.0**

A web scraper tool made for saving dialogue of a selected character from Owl House transcripts found at https://theowlhouse.fandom.com/wiki/Category:Transcripts to a text file.

**Requirements to run this program:**
* Chrome browser is installed
* Click The_Owl_House_Character_Dialogue_Search.exe to run
* Alternatively, if Python and required libraries (selenium, tkinter, PIL) are installed, The_Owl_House_Character_Dialogue_Search.py can be ran in IDLE
* Transcript_Dialogue_Web_Scraper.py can also be run though IDLE with Python and the same required libraries installed. It is a simplifed version of the application. No UI provided. Character name being searched must be provided on line 6.

**Features:**
* Dropdown selection to search for dialogue from a single or multiple characters
* Dropdown selection to search through a single, mulitple, or all episode transcripts
* Updatable character list in case of new characters being added
* Character dialogue information, including words most often used and total words spoken, provided after each search

**Known issues:**
* Sometimes after the search has been completed, it will repeat
* If program fails on start-up before UI is loaded, there may be an issue with the chromedriver.exe. Please ensure your Chrome version is up-to-date and download latest stable chromedriver from https://chromedriver.chromium.org/downloads. Replace chromedriver.exe in program folder with newer version
