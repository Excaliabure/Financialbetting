import requests
from bs4 import BeautifulSoup


teams_id = {"T1" : 2144,
            "Hanwha" : 2122}

url = f"https://gol.gg/teams/team-stats/2144/split-Summer/tournament-ALL/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

a = requests.get(url,headers=headers)
