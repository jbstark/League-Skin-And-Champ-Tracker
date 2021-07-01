import base64
import json
import logging
import logging.handlers
import os
import sqlite3
import time
from datetime import datetime, timedelta

import psutil
import requests
from PyQt5 import QtTest
from requests.packages.urllib3.exceptions import InsecureRequestWarning

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class Client:

    def __init__(self):
        """
        Creates variables for find the client and lockfile. Then runs find client
        """

        # Stores user settings
        self.data_folder_name = "data"
        self.settings = None
        self.check_settings()

        # Create the logger
        self.logs_folder_name = "logs"
        self.logger = None
        self.create_logger()

        # Disable InsecureRequestWarning as the connection to the client cannot be secure
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        # Variables for clientRunning
        self.clientRunning = False
        self.clientNames = ["leagueclientuxrender.exe", "leagueclientux"]
        self.possibleDirectories = set()
        self.currentDirectory = None

        # Variables needed for lockfile/api
        self.url = None
        self.header = None

        # Summoner Info
        self.summonerInfo = None
        self.summonerId = None
        self.summonerName = None

        # For connection to champions.db
        self.con = None

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
        self.logger.info("Checking if client is loaded")

        stored_paths = self.settings['Install Directories']
        skip_psutil = self.settings['Skip Psutil']

        if stored_paths:
            for path in stored_paths:
                self.possibleDirectories.add(path)

        # If no possible directories stored, ignore user setting and use psutil
        else:
            skip_psutil = False

        if self.find_lockfile():
            return

        if skip_psutil:
            self.logger.info("The League of Legends client is not running, or is running but an incorrect path is set. "
                             "Please update the path, or allow for automatic checking of processes in settings")
            return

        # skip_psutil is false in settings, or no stored directories
        self.find_client_process()

    def find_client_process(self):
        """
        Attempts to find the client process on the computer. Runs if skip_psutil is False or no stored directories
        :return:
        """
        self.logger.info("Using psutil to find client process")

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
            if self.find_lockfile() is False:
                self.logger.error("The client process was found, but the lockfile was not")
        else:
            self.logger.info("The League of Legends client is not running")

    def find_lockfile(self):
        """
        Finds the lockfile as long as lockfile is in a folder in possibleDirectories
        :return:
        """

        self.logger.info("Looking for lockfile")

        for path in self.possibleDirectories:
            lockfile = os.path.join(path, r'lockfile')
            try:
                with open(lockfile, 'r') as f:
                    lockfile_contents = f.read().split(":")
                self.logger.info(f"Client running. Lockfile found at {lockfile}")
                self.clientRunning = True
                self.currentDirectory = lockfile
                self.set_local_settings("Install Directories", path, True)

                port = lockfile_contents[2]
                password = lockfile_contents[3]

                self.build_api(port, password)
                self.check_db()
                self.update()

                return True
            except FileNotFoundError:
                pass

        return False

    # Database and API management

    def create_logger(self):
        """
        Creates the logger using user settings
        :return:
        """

        log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        level = log_levels[self.settings['Log Level']]

        if not os.path.exists(self.logs_folder_name):
            os.makedirs(self.logs_folder_name)

        log_filename = os.path.join("logs", time.strftime("%Y-%m-%d-"))

        # See if log file with name exists, and then try to increment log file by 1
        i = 1
        while os.path.exists(log_filename + "%s.log" % i):
            i += 1
        log_filename = log_filename + str(i) + ".log"

        # Create Custom Logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        handler = logging.FileHandler(log_filename, delay=True)
        handler.setLevel(level)
        handler_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%d-%b-%y %H:%M:%S')
        handler.setFormatter(handler_format)
        self.logger.addHandler(handler)

        self.logger.info("Logger successfully created")

    def check_settings(self):
        """
        Reads/ Creates a settings file depending on if it exists. Stores results in self.settings
        :return:
        """

        if not os.path.exists(self.data_folder_name):
            os.makedirs(self.data_folder_name)
        settings_path = os.path.join(self.data_folder_name, r'settings.json')

        # Default data to store in the json
        # Install Directories is a list of possible locations
        # Skip psutil is a bool of whether to look for processes
        # Log level (0-4) of which logs to show and up from 0-4 it's, DEBUG, INFO, WARNING, ERROR, CRITICAL
        default_data = {
            'Install Directories': [],
            'Skip Psutil': True,
            'Log Level': 1
        }

        # If the file exists, then look for new keys in default_data
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as infile:
                file_settings = json.load(infile)

                for key in default_data.keys():
                    file_settings.setdefault(key, default_data[key])

            with open(settings_path, 'w') as outfile:
                json.dump(file_settings, outfile, indent=4)
        # Create File
        else:
            with open(settings_path, 'w') as outfile:
                json.dump(default_data, outfile, indent=4)

        # Read the settings and place them in self.settings
        with open(settings_path, 'r') as infile:
            self.settings = json.load(infile)

    def check_db(self):
        """
        Checks the database to make sure all the columns are there, adds if they are not
        :return:
        """

        self.logger.info("Checking database files")

        # Check for if the client was closed
        if not self.summonerName:
            self.logger.error(f'Client has been quit during operations. Please refresh')
            return

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
                          ("eventTokens", "INTEGER"), ("eventLootID", "INTEGER"), ("tokenEndDate", "INTEGER"),
                          ("shopEndDate", "INTEGER")]

        with self.con:
            self.con.execute("CREATE TABLE if not exists Champions (name TEXT UNIQUE)")
            self.con.execute("CREATE TABLE if not exists Player (username TEXT UNIQUE)")

            for col in columns_champions:
                col_name = col[0]
                col_type = col[1]
                try:
                    self.con.execute(f"ALTER TABLE Champions ADD COLUMN {col_name} {col_type}")
                except sqlite3.OperationalError:
                    # Column Already Exists
                    pass

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

        self.logger.info("Retrieving information for API calls")

        self.url = 'https://127.0.0.1:' + port
        authorization = "riot:" + password
        authorization_b64 = base64.b64encode(authorization.encode()).decode()
        self.header = {"Accept": "application/json", "Authorization": "Basic " + authorization_b64}

        self.test_api()

    def test_api(self):
        """
        Client has multiple loading phases, as plugins load. This waits until the plugins are active
        :return:
        """

        self.logger.info("Testing API to ensure it is running")

        basic_api_loading = True
        attempt = 1
        basic_time = time.time()

        while basic_api_loading:
            if attempt > 9:
                self.clientRunning = False
                self.logger.warning('Basic API never loaded. Either client is slow, or was quit. Time taken:' +
                                    f'{time.time() - basic_time}')
                return
            try:
                self.summonerInfo = self.call_api('/lol-summoner/v1/current-summoner')
                self.summonerId = self.summonerInfo["summonerId"]
                self.summonerName = self.summonerInfo["displayName"]
                basic_api_loading = False
                self.logger.info(f"Summoner {self.summonerName} has been found")

            except (KeyError, requests.exceptions.ConnectionError):
                self.logger.warning(f'Basic API not fully loaded, attempt number {attempt}')
                QtTest.QTest.qWait(1000)
                attempt += 1
                pass

        # Same as above but for champion api
        champ_api_loading = True
        attempt = 1
        champion_time = time.time()

        while champ_api_loading:
            if attempt > 9:
                self.clientRunning = False
                self.logger.warning('Champion API never loaded. Either client is slow, or was quit. Time taken' +
                                    f':{time.time() - champion_time}')
                return
            try:
                response = self.call_api(f'/lol-champions/v1/inventories/{self.summonerId}/champions-minimal')
                if response['message'] == 'Champion data has not yet been received.':
                    self.logger.warning(f'Champion API not fully loaded, attempt number {attempt}')
                    QtTest.QTest.qWait(1000)
                    attempt += 1
                    pass
            except (KeyError, TypeError, requests.exceptions.ConnectionError):
                champ_api_loading = False

    def call_api(self, address):
        """
        Calls the API
        :param address: The request to make to the API
        :return: the json of the response
        """
        self.logger.debug(f"Calling API with address {address}")

        if self.clientRunning is False:
            return None
        response = requests.get(self.url + address, verify=False, headers=self.header)
        return json.loads(response.text)

    def call_api_image(self, address):
        """
        Calls the API, but returns just the response instead of the json
        :param address: The request to make to the API
        :return: the image from the call api (use .content to get the bytes string)
        """
        self.logger.debug(f"Calling API image with address {address}")

        if self.clientRunning is False:
            return None
        response = requests.get(self.url + address, verify=False, headers=self.header)
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

        self.logger.debug(f"Adding {data} to {table} in column {column} where row {row} is {comparison}")

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

        self.con.execute(f'UPDATE {table} SET {column} = {data} WHERE {row} = {comparison}')
        self.con.commit()

    # Update Functions

    def update(self):
        """
        Updates the information from the client. Used for changes in status (champions, skins, etc.)
        Does NOT update RP as it is an expensive call
        :return:
        """

        self.logger.info(f"Starting Update")

        # see if user logged out between last update
        try:
            self.call_api('/lol-summoner/v1/current-summoner')
        except requests.exceptions.ConnectionError:
            self.logger.warning("Could not find the current summoner. A new summoner or no summoner is logged in")
            self.clientRunning = False
            self.check_client_running()
            self.logger.warning("The client could not be found")

        if self.clientRunning:
            self.update_summoner()
            self.update_all_champions()
            self.update_loot()
            self.update_event()
        else:
            self.check_client_running()
            if not self.clientRunning:
                self.logger.warning("The client could not be found")

    def update_summoner(self):
        """
        Updates information for the summoner table including loot
        :return:
        """

        self.logger.info(f"Starting Update Summoner")

        # Account info
        account_id = self.summonerInfo["accountId"]
        summoner_level = self.summonerInfo["summonerLevel"]

        # Update player information
        self.con.execute(f'INSERT or IGNORE INTO Player (username) VALUES (?)', (self.summonerName,))
        self.add_to_database("Player", "username", self.summonerName, "summonerID", self.summonerId)
        self.add_to_database("Player", "username", self.summonerName, "accountID", account_id)
        self.add_to_database("Player", "username", self.summonerName, "level", summoner_level)

    def update_rp(self):
        """
        Updates the rp in the db
        :return:
        """

        self.logger.info(f"Starting Update RP")

        wallet = self.call_api("/lol-store/v1/wallet")
        rp = wallet["rp"]
        self.add_to_database("Player", "username", self.summonerName, "riotPoints", rp)

    def update_all_champions(self):
        """
        Gets champion information form LCU
        Calls update_champion_costs(), update_mastery_and_date(), update_champion_loot()

        :return:
        """

        self.logger.info(f"Starting Update All Champions")

        # Make request for all champion data
        all_champions_api = self.call_api(f'/lol-champions/v1/inventories/{self.summonerId}/champions-minimal')
        all_champions_db = self.get_all_champs()
        unowned_champions = self.get_champs(False)

        # if the API call fails
        if all_champions_api is None:
            return "Client not connected. Please refresh"

        all_champions_api.sort(key=sort_champs)

        # If there is a new champion or an unowned is bought
        self.logger.info(f"Checking for a new champion and/or if any unowned champions were bought")

        for champion in all_champions_api:
            champion_name = champion['name']
            if champion['name'] != "None" and champion["name"] not in all_champions_db:
                # Add champion to Database
                self.con.execute(f'INSERT or IGNORE INTO Champions (name) VALUES (?)', (champion_name,))

                # Add ID to Database
                champion_id = champion['id']
                self.add_to_database("Champions", "name", champion_name, "championID", champion_id)

                # Add Owned Status
                self.add_to_database("Champions", "name", champion_name, "owned", int(champion["ownership"]["owned"]))
            if champion['name'] in unowned_champions:
                # Add Owned Status to Database
                if int(champion["ownership"]["owned"]) != 0:
                    self.add_to_database("Champions", "name", champion_name, "owned", 1)

        # Update other columns
        self.update_champion_costs()

        self.update_mastery_and_date()

    def update_champion_costs(self):
        """
        Updates the cost of champions in the champions.db table.

        :return:
        """

        self.logger.info(f"Starting Update Champion Costs")

        # Make request
        costs = self.call_api('/lol-store/v1/catalog?inventoryType=%5B%22CHAMPION%22%5D')

        # if the API call fails
        if costs is None:
            return "Client not connected. Please refresh"

        # Get the localization for getting champion cost
        localization = [*costs[0]["localizations"]][0]

        for champion in costs:
            name = champion["localizations"][localization]["name"]
            ip_cost = str(champion["prices"][0]["cost"])
            self.add_to_database("Champions", "name", name, "cost", ip_cost)

    def update_mastery_and_date(self):
        """
        Updates champion mastery and date last played in champions.db

        :return:
        """

        self.logger.info(f"Starting Update Mastery And Date")

        mastery = self.call_api(f'/lol-collections/v1/inventories/{self.summonerId}/champion-mastery')

        # if the API call fails
        if mastery is None:
            return "Client not connected. Please refresh"

        for champion in mastery:
            mastery_level = champion['championLevel']
            # Last date mastery points were gained on a champion, NOT last played (bots don't count)
            date = champion['lastPlayTime']
            self.add_to_database("Champions", "championID", champion["championId"], "championMastery", mastery_level)
            self.add_to_database("Champions", "championID", champion["championId"], "masteryTokens", 0)
            self.add_to_database("Champions", "championID", champion["championId"], "lastPlayed", date)

    def update_loot(self):
        """
        Updates champion shards and mastery tokens in champions.db

        :return:
        """

        self.logger.info(f"Starting Update Champion Loot")

        loot = self.call_api('/lol-loot/v1/player-loot')

        # if the API call fails
        if loot is None:
            return "Client not connected. Please refresh"

        # Lists of all champions, takes off champions with values to then have all that should be 0
        champs_no_shards = self.get_all_champs()
        eligible_mastery_champs = self.con.execute("SELECT name FROM Champions WHERE championMastery = 5 " +
                                                   "OR championMastery = 6").fetchall()
        champs_no_mastery_tokens = [name[0] for name in eligible_mastery_champs]

        for item in loot:
            # Champion Shards
            if item["displayCategories"] == "CHAMPION":
                name = item["itemDesc"]
                num_owned = item["count"]
                self.add_to_database("Champions", "name", name, "champShards", num_owned)
                # Remove champion from list, as its value will be added
                champs_no_shards.remove(name)

            # Mastery Tokens
            elif item["displayCategories"] == "CHEST" and item["type"] == "CHAMPION_TOKEN":
                name = item["itemDesc"]
                num_owned = item["count"]
                self.add_to_database("Champions", "name", name, "masteryTokens", num_owned)
                # Remove champion from list, as its value will be added
                champs_no_mastery_tokens.remove(name)

            # Blue essence
            elif item['asset'] == "currency_champion":
                be = item["count"]
                self.add_to_database("Player", "username", self.summonerName, "blueEssence", be)

        # All champions with no shards should be set to null
        for champ in champs_no_shards:
            self.add_to_database("Champions", "name", champ, "champShards", 0)

        # All champions with no tokens should be set to null
        for champ in champs_no_mastery_tokens:
            self.add_to_database("Champions", "name", champ, "masteryTokens", 0)

    def update_event(self):
        """
        Updates the event_name, token_id, token_count, and event end date
        :return:
        """

        self.logger.info(f"Starting Update Event")

        shop_end_time = self.con.execute("SELECT shopEndDate FROM Player").fetchone()[0]

        # Shop has closed
        if shop_end_time and time.time() > shop_end_time:
            # Event is fully over
            self.logger.info("Event not running, as the token shop has closed")
            self.add_to_database("Player", "username", self.summonerName, "eventName", None)
            self.add_to_database("Player", "username", self.summonerName, "eventTokens", None)
            self.add_to_database("Player", "username", self.summonerName, "eventLootID", None)
            self.add_to_database("Player", "username", self.summonerName, "tokenEndDate", None)
            self.add_to_database("Player", "username", self.summonerName, "shopEndDate", None)

        # Event info stored so only need to update tokens
        if self.con.execute("SELECT eventLootID FROM Player").fetchone()[0]:
            self.logger.info("Event information is stored, and only the token count should be updated")

            # Number of tokens
            token_id = self.con.execute("SELECT eventLootID FROM Player").fetchone()[0]
            current_tokens = self.call_api(f"/lol-loot/v1/player-loot/{token_id}")["count"]
            self.add_to_database("Player", "username", self.summonerName, "eventTokens", current_tokens)
            return

        # Can I get rid of this call?
        store = self.call_api("/lol-store/v1/featured")

        # Event Name using pass
        for item in store["catalog"]:
            if item['inventoryType'] == "BUNDLES":
                for loot in item['bundleItems']:
                    # If other bundles has tokens, change this line to something more unique
                    if loot["name"].find("Token") != -1:
                        self.logger.info("Found event information")

                        # Event name
                        event_name = item["name"].split()[1]
                        self.add_to_database("Player", "username", self.summonerName, "eventName", event_name)

                        # Event loot ID
                        token_id = "MATERIAL_" + str(loot["itemId"])
                        self.add_to_database("Player", "username", self.summonerName, "eventLootID", token_id)

                        # Number of tokens
                        current_tokens = self.call_api(f"/lol-loot/v1/player-loot/{token_id}")["count"]
                        self.add_to_database("Player", "username", self.summonerName, "eventTokens", current_tokens)

                        # Token end date
                        event_mission = self.get_event_missions()[0]
                        event_mission: dict
                        end_time = None
                        if event_mission:
                            end_time = event_mission["endTime"]
                        self.add_to_database("Player", "username", self.summonerName, "tokenEndDate", end_time)

                        # Shop End Date
                        shop_end = datetime.strptime(item["inactiveDate"], "%Y-%m-%dT%H:%M:%S.%f%z")
                        # Bundles end 2 hours before shop, add 2 hours. * 1000 for milliseconds
                        shop_end = (shop_end + timedelta(hours=2)).timestamp() * 1000
                        self.add_to_database("Player", "username", self.summonerName, "shopEndDate", shop_end)

    # Get functions

    def get_all_champs(self):
        """
        get_all_champs returns a list of ALL champions in the game

        :return: Returns a list
        """

        self.logger.info(f"Getting All Champions")

        with self.con:
            owned = self.con.execute("SELECT name FROM Champions")
        champions = owned.fetchall()

        return [champion[0] for champion in champions]

    def get_champs(self, owned_status):
        """
        get_champs returns a list of owned or unowned champions

        :param owned_status: Boolean for if the function should find owned (True) or unowned (False) champions
        :return: Returns a list of owned or unowned champions
        """

        self.logger.info(f"Getting all champions where owned is {owned_status}")

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

        self.logger.info(f"Getting number of champions where owned is {owned_status}")

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
        self.logger.info(f"Sorting champions by {primary_sort} {primary_direction}, and then " +
                         f"{secondary_sort} {secondary_direction}")

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

        self.logger.info(f"Getting IP needed using {version} and subtracting owned is {subtract_owned}. " +
                         f"Using extra shards is {use_extra_shards}")

        # If the program should subtract IP in the account, get the current_ip
        if subtract_owned:
            current_ip = self.con.execute("SELECT blueEssence FROM Player").fetchone()[0]
        else:
            current_ip = 0

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
            return "0"

    def get_event_missions(self):
        """
        Gets the missions for the event

        :return: returns a list of dictionaries with each mission
        """

        self.logger.info(f"Getting all event missions.")

        event_name = self.con.execute("SELECT eventName FROM Player").fetchone()[0]

        if event_name is None:
            self.logger.warning(f"Event not running, or shop not found")
            return

        all_missions = self.call_api('/lol-missions/v1/missions')
        event_missions = []

        for mission in all_missions:
            if mission["seriesName"].find(event_name) != -1:
                event_missions.append(mission)
        return event_missions

    def get_event_shop(self):
        """
        Gets the event shop as a list of dictionaries for each item

        :return: list of dictionaries of items in the shop
        """

        self.logger.info(f"Getting event shop.")

        # TODO check for owned content for events (grey out image if you own the max or the amount wanted?)
        shop = []

        event_id = self.con.execute("SELECT eventLootID FROM Player")

        if event_id is None:
            self.logger.warning(f"Event not running, or shop not found")
            return

        shop_items = self.call_api(f"/lol-loot/v1/recipes/initial-item/{event_id.fetchone()[0]}")

        for item in shop_items:
            image_path = item['imagePath']
            # If there is no image path then it is a skin
            if image_path == '':
                skin_id = item["outputs"][0]["lootName"]
                skin_id = ''.join(i for i in skin_id if i.isdigit())
                skin_info = self.call_api(f'/lol-store/v1/skins/{skin_id}')
                champ_id = skin_info["itemRequirements"][0]["itemId"]
                # Make the image_path
                image_path = f"/lol-game-data/assets/v1/champion-tiles/{champ_id}/{skin_id}.jpg"

            # See if loot is owned
            owned = False
            output = item['outputs'][0]['lootName']
            loot = self.call_api(f"/lol-loot/v1/player-loot/{output}")
            if loot["redeemableStatus"] == "ALREADY_OWNED":
                owned = True

            shop.append((item["contextMenuText"], image_path, item["slots"][0]["quantity"], owned))

        shop_alphabet_sorted = sorted(shop, key=lambda t: (t[0]), reverse=False)
        shop_cost_sorted = sorted(shop_alphabet_sorted, key=lambda t: (t[2]), reverse=True)
        return shop_cost_sorted

    def get_tokens_per_day(self, target):
        """
        Returns the tokens per day needed to reach the target
        :param target: the amount of tokens desired by the end of the event
        :return: int of tokens needed per day
        """

        self.logger.info(f"Getting tokens per day with a target of {target}.")

        # updating the event to make sure all is up to date
        self.update_event()

        # End time
        try:
            end_time = datetime.utcfromtimestamp(
                self.con.execute("SELECT tokenEndDate FROM Player").fetchone()[0] // 1000)
            days_left = (end_time - datetime.utcnow()).total_seconds() / 86400
        except TypeError:
            self.logger.info(f"Tried to get tokens per day for {target}, but there is no stored date in the db")
            return "Event not running"

        if days_left < 0:
            self.logger.info(f"Tried to get tokens per day for {target}, but tokens can no longer be earned")
            return "Tokens can no longer be earned"

        if target is None or target == 0:
            self.logger.warning(f"No target specified")
            return "No target tokens"

        total_tokens = self.get_current_tokens()

        event_name = self.con.execute("SELECT eventName FROM Player").fetchone()[0]

        if event_name is None:
            self.logger.warning(f"Event not running, or tokens not found")
            return

        if event_name.find("WORLDS") != -1:
            tokens_from_missions_left = 1815
        else:
            tokens_from_missions_left = 1500

        earned_from_missions = 200

        missions = self.get_event_missions()
        mission: dict

        for mission in missions:
            if mission["completedDate"] != -1:
                if mission["title"] != "Pass Token Bank Missions":
                    for reward in mission["rewards"]:
                        if reward["description"].find("Tokens") != -1 and reward["rewardFulfilled"] is True:
                            earned_from_missions += reward["quantity"]

        tokens_from_missions_left -= earned_from_missions

        # Tokens assuming you complete all future missions
        total_tokens += tokens_from_missions_left

        tokens_remaining = target - total_tokens

        tokens_per_day = round(tokens_remaining / days_left, 3)

        if tokens_per_day < 0:
            return "Goal met"
        return tokens_per_day

    def get_current_tokens(self):
        """

        :return: The current tokens in the db (update should be called before)
        """
        self.logger.info("Getting current tokens.")
        tokens = self.con.execute("SELECT eventTokens FROM Player").fetchone()[0]
        if tokens is None:
            self.logger.warning(f"Event not running")
        return tokens

    # Setter functions

    def set_local_settings(self, setting, value, add_not_update):
        """
        Set local settings for the user stored in settings.json

        :param setting: name of the setting in the json to edit
        :param value: Value to insert into the json
        :param add_not_update: Bool for whether to add (true) or update (false) the value
        :return:
        """

        settings_path = os.path.join(self.data_folder_name, r'settings.json')

        if add_not_update:

            if not isinstance(self.settings[setting], list):
                self.logger.warning("Set settings called with add, but no list found")
                return

            # Setting is a set with value added, formatted as a list for json
            if value not in self.settings[setting]:
                self.logger.info(f"Adding local setting {setting} to {value}.")
                self.settings[setting].append(value)
                self.settings[setting] = list(set(self.settings[setting]))

        else:
            self.logger.info(f"Setting local setting {setting} to {value}.")
            self.settings[setting] = value

        with open(settings_path, "w") as outfile:
            json.dump(self.settings, outfile, indent=4)


def sort_champs(champ):
    """
    Returns the name of a champion dictionary to be used for sorting

    :param champ: the dictionary representing the champion
    :return: Returns the name of the champion in the dictionary
    """
    return champ["name"]
