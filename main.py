import requests
import pandas as pd
from auth import user_authentication
from matchs import matchLists


#USE TO FORMAT JSON
#import json


#Get information based on player information
name = 'GBA' #str(input('Accont name: '))
tag = 'TFT' #str(input('tag name: '))
api_key = 'RGAPI-21aaf387-d5ce-48c8-be08-b394fa33e212'

user_auth = user_authentication(name, tag, api_key)
puuid = user_auth.get_puuid()

#Get number of match ids 'order desc'
matchNumer = int(input('Number of Matchs to recover: '))
user_matchs = matchLists(puuid, matchNumer, api_key)
matchIds = user_matchs.get_matchLists()

playerDataBase = {
                    "puuid": [puuid],
                    "riotIdGameName": [name],
                    "riotIdTagline": [tag]
                }
        
df_playerInformation = pd.DataFrame(playerDataBase)
print(df_playerInformation)

for i, match_position in enumerate(matchIds, start=0):

    url = (f'https://americas.api.riotgames.com/tft/match/v1/matches/{match_position}?api_key={api_key}')

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        info = data.get("info",{})

        print(f"\n🔹 Analisando partida {match_position} 🔹")

        endOfGameResult = info["endOfGameResult"]
        gameCreation = info["gameCreation"]
        game_datetime = info["game_datetime"]
        game_length = info["game_length"]
        mapId = info["mapId"]
        
        #print(json.dumps(info, indent=4, ensure_ascii=False))
        
        for player in info.get("participants"):
            if player["riotIdGameName"] == name and player["riotIdTagline"] == tag:
                riotIdGameName = player['riotIdGameName']
                riotIdTagline = player["riotIdTagline"]
                placement = player["placement"]
                damageCaused = player["total_damage_to_players"]
                isWin = player["win"]
                
                champs = [(unit['character_id'], unit['itemNames']) for unit in player['units']]

                matchResume = {
                    "matchId": [match_position],
                    "gameCreation": [gameCreation],
                    "game_datetime": [game_datetime],
                    "endOfGameResult": [endOfGameResult],
                    "game_length": [game_length],
                    "mapId": [mapId],
                    "puuid": [puuid],
                    "damageCaused": [damageCaused],
                    "placement": [placement],
                    "isWin": [isWin]
                }

                df_matchResume = pd.DataFrame(matchResume)

                print(df_matchResume)

                # for unit in player['units']:
                #     champs = [
                #         unit["character_id"],
                #         unit['itemNames']
                #     ]
    else:
        print(f"Erro ao obter dados da partida: {response.status_code} - {response.text}")
