from requests import post, get
from time import sleep
import config
from config import WEBHOOK_URL
from json import load as load_json
from json import dump as dump_json

purple_item_names = ['Ancestral hat',
                     'Ancestral robe bottom',
                     'Ancestral robe top',
                     'Arcane prayer scroll',
                     'Dexterous prayer scroll',
                     "Dinh's bulwark",
                     'Dragon claws',
                     'Dragon hunter crossbow',
                     'Elder maul',
                     'Kodai insignia',
                     'Twisted bow',
                     'Twisted buckler']

def send_discord_message(content: str):
    post(WEBHOOK_URL, {"content": content})

def main():
    num_attempts = 0
    while True:
        response = get('https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws', {'player': config.USERNAME})
        num_attempts += 1
        if response.status_code == 200:
            break
        if num_attempts > 20:
            print('OSRS hiscores api failed after more than 20 tries, aborting.')
            send_discord_message('I tried to get the hiscores data a lot of times but I kept failing. Maybe the hiscores are down?')
            exit(1)
        print('There was an issue with the osrs hiscores API. Retrying in 2 minutes')
        sleep(120)

    hiscore_values = response.content.decode().replace('\n', ',').split(',')
    cox_kc = int(hiscore_values[113])
    rank = int(hiscore_values[112])

    try:
        with open(config.PROJECT_PATH + 'previous_kc.json', 'r') as _:
            previous_kc = load_json(_)
    except FileNotFoundError:
        previous_kc = 0

    if cox_kc == previous_kc:
        return
    else:
        with open(config.PROJECT_PATH + 'previous_kc.json', 'w') as _:
            dump_json(cox_kc, _)

    content = f'Crotch\'s cox kc is: {cox_kc} (+{cox_kc-previous_kc}) (ranked {rank}).\n\n'

    try:
        with open(config.PROJECT_PATH + 'previous_collection_log.json', 'r') as _:
            previous_coll_log = load_json(_)
    except FileNotFoundError:
        previous_coll_log = False

    results = get(f'https://api.collectionlog.net/collectionlog/user/{config.USERNAME}').json()
    cox = results['collectionLog']['tabs']['Raids']['Chambers of Xeric']['items']
    cox_loot = {item['name']: item['quantity'] for item in cox}

    if not previous_coll_log:
        with open(config.PROJECT_PATH + 'previous_collection_log.json', 'w') as _:
            dump_json(cox_loot, _)
        previous_coll_log = cox_loot

    if cox_loot != previous_coll_log:
        with open(config.PROJECT_PATH + 'previous_collection_log.json', 'w') as _:
            dump_json(cox_loot, _)
        excluded_uniques = ['Dark relic', 'Torn Prayer Scroll']
        content += 'He obtained the following uniques since I was last run:\n'
        for unique in cox_loot.keys():
            if unique.lower() in [unique.lower() for unique in excluded_uniques]:
                continue

            if cox_loot[unique] != previous_coll_log[unique]:
                content += f'+{cox_loot[unique] - previous_coll_log[unique]} {unique} - totalling {cox_loot[unique]}\n'

        content += '\n'

    content += f'Total purps: {sum([count for unique, count in cox_loot.items() if unique in purple_item_names])}\n\n'

    with open(config.PROJECT_PATH + 'guesses.json', 'r') as _:
        guesses = load_json(_)

    distances = []
    eliminatedPlayers = []
    for guess in guesses.items():
        if guess[1] > cox_kc:
            distances.append((guess[0], guess[1], abs(guess[1]-cox_kc)))
        else:
            eliminatedPlayers.append(guess)

    eliminatedPlayers = sorted(eliminatedPlayers, key=lambda a:a[1])
    topGuesses = sorted(distances, key=lambda d:d[2])[:3]

    content += 'The following players have been eliminated:\n'
    for player in eliminatedPlayers:
        content += f'- {player[0]} ({player[1]})\n'

    content += '\nThe next closest guesses are:\n'
    counter = 1
    for player in topGuesses:
        content += f'{counter}. {player[0]} ({player[1]})\n'
        counter += 1

    content += '\nSee you tomorrow.'

    send_discord_message(content)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        send_discord_message(f"Uh oh. Looks like I crashed. You suck at programming, look at my code again idiot. \n{e}")