# League-Skin-And-Champ-Tracker
A Skin, Champion, and Event Tracker for League of Legends

Provides insights into:
- Blue Essence needed to unlock all champions
- Tokens needed per day to hit your target goal
- More to come

# Getting Started
Currently there are no downloads for compiled versions, but you can clone the repository and run LeagueTrackerGui.py.

<strong>Requirements</strong><br/>
The project is coded in python, and should be ran with python 3.8

The project currently requires some libraries to run.
- psutil (to look for a running league process)
- requests (to query the league client api)
- PyQt5 (to run the GUI)

# Data
Data is stored per user in /data. To read this outside of the client use a db reader

# Frequently Asked Questions

- [Why did it fail to connect while the league client was open](#Why-did-it-fail-to-connect-while-the-league-client-was-open)


## Why did it fail to connect while the league client was open

The connection procress goes through 3 steps. First it looks for the process (either stored or using psutil). Second, it looks for the lockfile created when the client is opened for information needed to use the API. Lastly, it tests the API until it works. Sometimes, if the client is still loading, the program will try the API too many times and quit. This cannot be made faster, as the league client would need to load faster. Eventually, we hope to have a setting for how long it should retry for. While opening the league client is the most common way this happens, any time it is loading a new account it can occure, including signing out and signing back in. If you belive it to be a diffent reason, please [open an issue](https://github.com/jbstark/League-Skin-And-Champ-Tracker/issues/new) with the speicifcs and we can look into it.
