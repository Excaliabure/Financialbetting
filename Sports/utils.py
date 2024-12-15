import requests

class Odds():
    def __init__(self):
        self.odds_api_key = "636d5691d8f7230cc460a506e190314c"
        self.daily_fantasy_api_key = "660e9031-3f08-44e3-912f-69c9da920c08"

        
# dailyfantasy_data = requests.get(url_dailyfantasy,headers={"x-api-key" : "660e9031-3f08-44e3-912f-69c9da920c08"})
        
    def odds_api(self,regions,markets):
        """
        
        """
        url_odds_api = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds?apiKey={self.odds_api_key}{region_str}{market_str}&odds=american"
        


    # def daily_fantasy(self):
    #     url_dailyfantasy = "https://api.dailyfantasyapi.io/v1/lines/upcoming&sportsbook=PrizePicks&league=NFL"


    # def PrizePick(self):
    #     odds = None
    #     return odds
