#Requires: Requests
import requests


API_KEY = "RGAPI-de6f5e0d-f45e-4a09-9751-ef0f4b2410a1"
summoner_name = "jjrsk"
language = "en_US"




url = "https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + summoner_name + "?api_key="+API_KEY
response = requests.get(url)

summoner_id = response.json()["id"]


print(response.json())

print(response.json()["id"])