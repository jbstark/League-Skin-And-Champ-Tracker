import requests
import base64
import json
import psutil
import sqlite3
from requests.packages.urllib3.exceptions import InsecureRequestWarning


# TODO Replace if not self.clientRunning:

class Client:

    def __init__(self):
        """
        Creates variables for find the client and lockfile. Then runs find client
        """
        # Disable InsecureRequestWarning as the connection to the client cannot be secure
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Variables for clientRunning
        self.clientRunning = False
        # TODO add process name for mac (linux?)
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
            self.con.execute("CREATE TABLE if not exists Champions (name TEXT UNIQUE, championID INTEGER, " +
                             "owned INTEGER, cost INTEGER, champShards int, championMastery int, masteryTokens int)")

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
        for process in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process.name().lower() in self.clientNames:
                    self.clientRunning = True
                    self.possibleDirectories.add(process.cwd())
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
        print(self.summonerId)
        self.update_all_champions()

    def update(self):
        """
        Updates the information from the client. Used for changes in status (champions, skins, etc.)
        :return:
        """
        # Refresh which champions are owned
        self.update_all_champions()

    def update_all_champions(self):
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

        # Get Blue Essence Costs
        prices = self.update_champion_costs()

        # Get champ Shards and Mastery Tokens
        champ_shards, mastery_tokens = self.update_loot()

        # Get Champion Master
        mastery = self.update_mastery()

        # Make request
        response = requests.get(request, verify=False, headers=self.header)
        response_json = json.loads(response.text)
        response_json.sort(key=sort_champs)
        for champion in response_json:
            if champion['name'] != "None":
                champion_name = champion['name']
                champion_id = champion['id']
                owned = str(int(champion["ownership"]["owned"]))

                # Get Cost
                cost = prices[champion_name]
                # Get Champion Shards
                num_shards = champ_shards[champion_name]
                # Get mastery level
                mastery_level = 0
                try:
                    mastery_level = mastery[champion_id]
                except KeyError:
                    # Champion has no mastery
                    mastery_level = 0
                # Get number of tokens
                num_tokens = mastery_tokens[champion_name]

                with self.con:
                    # name TEXT, owned INTEGER, cost INTEGER, champShards int, championMastery int, masteryTokens int
                    self.con.execute(f'INSERT OR REPLACE INTO Champions VALUES ("{champion_name}", {champion_id}, '
                                     f'{owned}, {cost}, {num_shards}, {mastery_level}, {num_tokens})')
                    # champShards int, championMastery int, masteryTokens int)

    def get_all_champs(self):
        """
        get_all_champs returns a list of ALL champions in the game

        :return: Returns a list
        """

        # Return error if lockfile never opened
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        with self.con:
            owned = self.con.execute("SELECT name FROM Champions")

        fetch = owned.fetchall()

        if not fetch:
            summoner_id_string = str(self.summonerId)
            request = self.url + '/lol-champions/v1/inventories/' + summoner_id_string + '/champions-minimal'

            response = requests.get(request, verify=False, headers=self.header)
            response_json = json.loads(response.text)
            response_json.sort(key=sort_champs)
            return(champion['name'] for champion in response_json)

        return [champion[0] for champion in fetch]

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

    def update_loot(self):
        """
        Gets loot from league client and then updates the table
        :return: two lists of tuples (champion, #shards), First return is champ_shards second is mastery_tokens
        """
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        request = self.url + '/lol-loot/v1/player-loot'
        response = requests.get(request, verify=False, headers=self.header)
        response_json = json.loads(response.text)

        all_champs = self.get_all_champs()
        shards = {champ: 0 for champ in all_champs}
        token = shards.copy()

        for item in response_json:
            # Champion Shards
            if item["displayCategories"] == "CHAMPION":
                name = item["itemDesc"]
                num_owned = item["count"]
                shards[name] = num_owned
            # Mastery Tokens
            elif item["displayCategories"] == "CHEST" and item["type"] == "CHAMPION_TOKEN":
                name = item["itemDesc"]
                num_owned = item["count"]
                token[name] = num_owned
        return shards, token

    def update_champion_costs(self):
        """
        Updates the cost of champions in the champions.db table. Used for change in price or new champions
        :return: a dictionary of champion names and their cost
        """
        # TODO Remove hard coding in localization
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        localization = "en_US"
        all_champs = self.get_all_champs()
        champion_costs = {champ: 0 for champ in all_champs}

        # Make request
        request = self.url + '/lol-store/v1/catalog?inventoryType=%5B%22CHAMPION%22%5D'
        response = requests.get(request, verify=False, headers=self.header)
        response_json = json.loads(response.text)
        for champion in response_json:
            name = champion["localizations"][localization]["name"]
            ip_cost = str(champion["prices"][0]["cost"])
            champion_costs[name] = ip_cost

        return champion_costs

    def update_mastery(self):

        if not self.clientRunning:
            return "Client not connected. Please refresh"

        all_champs = dict()

        # Make request
        request = self.url + f'/lol-collections/v1/inventories/{self.summonerId}/champion-mastery'
        response = requests.get(request, verify=False, headers=self.header)
        response_json = json.loads(response.text)
        # Create Dictionary
        for champion in response_json:
            all_champs[champion['championId']] = champion['championLevel']
        return all_champs


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

    def get_ip_needed(self, version, subtract_owned):
        """
        Computes the IP/BE needed to buy all champions left
        :param version: max, min or best. Determines which IP value to get
        max is the total cost for all unowned champions without shards
        min is the total cost for all unowned champions with shards
        Default/current is the total cost for all unowned champions given current shards in loot
        :param subtract_owned: Whether to subtract the current amount of IP in the account
        :return:
        """
        if not self.clientRunning:
            return "Client not connected. Please refresh"

        # Default weighting is 0, if discounted it is 60%
        if version == "max":
            weighting = 1
        elif version == "min":
            weighting = .60
        else:
            weighting = -1

        champs = self.con.execute("SELECT * FROM Champions WHERE owned = 0")
        if weighting != -1:
            cost = int(sum(champion[3] for champion in champs) * weighting)
        else:
            weighting = .6
            cost = int(sum(champion[3] * weighting if champion[4] >= 1 else champion[3] for champion in champs))

        if not subtract_owned:
            return cost

        request = self.url + "/lol-store/v1/wallet"
        response = requests.get(request, verify=False, headers=self.header)
        response_json = json.loads(response.text)

        current_ip = response_json["ip"]
        return cost - current_ip


def sort_champs(champ):
    """
    Returns the name of a champion dictionary to be used for sorting

    :param champ: the dictionary representing the champion
    :return: Returns the name of the champion in the dictionary
    """
    return champ["name"]
