import requests

class matchLists ():
    def __init__(self, puuid, matchNumber, token):
        self.token = token
        self.puuid = puuid
        self.star = 0
        self.matchNumber = matchNumber

    def get_matchLists(self):
        url = (f'https://americas.api.riotgames.com/tft/match/v1/matches/by-puuid/{self.puuid}/ids?start={self.star}&count={self.matchNumber}&api_key={self.token}')

        response = requests.get(url)
        matchIds = response.json()
        #print(matchIds)

        return matchIds