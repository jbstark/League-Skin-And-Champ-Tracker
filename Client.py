import requests
import base64
from tkinter import *


class Client:

    def __init__(self, lockfile):
        # Open the lockfile
        try:
            with open(lockfile, 'r') as f:
                file_contents = f.read().split(":")
        except FileNotFoundError:
            # League Client Not Open
            # TODO instead of quitting allow for refresh
            print("League Client Not Opened")
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

    def get_owned_champions(self):
        request = self.url + '/lol-champions/v1/owned-champions-minimal'

        # Make request
        print(request)
        response = requests.get(request, verify=False, headers=self.header)
        print(response)
