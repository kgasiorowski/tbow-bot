from requests import post, get
from time import sleep
import secret
from secret import WEBHOOK_URL
from json import load as load_json

def send_discord_message(content: str):
    post(WEBHOOK_URL, {"content": content})

def main():
    num_attempts = 0
    while True:
        response = get('https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player=UIM%20Crotch')
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

    with open(secret.GUESSES_PATH + 'guesses.json', 'r') as _:
        guesses = load_json(_)

    distances = []
    eliminatedPlayers = []
    for guess in guesses.items():
        if guess[1] >= cox_kc:
            distances.append((guess[0], guess[1], abs(guess[1]-cox_kc)))
        else:
            eliminatedPlayers.append(guess)

    topGuesses = sorted(distances, key=lambda d:d[2])[:3]

    content = f'Crotch\'s cox kc is: {cox_kc} (ranked {rank}).\n\n'

    content += 'The following players have been eliminated:\n'
    for player in eliminatedPlayers:
        content += f'{player[0]} ({player[1]})\n'

    content += '\nThe closest guesses are:\n'
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
        send_discord_message("Uh oh. Looks like I crashed. You suck at programming, look at my code again idiot.")