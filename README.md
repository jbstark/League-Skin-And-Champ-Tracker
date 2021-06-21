# League-Skin-And-Champ-Tracker
A Skin, Champion, and Event Tracker for League of Legends

Provides insights into:
- Blue Essence needed to unlock all champions
- Tokens needed per day to hit your target goal
- And other information

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
