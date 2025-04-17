import requests 
import pandas as pd  
import json
import os
from auth import user_authentication  
from matchs import matchLists  
from pg_connection import pg_connection

name = 'GBA' 
tag = 'TFT'  
api_key = 'RGAPI-47a96b62-5257-452c-b3fc-fb3dea34251e' 

user_auth = user_authentication(name, tag, api_key)
puuid = user_auth.get_puuid()

matchNumer = int(input('Number of Matchs to recover: '))
user_matchs = matchLists(puuid, matchNumer, api_key)
matchIds = user_matchs.get_matchLists()

df_playerInformation = pd.DataFrame(
    {
    "puuid": [puuid],
    "riotIdGameName": [name],
    "riotIdTagline": [tag]
    }
)

mathStatusFormation = []
chapionsFormation = []

for i, match_position in enumerate(matchIds, start=0):
    url = (f'https://americas.api.riotgames.com/tft/match/v1/matches/{match_position}?api_key={api_key}')
    response = requests.get(url)  

    if response.status_code == 200:
        data = response.json() 
        info = data.get("info", {}) 

        endOfGameResult = info["endOfGameResult"]
        gameCreation = info["gameCreation"] 
        game_datetime = info["game_datetime"] 
        game_length = info["game_length"] 
        mapId = info["mapId"] 
        season = info["tft_set_number"] 
        
        for player in info.get("participants", []):
            if player["riotIdGameName"] == name and player["riotIdTagline"] == tag:
                placement = player["placement"]
                damageCaused = player["total_damage_to_players"] 
                level = player["level"] 
                last_round = player["last_round"]
                time_eliminated = player["time_eliminated"]
                isWin = player["win"]  
                
                traits = [(trait["name"], trait["num_units"]) for trait in player['traits']]
                
                matchResume = {
                    "match_id": [match_position],
                    "set": [season],
                    "game_creation": [gameCreation],
                    "game_datetime": [game_datetime],
                    "end_of_game_result": [endOfGameResult],
                    "game_length": [game_length],
                    "level": [level],
                    "last_round": [last_round],
                    "time_eliminated": [time_eliminated],
                    "map_id": [mapId],
                    "puuid": [puuid],
                    "damage_caused": [damageCaused],
                    "placement": [placement],
                    "traits": [traits],
                    "is_win": [isWin]
                }
                
                df_matchResume = pd.DataFrame(matchResume)
                mathStatusFormation.append(df_matchResume)
                
                champs = [(unit['character_id'], unit['itemNames']) for unit in player['units']]
                
                championsInMatch = {
                    "matchId": [match_position],
                    "puuid": [puuid],
                    "champions": [champs]
                }
                
                df_champions = pd.DataFrame(championsInMatch)
                chapionsFormation.append(df_champions)
    else:
        print(f"Erro ao obter dados da partida: {response.status_code} - {response.text}")

mathStatus = pd.concat(mathStatusFormation, ignore_index=True)

mathStatus['game_creation'] = pd.to_datetime(mathStatus['game_creation'] / 1000, unit='s')
mathStatus['game_datetime'] = pd.to_datetime(mathStatus['game_datetime'] / 1000, unit='s')

mathStatus['traits'] = mathStatus['traits'].apply(json.dumps)

mathStatus['game_length'] = mathStatus['game_length'] / 1000

mathStatus['traits_used'] = len(traits)

chapionsToMatch = pd.concat(chapionsFormation, ignore_index=True)

#print(mathStatus.dtypes)

# postgresDB = pg_connection()
# postgresDB.insertOnMatchStatus(mathStatus)

filePath = 'schema_tft/matchStatus.xlsx'

if os.path.exists(filePath):
    newDF = []
    
    dfMStatus = pd.read_excel(filePath)
    
    playerLastGame =  dfMStatus[dfMStatus['puuid'] == puuid]['game_creation'].max()   # dfMStatus[dfMStatus['puuid'] == puuid]  também é entendido com data frame por isso posso acessar as colunas 
    newMatchRows = mathStatus[mathStatus['game_creation'] > playerLastGame]

    if newMatchRows.empty:
        print('0 matches to recover')
    else:
        print(f'{len(newMatchRows)} new matches found')

        newDF.append(dfMStatus)
        newDF.append(newMatchRows)

        dwConcatened = pd.concat([dfMStatus, newMatchRows], ignore_index = True)

        print('Rewriting file')

        dwConcatened.to_excel(filePath)

else:
    print('File not found, creating ...')
    mathStatus.to_excel('schema_tft/matchStatus.xlsx')