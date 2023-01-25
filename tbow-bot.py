from requests import post, get
from secret import WEBHOOK_URL

if __name__ == "__main__":

    cox_kc = get('https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?player=Crotch%20Flame').content.decode()
    cox_kc = cox_kc.replace('\n', ',').split(',')[113]
    response = post(WEBHOOK_URL, {'content':f"Crotch's cox kc is: {cox_kc}. See you tomorrow."})
