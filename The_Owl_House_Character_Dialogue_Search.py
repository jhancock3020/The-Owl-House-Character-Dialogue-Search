import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import *

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from PIL import ImageTk, Image

from collections import Counter

import os

#Set up for driver
options = Options()
options.headless = True
options.add_argument("--headless")

#Gets current path of program to know where the chromedriver currently is
cwd = os.getcwd()

#Webscrapper
driver = webdriver.Chrome(executable_path= cwd + "\chromedriver.exe",options=options)
driver.get("https://theowlhouse.fandom.com/wiki/Category:Transcripts")

#Search main transcript page and get links to all episode transcripts
elements = driver.find_elements(By.CSS_SELECTOR,("div.category-page__members-wrapper a"))
episodeTranscriptUrls = []
names = []
for element in elements:
    if "Category:" not in element.get_attribute("href"):
        episodeTranscriptUrls.append(element.get_attribute("href"))
numOfUrls = len(episodeTranscriptUrls)

#Create program window
window = tk.Tk()
window.resizable(width=False,height=False)
window.title('TOHCDS (Version 1.0.0)')
window.geometry('600x720')
##logoImg = Image.open(cwd + '\img\logo.png')
##logoImg.save('logo.ico',format='ICO',sizes=[(32,32)])
window.wm_iconbitmap(cwd + '\img\logo.ico')

#Fram in window where all UI features are placed. Used for best practice
frame = tk.Frame(window,width=600,height=720)
frame.grid()
frame.columnconfigure(1,minsize=600,weight=0)

#Frames will be added to grid so buttons can be next to each other
episodeFrame = tk.Frame(frame)
characterFrame = tk.Frame(frame)
statsFrame = tk.Frame(frame)

#If reset episode button is clicked, the selected episodes list is cleared, and search button is disabled until new
#selected episode is added
def resetSelectedEpisodes():
    selectedEpisodes.clear()
    selectEpisodeLabel['text'] = "Select episode(s) : "
    episodeButtonSelect["state"] = "normal"
    searchButton["state"] = "disabled"
    searchButton["text"] = "Now select episode"
    frame.update()
#If reset character button is clicked, the selected characters list is cleared, and search button is disabled until new
#selected character is added. Character Dialogue stats are also cleared to avoid error
def resetSelectedCharacters():
    statsFrame.grid_forget()
    characterDialogueStatsLabel.grid_forget()
    selectedCharacters.clear()
    selectCharacterLabel['text'] = "Select episode(s) : "
    searchButton["state"] = "disabled"
    searchButton["text"] = "Now select character"
    frame.update()
#Update character dropdown in case new characters are introduced in new episodes
def updateCharacterList():
    #Display loading label and bar
    loadingLabel.grid(column=1, row=12)
    loadingBar.grid(column = 1,row = 13)
    loadingLabel['text'] = "Please wait..."
    loadingBar['value'] = 0
    frame.update()
    transcriptsSearchedSoFar = 0
    newEpisodeTranscriptUrls = []
    newCharacters = []
    #Go through list of transcripts. If a transcript is found not to be in list of current episodes (as of 5/13/22)
    #Add that transcript to list that will be searched
    for url in episodeTranscriptUrls:
        transcriptName = url.replace('https://theowlhouse.fandom.com/wiki/','')
        transcriptName = transcriptName.replace('/Transcript','')
        if transcriptName not in currentEpisodes:
            newEpisodeTranscriptUrls.append(url)
    totalNumOfSearchedTranscripts = len(newEpisodeTranscriptUrls)
    percentNumOfASingleTranscript = 100/totalNumOfSearchedTranscripts
    #Go through 'new' transcripts
    for url in newEpisodeTranscriptUrls:
        transcriptName = url.replace('https://theowlhouse.fandom.com/wiki/','')
        transcriptName = transcriptName.replace('/Transcript','')
        transcriptsSearchedSoFar += 1
        loadingLabel['text'] = "Please wait, searching for new characters in '" + transcriptName + "' (" + str(transcriptsSearchedSoFar) + " / " + str(totalNumOfSearchedTranscripts) + ")..." #f"Current loadingBar: {loadingBar['value']}%"
        frame.update()
        driver.get(url)
        #Get all html elements on page of this type, which is where transcript dialogue is held
        elements = driver.find_elements(By.CSS_SELECTOR,("div.mw-parser-output p"))
        for element in elements:
            #Trim string so only '<name>:' is in string. If '&', replace with ' ' to make check easier
            colonChar = ':'
            bracketChar = '['
            searchSubstring = element.text[0:element.text.find(colonChar)]
            searchSubstring.replace('&',' ')
            altVersionOfName = False
            #Check if character is in dropdown
            for characterName in characterSelectionDropdown['values']:
                if(characterName in searchSubstring):
                    altVersionOfName = True
            #If name not in list, colon is in string (which means dialogue) and bracket not in string
            #(which means line is not dialogue), add character name to new character list
            if(colonChar in element.text and bracketChar not in element.text and altVersionOfName == False):
                newCharacters.append(element.text[0:element.text.find(colonChar)])
        loadingBar['value'] += percentNumOfASingleTranscript
        numberOfNewCharacters = len(newCharacters)
    #New characters list converted to tuple to be added to character dropdown 
    newCharactersTuple = tuple(newCharacters)
    characterSelectionDropdown['values'] += newCharactersTuple
    loadingLabel['text'] = "Completed search for new characters to add to list. " + str(numberOfNewCharacters) + " new characters added."
    frame.update()
