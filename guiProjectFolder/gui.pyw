from tkinter import *
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from copy import deepcopy

import zipfile, os, time, json

VERSION = 0.02
CONSOLE_PREFIX = "||"
PROGRAM_PATH = __file__[:__file__.rindex("\\")]

guiTest = {"guiObjects": []}
titleFontObject = ("Arial", 25, "bold")

applicationLogLabel = None
currentlyDownloading = False
consoleLabel = None
darkmodeButton = None
editPathTextBox = None
extractingTo = None

CurrentDrive = "C"
HomePath = Path(CurrentDrive + str(Path.home())[1:])
ToExtractFolder = str(HomePath) + "\Desktop\Extraction Project"
AssetsFolder = ToExtractFolder + "\extraction-project-assets"
commonSteamDestination = "\Program Files (x86)\Steam\steamapps\common"
AbsolutePathsFile = AssetsFolder + "\paths.json"
ConfigFileName = PROGRAM_PATH + "\\" + "UserPreferences.cfg"

WritableConfig = {
    "app_bg": "False",
    "app_sel": "None",
    "app_sel_name": "None"
}

DestinationTable = {
    "Blade&Sorcery": ["C:\\Program Files (x86)\Steam\steamapps\common\Blade & Sorcery\BladeAndSorcery_Data\StreamingAssets\Mods"],
    "BONELAB": ["C:\\Users\jakes\AppData\LocalLow\Stress Level Zero\BONELAB\Mods"],
    "Pavlov": ["C:\\Users\jakes\AppData\Local\Pavlov\Saved\Mods", "Data", "__ModName__"],
    "Beat Saber": ["C:\\Program Files (x86)\Steam\steamapps\common\Beat Saber\Beat Saber_Data\CustomLevels", "__ModName__"],
    "Deadlock": ["C:\\Program Files (x86)\Steam\steamapps\common\Deadlock\game\citadel\\addons"]
}

def PrintDebug(Statement):
    print(f"{Statement}")

    try:
        applicationLogLabel.configure(text=f"{CONSOLE_PREFIX}  {Statement}")
    except AttributeError:
        print("DEBUG: **Application Log Label does not exist yet!**\n")

def SearchForInstalledGame(game):
    CurrentDriveSearching = ""
    os.path.exists(CurrentDriveSearching + ":" + commonSteamDestination)

def changePathSetting():
    global extractingTo
    if currentGame is not None:
        modDir = filedialog.askdirectory(initialdir=extractingTo, mustexist=True)

        if modDir:
            DestinationTable[currentGameName][0] = modDir

            with open(AbsolutePathsFile, "r+") as file:
                jsonFile = json.load(file)
                jsonFile["Paths"][currentGameName] = modDir
                file.seek(0)
                # json.dump(jsonFile, fp=file, indent=4, separators=(", ", ": "))
                file.write(json.dumps(jsonFile, indent=4, separators=(", ", ": ")))
                file.truncate()

            extractingTo = modDir
            editPathTextBox.configure(text=extractingTo)
            PrintDebug(f"New path selected for {currentGameName}.")
            return 
    
    PrintDebug("No game selected!")

def createAbsolutePathFile():
    try:
        with open(AbsolutePathsFile, "x") as file:
            clonedDictonary = {"Paths": {}}
            clonedDictonary["Paths"] = DestinationTable.copy()
            for destination in clonedDictonary["Paths"]:
                clonedDictonary["Paths"][destination] = ""

            file.write(json.dumps(clonedDictonary, indent=4, separators=(", ", ": ")))

        PrintDebug("Absolute Path JSON file created!")

    except FileExistsError:
        print("JSON file exists already!")

def readAbsolutePaths():
    try:
        with open(AbsolutePathsFile, "r") as file:
            jsonFile = json.load(file)
            for destination in DestinationTable:
                if destination in jsonFile["Paths"]:
                    DestinationTable[destination][0] = jsonFile["Paths"][destination]
                else:
                    print(destination, "not found")
    except FileNotFoundError:
        createAbsolutePathFile()


