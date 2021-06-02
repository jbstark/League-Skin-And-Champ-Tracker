import base64
import json
import sqlite3
import os
import time
from datetime import datetime
import psutil
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# TODO when printing date convert from UTC to local time

# TODO add player to Champions table to store all information


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

        # Summoner Info
        self.summonerInfo = None
        self.summonerId = None
        self.summonerName = None

        # Current Patch
        self.currentPatch = None

        self.lockfileFound = False

        # Creates connection to champions.db
        self.con = None

        self.check_client_running()

    def check_db(self):

        # Create file for each user
        filename = "lol_" + self.summonerName + ".db"
        self.con = sqlite3.connect(filename)

        # All columns (besides name) in the DB. Add a tuple here to add a column
        columns_champions = [("championID", "INTEGER"), ("owned", "INTEGER"), ("cost", "INTEGER"),
                             ("champShards", "INTEGER"), ("championMastery", "INTEGER"), ("masteryTokens", "INTEGER"),
                             ("lastPlayed", "TEXT")]
        columns_player = [("summonerID", "INTEGER"), ("accountID", "INTEGER"), ("level", "INTEGER"),
                          ("blueEssence", "INTEGER"), ("riotPoints", "INTEGER"), ("eventName", "TEXT"),
                          ("eventTokens", "INTEGER"), ("eventLootID", "INTEGER")]

        with self.con:
            self.con.execute("CREATE TABLE if not exists Champions (name TEXT UNIQUE)")
            self.con.execute("CREATE TABLE if not exists Player (username TEXT UNIQUE)")

            # Check cols of DB and compare to list of all cols in current version. Add missing
            for col in columns_champions:
                col_name = col[0]
                col_type = col[1]
                try:
                    self.con.execute(f"ALTER TABLE Champions ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    # Column Already Exists
                    pass

            # Check cols of DB and compare to list of all cols in current version. Add missing
            for col in columns_player:
                col_name = col[0]
                col_type = col[1]
                try:
                    self.con.execute(f"ALTER TABLE Player ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    # Column Already Exists
                    pass

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

        self.check_db()

        # TODO Update if patch of client doesnt match patch of app
        self.update()

    def build_api(self, port, password):
        """
        Sets up the data needed to call the API later.

        :param port: The port which the riot games client is running on
        :param password: The password in the lockfile
        :return:
        """
        # Get client API url
        self.url = 'https://127.0.0.1:' + port

        # Get client Authorization For Request
        authorization = "riot:" + password
        authorization_b64 = base64.b64encode(authorization.encode()).decode()

        # Header for request
        self.header = {"Accept": "application/json", "Authorization": "Basic " + authorization_b64}

        # Get summonerID of logged in user
        self.summonerInfo = self.call_api('/lol-summoner/v1/current-summoner')
        self.summonerId = self.summonerInfo["summonerId"]
        self.summonerName = self.summonerInfo["displayName"]

        self.currentPatch = self.call_api('/system/v1/builds')['version']

        # Client is loaded, but unsure if all requests can work yet. This code repeats until everything is loaded
        # If the request errors out because the client is still loading
        response = self.call_api(f'/lol-champions/v1/inventories/{self.summonerId}/champions-minimal')

        try:
            # If the client errors, it is still loading
            if response['message'] == 'Champion data has not yet been received.':

                loading = True
                num_seconds = 0

                # While the client is loading
                while loading:
                    # If over 15 seconds for client to load, quit
                    if num_seconds > 15:
                        exit()
                    # Wait 1 seconds then retry API call
                    time.sleep(1)
                    num_seconds += 1
                    response = self.call_api(f'/lol-champions/v1/inventories/{self.summonerId}/champions-minimal')

                    try:
                        # If it failed, client is still loading and stay in while loop
                        if response['message'] == 'Champion data has not yet been received.':
                            pass
                    except (KeyError, TypeError, AttributeError):
                        # If an error was generated, then it stopped loading
                        loading = False
        # Client is fully loaded, so pass
        except (KeyError, TypeError, AttributeError):
            pass

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

    def call_api_image(self, address):
        if self.clientRunning is False:
            return None
        request = self.url + address
        response = requests.get(request, verify=False, headers=self.header)

        return response

    def update(self):
        """
        Updates the information from the client. Used for changes in status (champions, skins, etc.)

        :return:
        """
        if self.clientRunning:
            # Refresh which champions are owned
            self.update_all_champions()
            self.update_summoner()
        else:
            # If the client is not running, tries again
            self.check_client_running()

    def update_summoner(self):
        account_id = self.summonerInfo["accountId"]
        summoner_level = self.summonerInfo["summonerLevel"]

        store_info = self.call_api("/lol-store/v1/wallet")
        be = store_info["ip"]
        rp = store_info["rp"]

        # Update player information
        self.con.execute(f'INSERT or IGNORE INTO Player (username) VALUES (?)', (self.summonerName,))
        self.add_to_database("Player", "username", self.summonerName, "summonerID", self.summonerId)
        self.add_to_database("Player", "username", self.summonerName, "accountID", account_id)
        self.add_to_database("Player", "username", self.summonerName, "level", summoner_level)
        self.add_to_database("Player", "username", self.summonerName, "blueEssence", be)
        self.add_to_database("Player", "username", self.summonerName, "riotPoints", rp)

        self.update_user_loot()

    def update_user_loot(self):

        # TODO Should it run when they have no tokens for an event but the event is running. How?
        # Call the API
        response_json = self.call_api('/lol-loot/v1/player-loot')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        # For looking for event tokens
        event_description_start = "Gained from purchasing event content or completing event missions."

        # Tracks if an event is running
        event_running = False

        for item in response_json:
            # Event Tokens
            # todo check next pass to see if this will work for all
            if item["localizedDescription"].find(event_description_start) != -1:
                token_name = item["localizedName"]
                current_tokens = item["count"]
                loot_id = item["lootId"]

                # Add event name
                self.add_to_database("Player", "username", self.summonerName, "eventName", token_name)

                # Add event tokens
                self.add_to_database("Player", "username", self.summonerName, "eventTokens", current_tokens)

                # Add event material name
                self.add_to_database("Player", "username", self.summonerName, "eventLootID", loot_id)

                event_running = True

        if not event_running:
            # Add event name
            self.add_to_database("Player", "username", self.summonerName, "eventName", None)

            # Add event tokens
            self.add_to_database("Player", "username", self.summonerName, "eventTokens", None)

            # Add event material name
            self.add_to_database("Player", "username", self.summonerName, "eventLootID", None)

        self.con.commit()

    def update_all_champions(self):
        """
        Gets champion information form LCU
        Calls update_champion_costs(), update_mastery_and_date(), update_champion_loot()

        :return:
        """

        # Make request for all champion data
        response_json = self.call_api(f'/lol-champions/v1/inventories/{self.summonerId}/champions-minimal')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        response_json.sort(key=sort_champs)

        for champion in response_json:
            if champion['name'] != "None":
                # Add champion to Database
                champion_name = champion['name']
                self.con.execute(f'INSERT or IGNORE INTO Champions (name) VALUES (?)', (champion_name,))

                # Add ID to Database
                champion_id = champion['id']
                self.add_to_database("Champions", "name", champion_name, "championID", champion_id)

                # Add Owned Status to Database
                owned = int(champion["ownership"]["owned"])
                self.add_to_database("Champions", "name", champion_name, "owned", owned)
        self.con.commit()

        # Update other columns
        self.update_champion_costs()
        self.update_mastery_and_date()
        self.update_champion_loot()

    def update_champion_costs(self):
        """
        Updates the cost of champions in the champions.db table.

        :return:
        """

        # Make request
        response_json = self.call_api('/lol-store/v1/catalog?inventoryType=%5B%22CHAMPION%22%5D')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        # Get the localization for getting champion cost
        localization = [*response_json[0]["localizations"]][0]

        for champion in response_json:
            name = champion["localizations"][localization]["name"]
            ip_cost = str(champion["prices"][0]["cost"])
            self.add_to_database("Champions", "name", name, "cost", ip_cost)
        self.con.commit()

    def update_mastery_and_date(self):
        """
        Updates champion mastery and date last played in champions.db

        :return:
        """

        # Make request
        response_json = self.call_api(f'/lol-collections/v1/inventories/{self.summonerId}/champion-mastery')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        for champion in response_json:
            mastery_level = champion['championLevel']
            # Last date mastery points were gained on a champion
            date = datetime.utcfromtimestamp(champion['lastPlayTime'] / 1e3).strftime('%Y-%m-%d %H:%M:%S')
            self.add_to_database("Champions", "championID", champion["championId"], "championMastery", mastery_level)
            self.add_to_database("Champions", "championID", champion["championId"], "lastPlayed", date)
        self.con.commit()

    def update_champion_loot(self):
        """
        Updates champion shards and mastery tokens in champions.db

        :return:
        """

        # Call the API
        response_json = self.call_api('/lol-loot/v1/player-loot')

        # if the API call fails
        if response_json is None:
            return "Client not connected. Please refresh"

        # Lists of all champions, takes off champions with values to then have all that should be 0
        all_champs_shards = self.get_all_champs()
        all_champs_tokens = all_champs_shards.copy()

        for item in response_json:
            # Champion Shards
            if item["displayCategories"] == "CHAMPION":
                name = item["itemDesc"]
                num_owned = item["count"]
                self.add_to_database("Champions", "name", name, "champShards", num_owned)
                # Remove champion from list, as its value will be added
                all_champs_shards.remove(name)
            # Mastery Tokens
            elif item["displayCategories"] == "CHEST" and item["type"] == "CHAMPION_TOKEN":
                name = item["itemDesc"]
                num_owned = item["count"]
                self.add_to_database("Champions", "name", name, "masteryTokens", num_owned)
                # Remove champion from list, as its value will be added
                all_champs_tokens.remove(name)

        # All champions with no shards should be set to null
        for champ in all_champs_shards:
            self.add_to_database("Champions", "name", champ, "champShards", 0)

        # All champions with no tokens should be set to null
        for champ in all_champs_tokens:
            self.add_to_database("Champions", "name", champ, "masteryTokens", 0)

        self.con.commit()

    def add_to_database(self, table, row, comparison, column, data):
        """
        Adds information to champions.db

        :param table: The name of the table to alter
        :param row: The row value to compare (usually name or championID)
        :param comparison: What to select from that row (usually the champion name or champion id)
        :param column: Column to insert the information into
        :param data: Data to insert into the column
        :return:
        """

        # Format data for update
        if isinstance(data, str):
            data = f'"{data}"'
        elif data is None:
            data = "Null"

        # Format comparison for update
        if isinstance(comparison, str):
            comparison = f'"{comparison}"'
        elif comparison is None:
            comparison = "Null"

        # Execute update
        self.con.execute(f'UPDATE {table} SET {column} = {data} WHERE {row} = {comparison}')

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

    def get_num_champs(self, owned_status):
        """
        get_num_champs returns an int for the number of owned or unowned champions

        :param owned_status: Boolean for if the function should find owned (True) or unowned (False) champions
        :return: Returns an formatted string
        """

        if owned_status is True:
            owned = "1"
        else:
            owned = "0"
        with self.con:
            result = self.con.execute("SELECT COUNT(*) FROM Champions WHERE owned = " + owned)

        return f'{result.fetchall()[0][0]:,}'

    def get_sorted_champs(self, primary_sort, primary_direction, secondary_sort, secondary_direction, show_unowned):

        if show_unowned:
            result = self.con.execute("SELECT * FROM Champions WHERE owned = 1 ORDER BY " +
                                      f"{primary_sort} {primary_direction},{secondary_sort} {secondary_direction}")
        else:
            result = self.con.execute(f"SELECT * FROM Champions ORDER BY " +
                                      f"{primary_sort} {primary_direction}, {secondary_sort} {secondary_direction}")
        print(result.fetchall())

    def get_ip_needed(self, version, subtract_owned, use_extra_shards):
        """
        Computes the IP/BE needed to buy all champions left

        :param version: max, min or best. Determines which IP value to get
        max is the total cost for all unowned champions without shards
        min is the total cost for all unowned champions with shards
        Default/current is the total cost for all unowned champions given current shards in loot
        :param subtract_owned: Whether to subtract the current amount of IP in the account
        :param use_extra_shards: Whether to use extra shards (any owned and >1 of unowned) for calculation
        :return: Returns an formatted string
        """

        # Default current_ip is 0 unless requested to use
        current_ip = 0

        # TODO should the player table be referenced?
        
        # If the program should subtract IP in the account, get the current_ip
        if subtract_owned:
            response_json = self.call_api("/lol-store/v1/wallet")
            # if the API call fails
            if response_json is None:
                return "Client not connected. Please refresh"
            current_ip = response_json["ip"]

        # Get the maximum cost of all unowned champions
        maximum = self.con.execute("SELECT SUM (cost) FROM Champions WHERE owned = 0").fetchone()[0]

        # Only get extra shards if they can be used, and will be subtracted
        if use_extra_shards and subtract_owned:
            # Get owned champions that also have shards
            try:
                owned_disenchant = self.con.execute("SELECT SUM (cost * champShards) FROM Champions WHERE" +
                                                    " owned = 1 AND champShards > 0").fetchone()[0] * .2
                current_ip += owned_disenchant
            except TypeError:
                # No owned champ shards to disenchant
                pass

            # Get duplicates for unowned champions
            try:
                unowned_extras = self.con.execute("SELECT SUM (cost*(champShards-1)) FROM Champions WHERE" +
                                                  " owned = 0 AND champShards > 1").fetchone()[0] * .2
                current_ip += unowned_extras
            except TypeError:
                # No unowned champs with 2 or more shards
                pass

        # if try fails, then the cost needed to purchase all champions is 0
        try:
            # If all champs are owned
            assert(maximum is not None)

            if version == "max":
                # If at max cost it is negative throw exception
                assert(maximum - current_ip > 0)
                return f'{int(maximum - current_ip):,}'
            elif version == "min":
                # If at min cost it is negative throw exception
                assert(int((maximum * .6) - current_ip) > 0)
                return f'{int((maximum * .6) - current_ip):,}'

            # Try to get all champions with shards. If it fails, then the discount is 0
            try:
                current_discount = self.con.execute("SELECT SUM (cost) FROM Champions WHERE " +
                                                    "owned = 0 AND champShards > 0").fetchone()[0] * .4
            except (SyntaxError, TypeError):
                current_discount = 0

            # If at current cost it is negative throw exception
            assert(maximum - current_discount - current_ip > 0)
            return f'{int(maximum - current_discount - current_ip):,}'

        except AssertionError:
            # Either no champs unowned, or user has enough IP
            return 0

    def print_all_data(self):
        """
        print_all_data prints the Champions table in champions.db

        :return:
        """
        all_data = self.con.execute("SELECT * FROM Champions")
        print(all_data.fetchall())

    def get_missions(self):

        response_json = self.call_api('/lol-missions/v1/missions')
        event_missions = []

        for mission in response_json:
            if mission["seriesName"].find("PROJECT") != -1:
                event_missions.append(mission)

        return event_missions

    def get_event_shop(self):
        # Get the event ID
        with self.con:
            event_id = self.con.execute("SELECT eventLootID FROM Player")

        if event_id is None:
            return "No event currently running. Refresh to check for an event"

        shop_items = self.call_api(f"/lol-loot/v1/recipes/initial-item/{event_id.fetchone()[0]}")
        for item in shop_items:
            print(item)


def sort_champs(champ):
    """
    Returns the name of a champion dictionary to be used for sorting

    :param champ: the dictionary representing the champion
    :return: Returns the name of the champion in the dictionary
    """
    return champ["name"]
