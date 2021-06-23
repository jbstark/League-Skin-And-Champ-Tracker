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


class Client:

    def __init__(self):
        """
        Creates variables for find the client and lockfile. Then runs find client
        """

        # Create Data Folder for storing information
        self.data_folder_name = "data"
        if not os.path.exists(self.data_folder_name):
            os.makedirs(self.data_folder_name)

        # Disable InsecureRequestWarning as the connection to the client cannot be secure
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Stores client information
        self.settings = None

        # Variables for clientRunning
        self.clientRunning = False
        self.clientNames = ["leagueclientuxrender.exe", "leagueclientux"]
        self.possibleDirectories = set()
        self.currentDirectory = None

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
        self.con_machine = None

        self.check_local_information()
        self.check_client_running()

    # Client Checking Functions

    def check_client_running(self):
        """
        Checks to see if the client is running. First uses stored install directory
        If it is possibleDirectories is updated with the directory, and find_lockfile is run
        This should be where lockfile is
        If not, self.clientRunning will be false, and other functions will not run

        :return:
        """
        # First check local machine info to see if there is a stored install path
        # read the json
        data_path = os.path.join(self.data_folder_name, r'local_machine_info.json')
        with open(data_path, 'r') as infile:
            self.settings = json.load(infile)
            stored_paths = self.settings['Install Directories']
            skip_psutil = self.settings['Skip Psutil']

        for path in stored_paths:
            self.possibleDirectories.add(path)

        # Look for the lockfile using the stored directories
        self.find_lockfile()

        # If the lockfile was found, we don't need psutil and can skip this part. Also see if we should skip psutil
        if self.lockfileFound or skip_psutil:
            return

        # If no lockfile was found using the stored install directories use psutil to find process
        found_process = False
        for process in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process.name().lower() in self.clientNames:
                    self.possibleDirectories.add(process.cwd())
                    found_process = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if found_process:
            # Try to find the lockfile
            self.find_lockfile()

            # Client was running, but Lockfile was not found. Error and quit
            if self.lockfileFound is False:
                exit("Lockfile not found")

    def find_lockfile(self):
        """
        Finds the lockfile as long as lockfile is in a folder in possibleDirectories

        :return:
        """

        # Find the lockfile
        for path in self.possibleDirectories:
            # gets path for all operating systems
            lockfile = os.path.join(path, r'lockfile')

            # Try opening the lockfile
            try:
                with open(lockfile, 'r') as f:
                    file_contents = f.read().split(":")
                # Lockfile is found
                self.lockfileFound = True
                self.clientRunning = True
                self.currentDirectory = lockfile

                # Update local machine info for faster startup in the future
                data_path = os.path.join(self.data_folder_name, r'local_machine_info.json')
                with open(data_path, "r") as jsonFile:
                    data = json.load(jsonFile)

                # Get all previous install paths
                install_directories = data["Install Directories"]
                # Add current install path to list
                install_directories.append(path)

                # Create a set to remove duplicates
                data["Install Directories"] = list(set(install_directories))

                # Update the settings to include new information
                self.settings = data

                # Write all install paths to the json file
                with open(data_path, "w") as outfile:
                    json.dump(data, outfile, indent=4)

                break
            # League client is still opening, FAIL
            except FileNotFoundError:
                pass

        if self.lockfileFound is False:
            return

        # Get the port and password form the lockfile
        port = file_contents[2]
        password = file_contents[3]

        self.build_api(port, password)

        self.check_db()

    # Database and API management

    def check_local_information(self):

        # json file
        path = os.path.join(self.data_folder_name, r'local_machine_info.json')
        if os.path.exists(path):
            pass
        else:
            data = {
                'Install Directories': [],
                'Skip Psutil': False
            }
            with open(path, 'w') as outfile:
                json.dump(data, outfile, indent=4)

    def check_db(self):
        """
        Checks the database to make sure all the columns are there, adds if they are not

        :return:
        """

        # Create file for each user
        filename = "lol_" + self.summonerName + ".db"
        path = os.path.join(self.data_folder_name, f'{filename}')
        self.con = sqlite3.connect(path)

        # All columns (besides name) in the DB. Add a tuple here to add a column
        columns_champions = [("championID", "INTEGER"), ("owned", "INTEGER"), ("cost", "INTEGER"),
                             ("champShards", "INTEGER"), ("championMastery", "INTEGER"), ("masteryTokens", "INTEGER"),
                             ("lastPlayed", "INTEGER")]
        columns_player = [("summonerID", "INTEGER"), ("accountID", "INTEGER"), ("level", "INTEGER"),
                          ("blueEssence", "INTEGER"), ("riotPoints", "INTEGER"), ("eventName", "TEXT"),
                          ("eventTokens", "INTEGER"), ("eventLootID", "INTEGER"), ("eventEndDate", "INTEGER")]

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

        # Try connecting to the API
        self.test_api()

    def test_api(self):
        """
        Client has multiple loading phases, as plugins load. This waits until the plugins are active
        :return:
        """
        # Check to see if client is loading
        loading = True
        num_seconds = 0

        # While the client is loading
        while loading:
            # If over 15 seconds for client to load, quit
            if num_seconds > 15:
                self.clientRunning = False
                self.lockfileFound = False
                return
            # Wait 1 seconds then retry API call
            time.sleep(1)
            num_seconds += 1

            try:
                # Get summonerID of logged in user
                self.summonerInfo = self.call_api('/lol-summoner/v1/current-summoner')
                self.summonerId = self.summonerInfo["summonerId"]
                self.summonerName = self.summonerInfo["displayName"]
                self.currentPatch = self.call_api('/system/v1/builds')['version']

                loading = False
            except (KeyError, requests.exceptions.ConnectionError):
                pass

        # Get a response to see if parts of the client ares still loading
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
                        self.clientRunning = False
                        self.lockfileFound = False
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
        """

        :param address: The request to make to the API
        :return: the image from the call api (use .content to get the bytes string)
        """

        if self.clientRunning is False:
            return None
        request = self.url + address
        response = requests.get(request, verify=False, headers=self.header)

        return response

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

    # Update Functions

    def update(self):
        """
        Updates the information from the client. Used for changes in status (champions, skins, etc.)

        :return:
        """

        if self.clientRunning:
            # Refresh which champions are owned
            self.update_all_champions()
            # Update information about the summoner
            self.update_summoner()
        else:
            # If the client is not running, tries again
            self.check_client_running()

    def update_summoner(self):
        """
        Updates information for the summoner table including loot
        :return:
        """

        # Account info
        account_id = self.summonerInfo["accountId"]
        summoner_level = self.summonerInfo["summonerLevel"]

        # Store Info
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
        """
        Updates the user loot (loot tab) for events
        :return:
        """

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

                # To get rid of warnings
                first_mission = self.get_event_missions()[0]
                first_mission: dict
                end_time = first_mission["endTime"]

                # Add event end date
                self.add_to_database("Player", "username", self.summonerName, "eventEndDate", end_time)

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
            date = champion['lastPlayTime']
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

    # Get functions

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
        """
        Get a list of sorted champions by priorities

        :param primary_sort: First sort to use
        :param primary_direction: asc/desc
        :param secondary_sort: Second sort to break ties. Use same as primary for only one sort
        :param secondary_direction: asc/desc
        :param show_unowned: Boolean of whether to show unowned champions
        :return: list of champions
        """

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

    def get_event_missions(self):
        """
        Gets the missions for the event

        :return: returns a list of dictionaries with each mission
        """

        event_name = self.con.execute("SELECT eventName FROM Player").fetchone()[0]
        # Splits the first word of the event token name. Hopefully this is the name used in other events
        event_name = event_name.split(' ')[0]

        if event_name is None:
            return "No ongoing event"

        response_json = self.call_api('/lol-missions/v1/missions')
        event_missions = []

        for mission in response_json:
            if mission["seriesName"].find(event_name) != -1:
                event_missions.append(mission)
        return event_missions

    def get_event_shop(self):
        """
        Gets the event shop as a list of dictionaries for each item

        :return: list of dictionaries of items in the shop
        """

        # TODO check for owned content for events (grey out image if you own the max or the amount wanted?)
        shop = []
        # Get the event ID
        with self.con:
            event_id = self.con.execute("SELECT eventLootID FROM Player")

        if event_id is None:
            return "No event currently running. Refresh to check for an event"

        # Get all items in the event shop
        shop_items = self.call_api(f"/lol-loot/v1/recipes/initial-item/{event_id.fetchone()[0]}")

        for item in shop_items:
            # Get the image for the current item
            image_path = item['imagePath']
            # If there is no image path then it is a skin
            if image_path == '':
                # Get the skin ID
                skin_id = item["outputs"][0]["lootName"]
                skin_id = ''.join(i for i in skin_id if i.isdigit())
                # Get the champ_id
                skin_info = self.call_api(f'/lol-store/v1/skins/{skin_id}')
                champ_id = skin_info["itemRequirements"][0]["itemId"]

                # Make the image_path
                image_path = f"/lol-game-data/assets/v1/champion-tiles/{champ_id}/{skin_id}.jpg"

            shop.append((item["contextMenuText"], image_path, item["slots"][0]["quantity"]))
        return sorted(shop, key=lambda t: (t[2]), reverse=True)

    def get_tokens_per_day(self, target):
        """
        Returns the tokens per day needed to reach the target
        :param target: the amount of tokens desired by the end of the event
        :return: int of tokens needed per day
        """

        # TODO check if pass is owned

        self.update_user_loot()

        # Get total tokens
        total_tokens = self.get_current_tokens()

        # Tokens from missions/buying the pass
        event_name = self.con.execute("SELECT eventName FROM Player").fetchone()[0]
        if event_name.find("WORLDS") != -1:
            tokens_from_missions_left = 1815
        else:
            tokens_from_missions_left = 1500

        #  Get earned tokens from missions, 200 tokens from buying pass
        earned_from_missions = 200

        missions = self.get_event_missions()
        # To get rid of warnings
        mission: dict

        for mission in missions:
            # if the mission is completed
            if mission["completedDate"] != -1:
                # If the mission is not the bank missions for winning/losing games
                if mission["title"] != "Pass Token Bank Missions":
                    # In case of multiple rewards like icon and tokens
                    for reward in mission["rewards"]:
                        # If the reward is tokens and for this event
                        if reward["description"].find("Tokens") != -1 and reward["rewardFulfilled"] is True:
                            earned_from_missions += reward["quantity"]

        # Subtract your earned to get total still to earn
        tokens_from_missions_left -= earned_from_missions

        # Tokens assuming you complete all future missions
        total_tokens += tokens_from_missions_left

        # TODO Should target be stored?
        tokens_remaining = target - total_tokens

        # Get the event end time as datetime
        end_time = datetime.utcfromtimestamp(self.con.execute("SELECT eventEndDate FROM Player").fetchone()[0] // 1000)
        # Get number of days left
        days_left = (end_time - datetime.utcnow()).total_seconds()/86400

        # Tokens per hour times 24 for each hour in the day
        tokens_per_day = round(tokens_remaining/days_left, 3)

        if tokens_per_day < 0:
            return "Goal met"
        return tokens_per_day

    def get_current_tokens(self):
        return self.con.execute("SELECT eventTokens FROM Player").fetchone()[0]


def sort_champs(champ):
    """
    Returns the name of a champion dictionary to be used for sorting

    :param champ: the dictionary representing the champion
    :return: Returns the name of the champion in the dictionary
    """
    return champ["name"]