def SaveConfig(**kargs):
    print("args:", kargs)
    with open(ConfigFileName, "w") as cfg:
        for attribute in WritableConfig:
            value = WritableConfig[attribute]
            if kargs[attribute]:
                value = kargs[attribute]

            cfg.write(attribute + ": " + str(value) + "\n")
        
def ReturnConfigAttribute(Property):
    try:
        with open(ConfigFileName, "r") as cfg:
            try:
                for l in cfg:
                    if l.find(Property) != -1:
                        PrintDebug(f"Found [{Property}] in config!")
                        return l[len(Property) + 1:].strip()
                    
                    PrintDebug(str(l[len(Property) + 1:]) + " : Not Found")
                    
            except IndexError:
                PrintDebug(f"[{Property}] not found in config!")
                return None
            
    except FileNotFoundError:
        SaveConfig()
        PrintDebug("Config File Created!")
            
darkmodeBool = ReturnConfigAttribute("app_bg") or "False"
currentGame = ReturnConfigAttribute("app_sel") or "None"
currentGameName = ReturnConfigAttribute("app_sel_name") or "None"
    
def changeDestination(Game):
    global extractingTo, consoleLabel, currentGame, currentGameName
    try:
        if DestinationTable[Game]:
            if os.path.exists(DestinationTable[Game][0]):
                PrintDebug(DestinationTable[Game][0])
                extractingTo = DestinationTable[Game][0]
                currentGame = DestinationTable[Game]
                currentGameName = Game
                consoleLabel.configure(text="Game path changed to [" + str(Game) + "].")
                if editPathTextBox:
                    editPathTextBox.configure(text=extractingTo)
            else:
                messagebox.showerror("An error has occured!", f"{Game}'s default path does not exist on this system! Please change it to an existing path.")
        else:
            consoleLabel.configure(text="Game path does not exist!")
    except KeyError:
        PrintDebug("No Game Selected!")

def extractMod(modName: str, destination: str):
    modZip = zipfile.ZipFile(ToExtractFolder + "\\" + modName, mode='r')
    try:
        modZip.extractall(destination)
    except zipfile.BadZipFile:
        PrintDebug("Failed extraction! Moving forward.")
    modZip.close()
    os.remove(modZip.filename)

def startExtraction(): 
    global consoleLabel

    i = 0
    if extractingTo != None:
        for modToExtract in os.scandir(ToExtractFolder):
            modName = str.strip(str.strip(str.split(str(modToExtract), "<DirEntry ")[-1], "'>"), '"')
            print(modName)
            if modName != "StartExtract.py.lnk" and modName != "StartExtract" and modName != "extraction-project-assets":
                consoleLabel.configure(text="Extracting " + modName + "...")
                if zipfile.is_zipfile(modToExtract):
                    i += 1
                    if len(currentGame) == 1:
                        extractMod(modName=modName, destination=extractingTo)
                    else:
                        ParentDir = None
                        ModContainer = None
                        if len(currentGame) > 2:
                            if currentGame[2] == "__ModName__":
                                os.mkdir(extractingTo+"\\"+modName)
                                ParentDir = extractingTo+"\\"+modName
                            else:
                                os.mkdir(extractingTo+"\\"+currentGame[2])
                                ParentDir = extractingTo+"\\"+currentGame[2]

                        if ParentDir:
                            ModContainer = ParentDir+"\\"+currentGame[1]
                            os.mkdir(ParentDir+"\\"+currentGame[1])
                        else:
                            ModContainer = extractingTo+"\\"+modName    #currentGame[1]
                            try:
                                os.mkdir(extractingTo+"\\"+modName)    #currentGame[1])
                            except:
                                consoleLabel.configure(text=modName + " already exists!")

                        extractMod(modName=modName, destination=ModContainer)
                    consoleLabel.configure(text="Finished Extracting " + modName + "!")
                    time.sleep(.15)
                else:
                    consoleLabel.configure(text=modName + " is not a valid zipfile!")
        time.sleep(.3)
        if i > 0:
            consoleLabel.configure(text=f"Finished extracting {str(i)} mods to {currentGameName}!")
        else:
            consoleLabel.configure(text="No mods to extract or able to be extracted!")
    else:
        consoleLabel.configure(text="Game path not defined!")