def selectEpisode():
    #If episode not in selection, add it to selected list
    if episodeSelectionDropdown.get() not in selectedEpisodes:
        selectedEpisodes.append(episodeSelectionDropdown.get())
    #If 'All episodes' selected, make that option the only one in selected list and don't allow additional episodes
    if "All episodes" in selectedEpisodes:
        selectedEpisodes.clear()
        selectedEpisodes.append("All episodes")
        episodeButtonSelect["state"] = "disabled"
    #Print selected episodes   
    selectedEpisodeListForLabel = ""
    for selectedCharacterIndex,selectedEpisodeName in enumerate(selectedEpisodes):            
        selectedEpisodeListForLabel += selectedEpisodeName
        if(len(selectedEpisodes) != 1 and selectedCharacterIndex + 1 < len(selectedEpisodes)):
            selectedEpisodeListForLabel += ", "
    selectEpisodeLabel['text'] = "Select episode(s) : " + selectedEpisodeListForLabel
    #If episode and character selected, allow search
    if selectedEpisodes and not selectedCharacters:
        searchButton["text"] = "Now select character"
    elif selectedEpisodes and selectedCharacters:
        searchButton["state"] = "normal"
        searchButton["text"] = "Click to search for dialogue"
    frame.update()
def selectCharacter():
    #If character not in selection, add it to selected list
    if characterSelectionDropdown.get() not in selectedCharacters:
        selectedCharacters.append(characterSelectionDropdown.get())
        selectedCharacterDialogueList.append("")
    #Print selected characters
    selectedCharacterListForLabel = ""
    for selectedCharacterIndex,selectedCharacterName in enumerate(selectedCharacters):
        selectedCharacterListForLabel += selectedCharacterName
        if(len(selectedCharacters) != 1 and selectedCharacterIndex + 1 < len(selectedCharacters)):
            selectedCharacterListForLabel += ", "
    selectCharacterLabel['text'] = "Select character(s) : " + selectedCharacterListForLabel
    
    #If episode and character selected, allow search
    if not selectedEpisodes and selectedCharacters:
        searchButton["text"] = "Now select episode"
    elif selectedEpisodes and selectedCharacters:
        searchButton["state"] = "normal"
        searchButton["text"] = "Click to search for dialogue"
    frame.update()
#Depending on characterDialogueStatsIndex is pointing, will display dialogue stats for the character at that
#selected character list index
def displayCharacterDialogueStats():
    global characterDialogueStatsIndex
    #Update character name displayed
    currentCharacterStatNameLabel['text'] = selectedCharacters[characterDialogueStatsIndex]
    #Checks where index is just to be safe
    checkCharacterDialogueStatsIndex()
    #If the character at that index has dialogue greater than zero
    #turn that dialogue string into a list in order to find total number of words and most used words
    if len(selectedCharacterDialogueList[characterDialogueStatsIndex]):
        dialogueList = selectedCharacterDialogueList[characterDialogueStatsIndex].split()
        characterDialogueStatsLabel['text'] = "Total word count is " + str(len(dialogueList)) + " words \n"
        bannedWords = ['a','you','I','the','and','or','to','in','on','that']
        for word in dialogueList:
            for bannedWord in bannedWords:
                if word == bannedWord:
                    dialogueList.remove(word)
        split = Counter(dialogueList)
        topFiveWordsDict = split.most_common(5)
        characterDialogueStatsLabel['text'] += "Most Common Words Used: \n"
        for index in range(5):
            topWordsAsTuple = topFiveWordsDict[index]
            characterDialogueStatsLabel['text'] += str(index + 1) + ") '" + str(topWordsAsTuple[0]) + "' said " + str(topWordsAsTuple[1]) + " times \n"
    else:
        characterDialogueStatsLabel['text'] = "No dialogue found for " + selectedCharacters[characterDialogueStatsIndex] + "!"
