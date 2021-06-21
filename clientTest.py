from Client import *
client = Client()

if not client.clientRunning:
    exit("Client not running")

print("Owned")
print(client.get_champs(True))
print("Num Owned:", client.get_num_champs(True), "\n")


print("Unowned")
print(client.get_champs(False))
print("Num Unowned:", client.get_num_champs(False), "\n")

print("IP Max:", client.get_ip_needed("max", False, True))
print("IP Max minus owned:", client.get_ip_needed("max", True, True), "\n")

print("IP Min:", client.get_ip_needed("min", False, True))
print("IP Min minus owned:", client.get_ip_needed("min", True, True), "\n")

print("IP Current:", client.get_ip_needed("current", False, True))
print("IP Current minus owned:", client.get_ip_needed("current", True, True), "\n")

print("All Data")
client.print_all_data()

print("\n", "Champions by most recent played")
client.get_sorted_champs("lastPlayed", "desc", "name", "asc", True)

print("\n", "Missions")
print(client.get_missions())

print("\n", "Event Shop")
print(client.get_event_shop())

print("\n", "Tokens needed each day:", client.get_tokens_per_day(2200))
