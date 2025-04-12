import requests

class user_authentication():
    def __init__(self, player_name, tag_name, token):
        self.player_name = player_name
        self.tag_name = tag_name
        self.token = token

    def get_puuid(self):
        url = (f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{self.player_name}/{self.tag_name}?api_key={self.token}')
        
        response = requests.get(url)

        if response.status_code == 200:
            print('//----------------User Authorized----------------//')
            data = response.json()
            puuid = data['puuid']

            return puuid
        else:
            return "Unauthorized: " + str(response.status_code)