#Tracks characterDialogueStatsIndex, which is where the selected character list is currently pointing
#If it is pointing at either end of list, either the increase or decrease button is disabled
def checkCharacterDialogueStatsIndex():
    global characterDialogueStatsIndex
    if characterDialogueStatsIndex >= len(selectedCharacters) - 1:
        statsButtonIncrease["state"] = "disabled"
    if characterDialogueStatsIndex <= 0:
        statsButtonDecrease["state"] = "disabled"
#If in range, characterDialogueStatsIndex increased by one. If at end of selected character list, disable increase
def characterDialogueStatsIncrease():
    global characterDialogueStatsIndex
    if characterDialogueStatsIndex < len(selectedCharacters) - 1:
        characterDialogueStatsIndex += 1
        currentCharacterStatNameLabel['text'] = selectedCharacters[characterDialogueStatsIndex]
        displayCharacterDialogueStats()
    else:
        statsButtonIncrease["state"] = "disabled"
    if characterDialogueStatsIndex > 0:
        statsButtonDecrease["state"] = "normal"
#If in range, characterDialogueStatsIndex decreased by one. If at beginning of selected character list, disable decrease
def characterDialogueStatsDecrease():
    global characterDialogueStatsIndex
    if characterDialogueStatsIndex > 0:
        characterDialogueStatsIndex -= 1
        currentCharacterStatNameLabel['text'] = selectedCharacters[characterDialogueStatsIndex]
        displayCharacterDialogueStats()
    else:
        statsButtonDecrease["state"] = "disabled"
    if characterDialogueStatsIndex < len(selectedCharacters) - 1:
        statsButtonIncrease["state"] = "normal"
