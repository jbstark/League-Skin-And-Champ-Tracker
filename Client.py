import requests
import base64
import json
import psutil
import sqlite3
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class Client:

    def __init__(self):
        """
        Creates variables for find the client and lockfile. Then runs find client
        """
        # Disable InsecureRequestWarning as the connection to the client cannot be secure
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Variables for clientRunning
        self.clientRunning = False
        self.clientNames = ["leagueclientuxrender.exe"]
        self.possibleDirectories = set()

        # Variables needed for lockfile
        self.url = None
        self.header = None
        self.summonerId = None
        self.lockfileFound = False

        # Creates connection to champions.db
        self.con = sqlite3.connect("champions.db")
        with self.con:
            self.con.execute("CREATE TABLE if not exists Champions (name TEXT UNIQUE, owned INTEGER, cost INTEGER)")

        self.check_client_running()

        # TODO Update if patch of client doesnt match patch of app

    def check_client_running(self):
        """
        Checks to see if the client is running.
        If it is possibleDirectories is updated with the directory, and find_lockfile is run
        This should be where lockfile is
        If not, self.clientRunning will be false, and other functions will not run
        :return:
        """
        # See if league client process is running
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if proc.name().lower() in self.clientNames:
                    self.clientRunning = True
                    self.possibleDirectories.add(proc.cwd())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        # If league isn't running quit
        if not self.clientRunning:
            print("Please refresh while the league of legends client is open")

        # If the client was found find the lockfile
        if self.clientRunning:
            self.find_lockfile()

    def find_lockfile(self):
        """
        Finds the lockfile as long as lockfile is in a folder in possibleDirectories
        :return:
        """

        # Return error if lockfile never opened
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        # Find the lockfile
        for path in self.possibleDirectories:
            lockfile = path + r"\lockfile"
            # Try opening the lockfile
            try:
                with open(lockfile, 'r') as f:
                    file_contents = f.read().split(":")
                self.lockfileFound = True
            # League client is still opening, FAIL
            except FileNotFoundError:
                pass
        if self.lockfileFound is False:
            print("Lockfile not found, Coding Error. Exiting")
            exit()

        # Get the port and password form the lockfile
        port = file_contents[2]
        password = file_contents[3]

        # Get client API url
        self.url = 'https://127.0.0.1:' + port

        # Get client Authorization For Request
        authorization = "riot:" + password
        authorization_b64 = base64.b64encode(authorization.encode()).decode()

        # Header for request
        self.header = {"Accept": "application/json", "Authorization": "Basic " + authorization_b64}

        # Get summonerID of logged in user
        request = self.url + '/lol-summoner/v1/current-summoner'
        response = requests.get(request, verify=False, headers=self.header)
        self.summonerId = json.loads(response.text)["summonerId"]

    def update(self):
        """
        Updates the information from the client. Used for changes in status (champions, skins, etc.)
        :return:
        """
        # Refresh which champions are owned
        self.get_all_champions()

    def get_all_champions(self):
        """
        Gets champion information form LCU
        :return:
        """
        # Return error if lockfile never opened
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        # Construct URL
        summoner_id_string = str(self.summonerId)
        request = self.url + '/lol-champions/v1/inventories/' + summoner_id_string + '/champions-minimal'

        # Make request
        response = requests.get(request, verify=False, headers=self.header)
        response_json = json.loads(response.text)
        response_json.sort(key=sort_champs)
        for champion in response_json:
            if champion['name'] != "None":
                champion_name = champion['name']
                owned = str(int(champion["ownership"]["owned"]))
                cost = "0"
                with self.con:
                    self.con.execute("INSERT OR REPLACE INTO Champions VALUES (\""
                                     + champion_name + '\", ' + owned + ', ' + cost + ')')

    # Get all champs if owned or unowned. owned_status is true or false
    def get_champs(self, owned_status):
        """
        get_champs returns a list of owned or unowned champions

        :param owned_status: Boolean for if the function should find owned (True) or unowned (False) champions
        :return: Returns a list of owned or unowned champions
        """

        # Return error if lockfile never opened
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        if owned_status is True:
            owned = "1"
        else:
            owned = "0"
        with self.con:
            owned = self.con.execute("SELECT name FROM Champions WHERE owned = " + owned)
        return [champion[0] for champion in owned.fetchall()]

    # Get number of champs if owned or unowned. owned_status is true or false
    def get_num_champs(self, owned_status):
        """
        get_num_champs returns an int for the number of owned or unowned champions

        :param owned_status: Boolean for if the function should find owned (True) or unowned (False) champions
        :return: Returns an int
        """

        # Return error if lockfile never opened
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        if owned_status is True:
            owned = "1"
        else:
            owned = "0"
        with self.con:
            num_owned = self.con.execute("SELECT COUNT(*) FROM Champions WHERE owned = " + owned)
        return num_owned.fetchall()[0][0]

    def print_all_data(self):
        """
        print_all_data prints the Champions table in champions.db

        :return:
        """
        # Return error if lockfile never opened
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        all_data = self.con.execute("SELECT * FROM Champions")
        print(all_data.fetchall())


def sort_champs(champ):
    """
    Returns the name of a champion dictionary to be used for sorting

    :param champ: the dictionary representing the champion
    :return: Returns the name of the champion in the dictionary
    """
    return champ["name"]
