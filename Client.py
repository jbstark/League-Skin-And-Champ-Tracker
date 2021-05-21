import requests
import base64
import json
import psutil
import sqlite3
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class Client:

    def __init__(self):
        """
        Constructor for Client Class
        Checks if client is running, and if so will open the lockfile
        Used to interface with the League Client (LCU)
        Sets up data to make requests later
        """
        # Disable InsecureRequestWarning as the connection to the client cannot be secure
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # See if client is running
        self.clientRunning = False
        self.clientNames = ["leagueclientuxrender.exe"]
        self.possibleDirectories = set()

        # See if league client process is running
        for self.proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if self.proc.name().lower() in self.clientNames:
                    self.clientRunning = True
                    self.possibleDirectories.add(self.proc.cwd())
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        # If league isn't running quit
        if not self.clientRunning:
            # TODO instead of quitting allow for refresh
            print("Please open the client and reopen this app")
            exit()

        # Find the lockfile
        self.lockfileFound = False
        for path in self.possibleDirectories:
            self.lockfile = path + "\lockfile"
            # Try opening the lockfile
            try:
                with open(self.lockfile, 'r') as f:
                    file_contents = f.read().split(":")
                self.lockfileFound = True
            # League client is still opening, FAIL
            except FileNotFoundError:
                pass

        # TODO Remove this when lockfile can be refreshed
        if self.lockfileFound is False:
            print("Lockfile not found")
            exit()

        # Get the port and password form the lockfile
        self.port = file_contents[2]
        self.password = file_contents[3]

        # Get client API url
        self.url = 'https://127.0.0.1:' + self.port

        # Get client Authorization For Request
        self.authorization = "riot:" + self.password
        self.authorization_b64 = base64.b64encode(self.authorization.encode()).decode()

        # Header for request
        self.header = {"Accept": "application/json", "Authorization": "Basic " + self.authorization_b64}

        # Get summonerID
        request = self.url + '/lol-summoner/v1/current-summoner'
        response = requests.get(request, verify=False, headers=self.header)
        self.summonerId = json.loads(response.text)["summonerId"]

        self.con = sqlite3.connect("champions.db")
        with self.con:
            self.con.execute("CREATE TABLE if not exists Champions (name TEXT UNIQUE, owned INTEGER, cost INTEGER)")

        # TODO Update if patch of client doesnt match patch of app

    def update(self):
        """
        Updates the information from the client. Used for changes in status (champions, skins, etc.)
        :return:
        """
        # Refresh which champions are owned
        self.get_all_champions()

    def get_all_champions(self):
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
        all_data = self.con.execute("SELECT * FROM Champions")
        print(all_data.fetchall())


def sort_champs(champ):
    """
    Returns the name of a champion dictionary to be used for sorting

    :param champ: the dictionary representing the champion
    :return: Returns the name of the champion in the dictionary
    """
    return champ["name"]