def searchTranscripts():
    #Clear character dialogue stats information
    statsFrame.grid_forget()
    characterDialogueStatsLabel.grid_forget()
    #Show new loading information
    loadingLabel.grid(column=1,row=12)
    loadingBar.grid(column=1,row=13)
    loadingLabel['text'] = "Please wait..."
    loadingBar['value'] = 0
    frame.update()
    #Loading display changes depends on if "All episodes" was selected or not
    totalNumOfSearchedTranscripts = 0
    if "All episodes" in selectedEpisodes:
        totalNumOfSearchedTranscripts = len(episodeTranscriptUrls)
        percentNumOfASingleTranscript = 100/totalNumOfSearchedTranscripts
    else:
        totalNumOfSearchedTranscripts = len(selectedEpisodes)
        percentNumOfASingleTranscript = 100/totalNumOfSearchedTranscripts
    characterNameListForFileTitle = ""
    #Get selected character list as a string for txt file title and later loading label display
    for characterNameIndex,characterName in enumerate(selectedCharacters):
        characterNameListForFileTitle += characterName
        if(len(selectedCharacters) != 1 and characterNameIndex + 1 < len(selectedCharacters)):
            characterNameListForFileTitle += " & "
    #Create/Override new character dialogue output file
    dialogueFileTitle = characterNameListForFileTitle + ".txt"
    dialogueFile = open(cwd + "\Dialogue_Output_Files\Dialogue_" + dialogueFileTitle, "w", encoding="utf-8")
    #Clears file if text already there
    dialogueFile.truncate(0)
    transcriptsSearchedSoFar = 0
    #Search through trnascript URLs
    for url in episodeTranscriptUrls:
        #Trims URL down to only proper episode name
        transcriptName = url.replace('https://theowlhouse.fandom.com/wiki/','')
        transcriptName = transcriptName.replace('/Transcript','')
        transcriptName = transcriptName.replace('_',' ')
        transcriptName = transcriptName.replace('%27',"'")
        #If transcript name in selected episode list, proceed with serach
        if transcriptName in selectedEpisodes or "All episodes" in selectedEpisodes:
            loadingLabel['text'] = "Please wait, searching for " + characterNameListForFileTitle + " dialogue in '" + transcriptName + "' (" + str(transcriptsSearchedSoFar) + " / " + str(totalNumOfSearchedTranscripts) + ")..." #f"Current loadingBar: {loadingBar['value']}%"
            frame.update()
            transcriptsSearchedSoFar += 1
            #In txt file, on a new line, give episode URL/title
            dialogueString = " \n"
            dialogueFile.write(dialogueString)
            dialogueString = str(transcriptsSearchedSoFar) + " " + url + "\n"
            dialogueFile.write(dialogueString)
            dialogueString = " \n"
            dialogueFile.write(dialogueString)
            driver.get(url)
            #Get all html elements on page of this type, which is where transcript dialogue is held and
            #go through each one
            elements = driver.find_elements(By.CSS_SELECTOR,("div.mw-parser-output p"))
            for element in elements:
                colonChar = ':'
                #Search through selected characters,
                #if that charcater name matches trimmed element that contains that name
                #add that characters name and dialogue to the txt file and
                #add ONLY dialogue to selectedCharacterDialogueList for later dialogue stat information
                for characterNameIndex,characterName in enumerate(selectedCharacters):
                    if(colonChar in element.text and characterName in element.text[0:element.text.find(colonChar)]):
                        dialogueFile.write(element.text + "\n")
                        characterDialogue = element.text[element.text.find(colonChar):]
                        characterDialogue = characterDialogue.replace(': ','')
                        selectedCharacterDialogueList[characterNameIndex] += characterDialogue
            loadingBar['value'] += percentNumOfASingleTranscript
            frame.update()
    loadingLabel['text'] = "Completed search for " + characterNameListForFileTitle + " dialogue! (" + str(transcriptsSearchedSoFar) + " / " + str(totalNumOfSearchedTranscripts) + ")"
    #Display character dialogue stat information
    statsFrame.grid(column = 1,row = 14)
    characterDialogueStatsLabel.grid(column = 1,row = 15)
    displayCharacterDialogueStats()
    frame.update()
    
#Adds Owl House Character Search Engine Logo
img = ImageTk.PhotoImage(Image.open(cwd + "\img\TOHCDS.png"))
ttk.Label(frame,image=img).grid( column = 1,row = 0)

#Episodes and characters the user selects
selectedEpisodes = []
selectedCharacters = []

#Text above character dropdown
selectCharacterLabel = ttk.Label(frame, text = "Select character(s) :",wraplength=150)
selectCharacterLabel.grid(column = 1,row = 5)
  
