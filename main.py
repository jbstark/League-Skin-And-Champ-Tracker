from tkinter import *
from datetime import datetime
import json

language = "en_US"


class GUI:

    # Default constructor
    def __init__(self, primary):
        self.primary = primary

        # Open json File and store as jsonData
        with open('userOptions.json', 'r') as f:
            self.file = f.readline()
            self.jsonData = json.loads(self.file)

        # Login frame
        self.loginFrame = LabelFrame(primary, width=325, height=130)

        # API input
        self.apiKeyPrompt = Label(self.loginFrame, text="API key:")
        self.apiKeyInput = Entry(self.loginFrame, width=200)
        self.apiKeyButton = Button(self.loginFrame, text="Update", command=self.enter_api_key)
        # Current API Key
        self.currentApiKey = Label(self.loginFrame, text="API Key: Not Set")
        if self.jsonData["apiKey"] != "":
            self.currentApiKey.configure(text="API Key: " + self.jsonData["apiKey"])

        # Summoner Name Input
        self.summonerNamePrompt = Label(self.loginFrame, text="Username:")
        self.summonerNameInput = Entry(self.loginFrame, width=200)
        self.summonerNameButton = Button(self.loginFrame, text="Update", command=self.enter_summoner_name)
        # Current Summoner Name
        self.currentSummonerName = Label(self.loginFrame, text="Username: Not Set")
        if self.jsonData["summonerName"] != "":
            self.currentSummonerName.configure(text="Username: " + self.jsonData["summonerName"])

        # Last Refresh
        self.lastRefreshDate = Label(self.loginFrame, text="Last Refresh: Never")
        if self.jsonData["lastRefresh"] != "":
            self.lastRefreshDate.configure(text="Last Refresh: " + self.jsonData["lastRefresh"])
        self.refreshOutcome = Label(self.loginFrame, text="Status")
        self.refresh = Button(self.loginFrame, text="Refresh", command=self.refresh_data)

        # Filter frame
        self.showUnowned = BooleanVar()

        self.firstSort = StringVar()
        self.firstSort.set("Alphabetical")

        self.secondSort = StringVar()
        self.secondSort.set("Alphabetical")

        self.filterFrame = LabelFrame(primary, width=325, height=95)
        # Primary Sort Widgets
        self.primarySortLabel = Label(self.filterFrame, text="Primary Sort:")
        self.primarySort = OptionMenu(self.filterFrame, self.firstSort, "Alphabetical ", "Mastery", "Cost",
                                      "Release Date", "Rarity")
        # Secondary Sort Widgets
        self.secondarySortLabel = Label(self.filterFrame, text="Secondary Sort:")
        self.secondarySort = OptionMenu(self.filterFrame, self.secondSort, "Alphabetical ", "Mastery", "Cost",
                                        "Release Date", "Rarity", )
        self.unownedBox = Checkbutton(self.filterFrame, text="Show Unowned",
                                      variable=self.showUnowned, command=self.update_filter)

        # Grid all
        self.grid_all()

    # Adds all widgets to Grid
    def grid_all(self):
        self.grid_login()
        self.grid_filter()

    # Adds widgets in frame login to grid
    def grid_login(self):
        # Grid the frame
        self.loginFrame.grid(row=0, column=0, padx=5, pady=5)
        self.loginFrame.grid_propagate(False)
        self.loginFrame.columnconfigure(1, weight=1)

        # Grid API information
        self.apiKeyPrompt.grid(row=0, sticky=W)
        self.apiKeyInput.grid(row=0, column=1, padx=5)
        self.apiKeyButton.grid(row=0, column=2, padx=5)
        self.currentApiKey.grid(row=1, columnspan=3, sticky="w")

        # Grid summoner name
        self.summonerNamePrompt.grid(row=2, sticky=W)
        self.summonerNameInput.grid(row=2, column=1, padx=5)
        self.summonerNameButton.grid(row=2, column=2, padx=5)
        self.currentSummonerName.grid(row=3, columnspan=3, sticky="w")

        # Refresh Options
        self.lastRefreshDate.grid(row=4, columnspan=2, sticky=W)
        self.refreshOutcome.grid(row=4, column=1, padx=5, sticky="E")
        self.refresh.grid(row=4, column=2, padx=5)

    # Adds widgets in frame filter to grid
    def grid_filter(self):
        # Grid the frame
        self.filterFrame.grid(row=1, column=0, padx=5, pady=5)
        self.filterFrame.grid_propagate(False)
        self.filterFrame.columnconfigure(1, weight=1)
        self.filterFrame.rowconfigure(1, weight=0)

        # Grid Filter Options
        self.primarySortLabel.grid(row=0, column=0, sticky="w")
        self.primarySort.grid(row=0, column=1, padx=5, sticky="ew")
        self.secondarySortLabel.grid(row=1, column=0, sticky="w")
        self.secondarySort.grid(row=1, column=1, padx=5, sticky="ew")
        self.unownedBox.grid(row=2, column=0)

    # Updates apiKey when update button pressed
    def enter_api_key(self):
        # If field is empty don't do anything
        if self.apiKeyInput.get() == "":
            return
        # If field not empty get input and clear field
        self.jsonData["apiKey"] = self.apiKeyInput.get()
        self.apiKeyInput.delete(0, 'end')

        # Update text
        self.currentApiKey.configure(text="API Key: " + self.jsonData["apiKey"])
        # Update userOptions.json
        self.save_data()

    # Returns API key
    def get_key(self):
        return self.jsonData["apiKey"]

    # Updates summonerName when update button pressed
    def enter_summoner_name(self):
        # If field is empty don't do anything
        if self.summonerNameInput.get() == "":
            return
        # If field not empty get input and clear field
        self.jsonData["summonerName"] = self.summonerNameInput.get()
        self.summonerNameInput.delete(0, 'end')

        # Update text
        self.currentSummonerName.configure(text="Username: " + self.jsonData["summonerName"])
        # Update userOptions.json
        self.save_data()

    # Returns SummonerName
    def get_summoner_name(self):
        return self.jsonData["summonerName"]

    # Save the jsonData to the file
    def save_data(self):
        # Format python to json
        self.toFile = json.dumps(self.jsonData)

        # Save json in file userOptions.json
        with open('userOptions.json', 'w') as f:
            f.write(self.toFile)

    # TODO
    def refresh_data(self):
        # Make API call

        # if API call sucsess
        if True:
            self.jsonData["lastRefresh"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            self.lastRefreshDate.configure(text="Last Refresh: " + self.jsonData["lastRefresh"])
            self.refreshOutcome.configure(text="Success", fg="green")
            self.save_data()
        else:
            # Else print fail and reason then return
            self.refreshOutcome.configure(text="Failure", fg="red")

    # TODO
    def update_filter(self):
        print(self.showUnowned.get())


# tkinter
root = Tk()
root.title("League Of Legends Tracker")
root.geometry("960x540")

info = GUI(root)
root.mainloop()
