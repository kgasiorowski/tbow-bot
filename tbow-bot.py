from requests import post, get

import secret
from secret import WEBHOOK_URL
from json import load as load_json

if __name__ == "__main__":

    cox_kc = get('https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player=Crotch%20Flame').content.decode()
    cox_kc = int(cox_kc.replace('\n', ',').split(',')[113])

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

    content = f'Crotch\'s cox kc is: {cox_kc}.\n\n'

    content += 'The following players have been eliminated:\n'
    for player in eliminatedPlayers:
        content += f'{player[0]} ({player[1]})\n'

    content += '\nThe closest guesses are:\n'
    counter = 1
    for player in topGuesses:
        content += f'{counter}. {player[0]} ({player[1]})\n'
        counter += 1

    content += '\nSee you tomorrow.'

    post(WEBHOOK_URL, {'content':content})