#Character selection dropdown
strVarCharacter = tk.StringVar()
characterSelectionDropdown = ttk.Combobox(frame,state="readonly", width = 27, textvariable = strVarCharacter)
characterSelectionDropdown['values'] = ['3-headed demon', 'Abomination', 'Adegast', 'Alador', 'All', 'Amber', 'Amelia', 'Amity', 'Angmar', 'Anne', 'Announcer', 'Audience', 'Author #1', 'Author #2', 'Author #3', 'Author #4', 'BATTs', 'Baby', 'Baker', 'Basilisk', 'Bat Queen', 'Beefy Bob', 'Belos', 'Bill', 'Bird', 'Blond Romance Lead', 'Bo', 'Book', 'Boscha', 'Bowtie', 'Boy', 'Braxas', 'Bria', 'Bystander', 'Camila', 'Candy Vendor', 'Carnivorous Plant', 'Cat', 'Celine', 'Chris', 'Citizen #1', 'Citizen #2', 'Class', 'Collector', 'Coven Scout', 'Coven Scouts', 'Crowd', 'Cursed Skull', 'Customer #1', 'Customer #2', 'Customer #3', 'Cyclops demon girl', 'Darius', 'Dark Figure', 'Date', 'Dell', 'Demon 1', 'Derwin', 'Detention Teacher', 'Eda', 'Edric', 'Edric and Emira', 'Eileen', 'Elf', 'Emira', 'Emperor Belos', "Emperor's coven delegate", 'Everyone', 'Eye-Eating Prisoner', 'Eyes', 'Fairy', 'Fan', 'Female student', 'Female townsperson', 'Fish Sailor', 'Flora', 'Garlog', 'Gavin', 'Ghost', 'Giant Boy', 'Gilbert', 'Girl 1', "Girl's voice", 'Glandus High student', 'Green-eyed witch', 'Gremlin', 'Guard', 'Guard #1', 'Guard #2', 'Guard Captain', 'Guest', 'Gus', 'Gwendolyn', 'Harvey', 'Healer', 'Hooded figure', 'Hooty', 'Hop Pop', 'Hunter', 'Inner Belos', 'Inspector', 'Jacob', 'Jerbo', 'Jon De Plume', 'Katya', 'Keeper', 'Kevin', 'Kid #1', 'Kid #2', 'Kids', 'Kikimora', 'King', 'Librarian', 'Lilith', 'Luz', 'Male student', 'Male townsperson', 'Malphas', 'Man', 'Man #2', 'Master Wortlop', 'Mattholomule', 'Member 1', 'Member 2', 'Merchant', 'Monster', 'Monster #1', 'Monster #2', 'Monster #3', 'Morton', 'Music', 'Mustached demon', 'Narration (Dana Terrace)', 'Narration (Matt Braly)', 'Narrator', 'Nevareth', 'Nevereth', 'New Guy', 'Odalia', 'Oracle Teacher', 'Otabin', 'Passerby', 'Peddler', 'People', 'Perry', 'Perry Porter', 'Person 1', 'Person 2', 'Philip', 'Piniet', 'Polly', 'Potions Teacher', 'Previous guard', 'Prim', 'Princess', 'Principal Bump', 'Principal Faust', 'Principal Hal', 'Prize Vendor', 'Professor Hermonculus', 'Pufferfish Guy', 'Purple-haired witch', 'Raine', 'Random investor', 'Rats', 'Recorder player', 'Roselle', 'Salty', 'Security', 'Shadow', 'Shopkeeper', 'Skara', 'Skeleton', 'Snaggleback', 'Someone in the body of a guard', 'Song', 'Spider Teacher', 'Sprig', 'St. Epiderm student', 'Steve', 'Student', 'Student #3', 'Student #4', 'Student #5', 'Sword', 'Tambourine player', 'Tarak', 'Teacher', 'Teacher #1', 'Teacher #2', 'Terra', 'Tibbles', 'Tinella', 'Tiny Nose', 'Townspeople', 'Tunnel of Love', 'Typewriter', 'Unknown', 'Unnamed Oracle student', 'Unnamed demon', 'Usurper', 'Vee', 'Villain', 'Viney', 'Violinist', 'Voice', 'Warden Wrath', 'Welcome Mat', 'Wild witch', 'Willow', 'Woman', 'Worker', 'Wrath', 'Yellow demon with horns']#['Luz', 'Camila', 'Principal Hal', 'Eda', 'Fairy', 'Monster #1', 'Monster #2', 'Monster #3', 'Monster', 'Guard #1', 'Hooty', 'King', 'Katya', 'Tiny Nose', 'Warden Wrath', 'Guard #2', 'Eye-Eating Prisoner', 'New Guy', 'Edric and Emira', 'Amity', 'Emira', 'Edric', 'Lilith', 'Kikimora', 'Bird', 'Gus', 'Willow', 'Principal Bump', 'Class', 'Emperor Belos', 'Narration (Dana Terrace)', 'Narration (Matt Braly)', 'Hop Pop', 'Anne', 'Sprig', 'Polly', 'Hunter', 'Darius', 'Narrator', 'Boscha', 'Unnamed Oracle student', 'Celine', 'Jerbo', 'Viney', 'Voice', 'Professor Hermonculus', 'Skara', 'Hooded figure', 'Steve', 'Tinella', 'Mattholomule', 'Tibbles', 'Announcer', 'Man #2', 'Audience', 'Baker', 'Fan', 'Student #3', 'Student #4', 'Student #5', 'Philip', 'Guard Captain', 'Raine', 'Kevin', 'Wild witch', 'Guard', 'Violinist', 'Tambourine player', 'Recorder player', 'BATTs', 'Derwin', 'Amber', 'Perry Porter', 'Perry', 'Mustached demon', 'Collector', 'Inner Belos', 'Salty', 'Unknown', 'Tarak', 'Demon 1', 'Bill', 'Coven Scouts', 'Woman', 'Flora', 'Person 1', 'Person 2', 'Gwendolyn', '3-headed demon', 'Dell', 'Spider Teacher', 'Worker', 'Student', 'Snaggleback', 'Cat', 'Date', 'Guest', 'Giant Boy', 'All', 'Braxas', 'Bat Queen', 'Usurper', 'Odalia', 'Random investor', 'Alador', 'Harvey', 'Gilbert', 'Terra', 'Coven Scout', 'Belos', 'Bystander', 'Peddler', 'Prim', 'Purple-haired witch', 'Yellow demon with horns', 'Male townsperson', 'Female townsperson', 'Previous guard', 'Green-eyed witch', 'Eyes', 'Shadow', 'Morton', 'Beefy Bob', 'Pufferfish Guy', "Girl's voice", 'Abomination', 'Boy', 'Male student', 'Female student', 'Teacher #1', 'Kids', 'Teacher #2', 'Healer', 'Gremlin', 'Master Wortlop', 'Tunnel of Love', 'Unnamed demon', 'Librarian', 'People', 'Kid #1', 'Kid #2', 'Otabin', 'Man', 'Roselle', 'Bowtie', 'Baby', 'Amelia', 'Music', 'Elf', 'Customer #1', 'Customer #2', 'Customer #3', 'Someone in the body of a guard', 'Dark Figure', 'Wrath', 'Security', 'Oracle Teacher', 'Skeleton', 'Citizen #1', 'Citizen #2', 'Candy Vendor', 'Prize Vendor', 'Cursed Skull', 'Passerby', 'Book', 'Merchant', 'Typewriter', 'Piniet', 'Welcome Mat', 'Crowd', 'Jon De Plume', 'Author #1', 'Author #2', 'Author #3', 'Author #4', 'Garlog', 'Shopkeeper', 'Townspeople', 'Fish Sailor', 'Bo', 'Eileen', 'Carnivorous Plant', 'Song', 'Potions Teacher', 'Detention Teacher', 'Teacher', 'Inspector', 'Principal Faust', 'Glandus High student', 'Cyclops demon girl', 'St. Epiderm student', 'Bria', 'Gavin', 'Angmar', 'Malphas', 'Keeper', 'Blond Romance Lead', 'Villain', 'Ghost', 'Sword', 'Adegast', 'Nevareth', 'Chris', 'Everyone', 'Princess', 'Nevereth', 'Basilisk', 'Vee', 'Rats', 'Girl 1', 'Jacob', 'Member 1', 'Member 2', "Emperor's coven delegate"]
characterSelectionDropdown.grid(column = 1, row = 6)
characterSelectionDropdown.current(0)

