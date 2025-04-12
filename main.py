import requests  # Importa a biblioteca requests para fazer requisições HTTP
import pandas as pd  # Importa a biblioteca pandas para manipulação de dados
import json
from auth import user_authentication  # Importa a função de autenticação do usuário
from matchs import matchLists  # Importa a função que obtém a lista de partidas
from pg_connection import pg_connection

# Define o nome do jogador e a tag
name = 'GBA'  # Nome do jogador (pode ser substituído por entrada do usuário)
tag = 'TFT'  # Tag do jogador (pode ser substituído por entrada do usuário)
api_key = 'RGAPI-6df05484-21e1-4c16-980a-489b837bff12'  # Chave da API para acessar os dados da Riot Games

# Autentica o usuário e obtém seu PUUID
user_auth = user_authentication(name, tag, api_key)
puuid = user_auth.get_puuid()

# Obtém o número de partidas a serem recuperadas a partir da entrada do usuário
matchNumer = int(input('Number of Matchs to recover: '))
user_matchs = matchLists(puuid, matchNumer, api_key)
matchIds = user_matchs.get_matchLists()

# Cria um dicionário com informações do jogador
df_playerInformation = pd.DataFrame(
    {
    "puuid": [puuid],
    "riotIdGameName": [name],
    "riotIdTagline": [tag]
    }
)

# Listas para armazenar os dados das partidas e campeões
mathStatusFormation = []
chapionsFormation = []

# Itera sobre cada partida encontrada
for i, match_position in enumerate(matchIds, start=0):
    url = (f'https://americas.api.riotgames.com/tft/match/v1/matches/{match_position}?api_key={api_key}')
    response = requests.get(url)  # Faz uma requisição para obter os dados da partida

    if response.status_code == 200:  # Verifica se a requisição foi bem-sucedida
        data = response.json()  # Converte a resposta JSON em um dicionário Python
        info = data.get("info", {})  # Obtém as informações da partida

        # Obtém informações gerais da partida
        endOfGameResult = info["endOfGameResult"]
        gameCreation = info["gameCreation"]  # Timestamp da criação da partida
        game_datetime = info["game_datetime"]  # Timestamp da data e hora do jogo
        game_length = info["game_length"]  # Duração do jogo
        mapId = info["mapId"]  # ID do mapa
        season = info["tft_set_number"]  # Número da temporada do TFT
        
        # Itera sobre os participantes da partida
        for player in info.get("participants", []):
            if player["riotIdGameName"] == name and player["riotIdTagline"] == tag:
                placement = player["placement"]  # Posição final do jogador
                damageCaused = player["total_damage_to_players"]  # Dano total causado
                level = player["level"]  # Nível do jogador
                last_round = player["last_round"]  # Última rodada do jogador
                time_eliminated = player["time_eliminated"]  # Tempo até ser eliminado
                isWin = player["win"]  # Se o jogador venceu ou não
                
                # Obtém os traits utilizados pelo jogador
                traits = [(trait["name"], trait["num_units"]) for trait in player['traits']]
                
                # Cria um dicionário com os dados resumidos da partida
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
                
                # Converte os dados em um DataFrame e adiciona à lista
                df_matchResume = pd.DataFrame(matchResume)
                mathStatusFormation.append(df_matchResume)
                
                # Obtém os campeões usados pelo jogador na partida
                champs = [(unit['character_id'], unit['itemNames']) for unit in player['units']]
                
                # Cria um dicionário com os campeões usados
                championsInMatch = {
                    "matchId": [match_position],
                    "puuid": [puuid],
                    "champions": [champs]
                }
                
                # Converte os dados em um DataFrame e adiciona à lista
                df_champions = pd.DataFrame(championsInMatch)
                chapionsFormation.append(df_champions)
    else:
        print(f"Erro ao obter dados da partida: {response.status_code} - {response.text}")

# Concatena os DataFrames das partidas em um único DataFrame
mathStatus = pd.concat(mathStatusFormation, ignore_index=True)

# Converte os timestamps de milissegundos para datetime
mathStatus['game_creation'] = pd.to_datetime(mathStatus['game_creation'] / 1000, unit='s')
mathStatus['game_datetime'] = pd.to_datetime(mathStatus['game_datetime'] / 1000, unit='s')

# Converte o campos traits para string json, para ser aceito no postgres
mathStatus['traits'] = mathStatus['traits'].apply(json.dumps)

# Cria nova coluna convertida e dropa a antiga
mathStatus['game_length'] = mathStatus['game_length'] / 1000
#mathStatus.drop('game_length', axis='columns')

# Adiciona uma nova coluna com a quantidade de traços usados
mathStatus['traits_used'] = len(traits)

# Concatena os DataFrames dos campeões usados em cada partida
chapionsToMatch = pd.concat(chapionsFormation, ignore_index=True)

#print(mathStatus.dtypes)

postgresDB = pg_connection()
postgresDB.insertOnMatchStatus(mathStatus)
