from Client import *

client = Client()

print("Owned")
print(client.get_champs(True))
print("Num Owned")
print(client.get_num_champs(True))

print("Unowned")
print(client.get_champs(False))
print("Num Unowned")
print(client.get_num_champs(False))

print("IP Max:", client.get_ip_needed("max", False, True))
print("IP Max minus owned:", client.get_ip_needed("max", True, True))

print("IP Min:", client.get_ip_needed("min", False, True))
print("IP Min minus owned:", client.get_ip_needed("min", True, True))

print("IP Current:", client.get_ip_needed("current", False, True))
print("IP Current minus owned:", client.get_ip_needed("current", True, True))

print("All Data")
client.print_all_data()

client.get_sorted_champs("lastPlayed", "desc", "name", "asc", True)

print(client.call_api('/lol-game-data/assets/v1/champion-icons'))