#Add frame in grid so character buttons can be next to each other
characterFrame.grid(column = 1,row = 7)

#Buttons that let user select characters to add to list, reset selected characters list, and update characterSelectionDropdown
characterButtonSelect = ttk.Button(characterFrame, text= "Click to select character", command=selectCharacter)
characterButtonSelect.pack(side=tk.LEFT)
characterButtonReset = ttk.Button(characterFrame, text= "Reset selected character(s)", command=resetSelectedCharacters)
characterButtonReset.pack(side=tk.LEFT)
characterButtonUpdate = ttk.Button(characterFrame, text= "Update character list", command=updateCharacterList)
characterButtonUpdate.pack(side=tk.LEFT)
selectedCharacterDialogueList = []

#Text above episode dropdown
selectEpisodeLabel = ttk.Label(frame, text = "Select episode(s) :",wraplength=150)

selectEpisodeLabel.grid(column = 1, row = 8)

#Episode selection dropdown
strVarEpisode = tk.StringVar()
episodeSelectionDropdown = ttk.Combobox(frame,state="readonly", width = 27, textvariable = strVarEpisode)
episodeListDropdown = []
episodeListDropdown.append("All episodes")
# list of all current episodes as of 5/13/22. Relevant for character update method
currentEpisodes = ['A_Lying_Witch_and_a_Warden','Adventures_in_the_Elements', 'Agony_of_a_Witch', 'Amphibia_and_The_Owl_House_crossover_panel', 'Any_Sport_in_a_Storm', 'Art_Lessons_with_Luz', 'Coven_Lovin_Soap_Opera', 'Covention', 'Echoes_of_the_Past', 'Eclipse_Lake', 'Eda%27s_Cursed_Brush', 'Eda%27s_Requiem', 'Edge_of_the_World', 'Elsewhere_and_Elsewhen', 'Enchanting_Grom_Fright', 'Escape_of_the_Palisman', 'Escaping_Expulsion', 'Follies_at_the_Coven_Day_Parade', 'Hollow_Mind', 'Hooty%27s_Moving_Hassle', 'Hunting_Palismen', 'I_Was_a_Teenage_Abomination', 'Keeping_Up_A-fear-ances', 'Knock,_Knock,_Knockin%27_on_Hooty%27s_Door', 'Labyrinth_Runners', 'Lost_in_Language', 'Once_Upon_a_Swap', 'Paint_Scare!', 'Reaching_Out', 'Really_Small_Problems', 'Sense_and_Insensitivity', 'Separate_Tides', 'Something_Ventured,_Someone_Framed', 'The_Dollhouse', 'The_First_Day', 'The_Intruder', 'Them%27s_the_Breaks,_Kid', 'Through_the_Looking_Glass_Ruins', 'Understanding_Willow', 'Welcome_to_Hexside', 'Wing_It_Like_Witches', 'Witches_Before_Wizards', 'Yesterday%27s_Lie', 'Young_Blood,_Old_Souls']
episodeNamesAsUrls = []
#Get and format episode names for dropdown
for url in episodeTranscriptUrls:
    transcriptName = url.replace('https://theowlhouse.fandom.com/wiki/','')
    transcriptName = transcriptName.replace('/Transcript','')
    episodeNamesAsUrls.append(transcriptName)
    transcriptName = transcriptName.replace('_',' ')
    transcriptName = transcriptName.replace('%27',"'")
    episodeListDropdown.append(transcriptName)