def darkmodefunction(ChangeVar=False):
    global darkmodeBool
    
    if ChangeVar is True:
        if darkmodeBool == "True":
            darkmodeBool = "False"
        else:
            darkmodeBool = "True"

    fgChangingElements = (Label, Button)

    if darkmodeBool == "False":
        GUI.configure(bg="white")
        darkmodeButton.configure(text="Dark Mode", bg="dark grey", activebackground="dark grey")
        for getAllObjects in guiTest["guiObjects"]:
            getAllObjects.configure(bg="white")

            if isinstance(getAllObjects, fgChangingElements):
                getAllObjects.configure(fg="black", bg="white")
    else:
        GUI.configure(bg="#383838")
        darkmodeButton.configure(text="Light Mode", bg="white", activebackground="white")
        for getAllObjects in guiTest["guiObjects"]:
            getAllObjects.configure(bg="#383838")

            if isinstance(getAllObjects, fgChangingElements):
                getAllObjects.configure(fg="white", bg="dark grey")

guiTest["GUI"] = Tk(screenName="screenName", baseName="baseName")
GUI = guiTest["GUI"]
GUI.title = "Mod Extraction Project"

Topbar = ttk.Frame(GUI, width=750, height=25, relief="ridge")
Topbar.pack(side="top", fill="x")

topbarVersion = Label(Topbar, text=f"Version: {VERSION}", relief="ridge", width=10)
topbarVersion.pack(side="left")

applicationLogLabel = Label(Topbar, text=f"", bd=0)
applicationLogLabel.pack(side="left")

newFrame = Frame(GUI, width=600, height=25)
newFrame.pack(side="top")

Title = Label(newFrame, text="Extract Mods", anchor="n", width=50, height=1, font=titleFontObject, fg="#000")
Title.pack(side="top", fill="x")

consoleLabel = Label(newFrame, text="Console will appear here!", relief="ridge", width=50)
consoleLabel.pack(side="top")

downloadButton = Button(newFrame, text="Start Extraction", anchor="center", width=15, height=1, bg="dark grey", activebackground="orange", command= lambda: startExtraction())
downloadButton.pack(side="top", pady=25)

optionsLabel = Label(newFrame, text="[GAME PATH OPTIONS]", relief="sunken", width=23)
optionsLabel.pack(side="top", pady=3)

for Destinations in DestinationTable:
    dBttn = Button(newFrame, text=Destinations, anchor="center", width=13, height=1, bg="light grey", activebackground="orange", command= lambda Destinations=Destinations: changeDestination(Destinations))
    dBttn.pack(side="top", pady=2)
    guiTest["guiObjects"].append(dBttn)

editPathLabel = Label(newFrame, text="[CHANGE PATH]", relief="sunken", width=25)
editPathLabel.pack(side="top", pady=(30, 5))

editPathTextBox = Button(newFrame, bg="light grey", relief="ridge", width=0, height=1, command=changePathSetting)
editPathTextBox.pack()

darkmodeButton = Button(GUI, text="Dark Mode", anchor="center", width=20, height=1, bg="dark grey", activebackground="dark grey", command= lambda: darkmodefunction(True))
darkmodeButton.pack(side="bottom")

GUI.geometry("750x500")
GUI.maxsize(750, 500)
GUI.minsize(750, 500)
GUI.wm_attributes("-transparentcolor", "pink")
# GUI.wm_attributes("-alpha", "0.95")
GUI.configure(bg="white")

Tk.title(GUI, "Mod Extraction")
Tk.iconphoto(GUI, True, PhotoImage(file=AssetsFolder + "\icon.png"))

guiTest["guiObjects"].append(newFrame)
guiTest["guiObjects"].append(Title)
guiTest["guiObjects"].append(darkmodeButton)

for getAllObjects in guiTest["guiObjects"]:
    getAllObjects.configure(bg="white")

PrintDebug("Python Console will appear here!")
readAbsolutePaths()
changeDestination(currentGameName)
darkmodefunction()

GUI.mainloop()
SaveConfig(app_bg=darkmodeBool, app_sel=currentGame, app_sel_name=currentGameName)