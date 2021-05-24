import base64
import json
import sqlite3
import os
from datetime import datetime
import psutil
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# TODO when printing date convert from UTC to local time


class Client:

    def __init__(self):
        """
        Creates variables for find the client and lockfile. Then runs find client
        """
        # Disable InsecureRequestWarning as the connection to the client cannot be secure
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Variables for clientRunning
        self.clientRunning = False
        # TODO add process linux? (How does wine work)
        self.clientNames = ["leagueclientuxrender.exe", "leagueclientux"]
        self.possibleDirectories = set()

        # Variables needed for lockfile
        self.url = None
        self.header = None
        self.summonerId = None
        self.lockfileFound = False

        # Creates connection to champions.db
        self.con = sqlite3.connect("champions.db")
        with self.con:
            # Champion name, Champion ID, Owned, IP cost, Num champ shards, Mastery Level, Mastery tokens, UTC date play
            self.con.execute("CREATE TABLE if not exists Champions (name TEXT UNIQUE, championID INTEGER, " +
                             "owned INTEGER, cost INTEGER, champShards int, championMastery int, masteryTokens int, " +
                             "lastPlayed TEXT)")

        self.check_client_running()

    def add_cols(self):
        # TODO fix this so that it is automatic and users can skip updates
        """
        If the table is updated, add column here
        :return:
        """
        with self.con:
            # Champion name, Champion ID, Owned, IP cost, Num champ shards, Mastery Level, Mastery tokens, UTC date play
            self.con.execute("ALTER TABLE Champions ADD COLUMN lastPlayed TEXT")

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
            # gets path for all operating systems
            lockfile = os.path.join(path, r'lockfile')
            
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

        self.build_api(port, password)

        # TODO Update if patch of client doesnt match patch of app

        self.update_all_champions()

    def build_api(self, port, password):
        """
        Sets up the data needed to call the API later.
        :param port: The port which the riot games client is running on
        :param password: The password in the lockfile
        :return: none
        """
        # Get client API url
        self.url = 'https://127.0.0.1:' + port

        # Get client Authorization For Request
        authorization = "riot:" + password
        authorization_b64 = base64.b64encode(authorization.encode()).decode()

        # Header for request
        self.header = {"Accept": "application/json", "Authorization": "Basic " + authorization_b64}

        # Get summonerID of logged in user
        self.summonerId = self.call_api('/lol-summoner/v1/current-summoner')["summonerId"]

    def call_api(self, address):
        """
        Calls the API
        :param address: The request to make to the API
        :return: the json of the response
        """
        if self.clientRunning is False:
            return None
        request = self.url + address
        response = requests.get(request, verify=False, headers=self.header)
        return json.loads(response.text)

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

        # Make request for all champion data
        response_json = self.call_api(f'/lol-champions/v1/inventories/{self.summonerId}/champions-minimal')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        response_json.sort(key=sort_champs)

        # Get Blue Essence Costs
        prices = self.update_champion_costs()

        # Get champ Shards and Mastery Tokens
        champ_shards, mastery_tokens = self.update_loot()

        # Get Champion Mastery
        mastery, last_played = self.update_mastery_and_date()

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
                try:
                    mastery_level = mastery[champion_id]
                except KeyError:
                    # Champion has no mastery
                    mastery_level = 0

                # Get last played date
                try:
                    date = last_played[champion_id]
                except KeyError:
                    # Champion has no lastPlayed (Meaning no mastery)
                    date = 0

                # Get number of tokens
                num_tokens = mastery_tokens[champion_name]

                try:
                    # name TEXT, owned INTEGER, cost INTEGER, champShards int, championMastery int, masteryTokens int
                    self.con.execute(f'INSERT OR REPLACE INTO Champions VALUES ("{champion_name}", {champion_id}, ' +
                                     f'{owned}, {cost}, {num_shards}, {mastery_level}, {num_tokens}, "{date}")')
                    # champShards int, championMastery int, masteryTokens int)
                except sqlite3.OperationalError:
                    # Old table, add column
                    self.add_cols()
                    self.con.execute(f'INSERT OR REPLACE INTO Champions VALUES ("{champion_name}", {champion_id}, ' +
                                     f'{owned}, {cost}, {num_shards}, {mastery_level}, {num_tokens}, "{date}")')

    def update_champion_costs(self):
        """
        Updates the cost of champions in the champions.db table. Used for change in price or new champions
        :return: a dictionary of champion names and their cost
        """

        # Make request
        response_json = self.call_api('/lol-store/v1/catalog?inventoryType=%5B%22CHAMPION%22%5D')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        all_champs = self.get_all_champs()
        champion_costs = {champ: 0 for champ in all_champs}

        # Get the localization for getting champion cost
        localization = [*response_json[0]["localizations"]][0]

        for champion in response_json:
            name = champion["localizations"][localization]["name"]
            ip_cost = str(champion["prices"][0]["cost"])
            champion_costs[name] = ip_cost

        return champion_costs

    def update_mastery_and_date(self):
        """
        Retrieves champion mastery for champions with mastery (owned)
        :return: a dict of championID and mastery levels. Use try except to set champs not here to 0
        """

        # Make request
        response_json = self.call_api(f'/lol-collections/v1/inventories/{self.summonerId}/champion-mastery')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        mastery = dict()
        date = dict()

        # Create Dictionary
        for champion in response_json:
            mastery[champion['championId']] = champion['championLevel']
            # Last date mastery points were gained on a champion
            date[champion['championId']] = datetime.utcfromtimestamp(champion['lastPlayTime'] / 1e3)\
                .strftime('%Y-%m-%d %H:%M:%S')
        return mastery, date

    def update_loot(self):
        """
        Gets loot from league client and then updates the table
        :return: two lists of tuples (champion, #shards), First return is champ_shards second is mastery_tokens
        """

        # Call the API
        response_json = self.call_api('/lol-loot/v1/player-loot')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

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

    def get_all_champs(self):
        """
        get_all_champs returns a list of ALL champions in the game

        :return: Returns a list
        """

        with self.con:
            owned = self.con.execute("SELECT name FROM Champions")

        fetch = owned.fetchall()

        if not fetch:
            response_json = self.call_api(f'/lol-champions/v1/inventories/{self.summonerId}/champions-minimal')

            # if the API call fails
            if response_json is None:
                return "Client not connected. Please refresh"

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

        if owned_status is True:
            owned = "1"
        else:
            owned = "0"
        with self.con:
            result = self.con.execute("SELECT name FROM Champions WHERE owned = " + owned)

        # ALl champs unowned or owned
        if result is None:
            return None

        return [champion[0] for champion in result.fetchall()]

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
            result = self.con.execute("SELECT COUNT(*) FROM Champions WHERE owned = " + owned)

        return result.fetchall()[0][0]

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

        # Default current_ip is 0 unless requested to use
        current_ip = 0

        # If the program should subtract IP in the account, get the current_ip
        if subtract_owned:
            response_json = self.call_api("/lol-store/v1/wallet")
            # if the API call fails
            if response_json is None:
                return "Client not connected. Please refresh"
            current_ip = response_json["ip"]

        # Get the maximum cost of all unowned champions
        maximum = self.con.execute("SELECT SUM (cost) FROM Champions WHERE owned = 0").fetchone()[0]

        # if try fails, then the cost needed to purchase all champions is 0
        try:
            # If all champs are owned
            assert(maximum is not None)

            if version == "max":
                # If at max cost it is negative throw exception
                assert(maximum - current_ip > 0)
                return int(maximum - current_ip)
            elif version == "min":
                # If at min cost it is negative throw exception
                assert(int((maximum * .6) - current_ip) > 0)
                return int((maximum * .6) - current_ip)

            # Try to get all champions with shards. If it fails, then the discount is 0
            try:
                current_discount = self.con.execute("SELECT SUM (cost) FROM Champions WHERE " +
                                                    "owned = 0 AND champShards > 0").fetchone()[0] * .4
            except (SyntaxError, TypeError):
                current_discount = 0

            # If at current cost it is negative throw exception
            assert(maximum - current_discount - current_ip > 0)
            return int(maximum - current_discount - current_ip)

        except AssertionError:
            # Either no champs unowned, or user has enough IP
            return 0

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