episodeSelectionDropdown['values'] = episodeListDropdown
episodeSelectionDropdown.grid(column = 1, row = 9)
#Default dropdown selection
episodeSelectionDropdown.current(0)

#Add frame in grid so episode buttons can be next to each other
episodeFrame.grid(column = 1,row = 10)

#Buttons that let user select characters to add to list and reset selected characters list
episodeButtonSelect = ttk.Button(episodeFrame, text= "Click to select episode", command=selectEpisode)
episodeButtonSelect.pack(side=tk.LEFT)
episodeButtonReset = ttk.Button(episodeFrame, text= "Reset selected episode(s)", command=resetSelectedEpisodes)
episodeButtonReset.pack(side=tk.LEFT)

#Button that lets user search for character dialogue
searchButton = ttk.Button(frame, text= "Select characters and dialogue", command=searchTranscripts)
searchButton.grid(column = 1,row = 11,pady=10)
#Search disabled until user selects at least one character and episode
searchButton["state"] = "disabled"

#Text above loading bar
loadingLabel = ttk.Label(frame, text="",wraplength=250)
loadingLabel.grid(column=1, row=12)
#Loading bar
s = ttk.Style()
s.configure("TProgressbar", foreground="green", background="green", thickness=50)
loadingBar = Progressbar(frame, style="TProgressbar", length=250, mode="determinate")
loadingBar.grid(column = 1,row = 13)
#Hide loadingLabel and loadingBar until search method
loadingLabel.grid_forget()
loadingBar.grid_forget()

#Add frame in grid so stats buttons can be next to each other
statsFrame.grid(column = 1,row = 14)

#What keeps track of dialogue stats
characterDialogueStatsIndex = 0

#Buttons that user increment through and view character dialogue stats
statsButtonDecrease = ttk.Button(statsFrame, text= "<", command=characterDialogueStatsDecrease)
statsButtonDecrease.pack(side=tk.LEFT)
currentCharacterStatNameLabel = ttk.Label(statsFrame, text="",wraplength=250)
currentCharacterStatNameLabel.pack(side=tk.LEFT)
statsButtonIncrease = ttk.Button(statsFrame, text= ">", command=characterDialogueStatsIncrease)
statsButtonIncrease.pack(side=tk.LEFT)
characterDialogueStatsLabel = ttk.Label(frame, text = "",wraplength=200)
characterDialogueStatsLabel.grid(column = 1,row = 15)

#Hide stats until serach is finished
statsFrame.grid_forget()
characterDialogueStatsLabel.grid_forget()

#Main loop for program to run
frame.mainloop()
