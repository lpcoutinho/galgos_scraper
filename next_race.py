
from scraper import  get_race_list, get_next_race, get_data_races
from utils import scraper

import time

# URLs
# pattern = r"/greyhounds/[a-zA-Z-]+/\d{2}:\d{2}/winner"
top_2_finish = "top-2-finish"
top_3_finish = "top-3-finish"

# Query
# query = "INSERT INTO odds (odd, nome_pista, quando, trap, nome_galgo, mercado) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (nome_pista, quando, trap, nome_galgo, mercado) DO UPDATE SET odd = excluded.odd"

# Cria o objeto soup usando o scraper
soup = scraper()

data = []

# Obtém a lista de corridas do dia
race_list = get_race_list(soup)
print("\n Total de corridas hoje:", race_list.shape[0])

# Loop infinito para capturar continuamente as corridas
while True:
    try:
        # Obtém o link da próxima corrida
        next_race = get_next_race(race_list)
        
        # Obtém os dados da corrida no mercado winner
        df_winner = get_data_races(next_race)
        
        # Cria os links para os mercados "top 2 finish" e "top 3 finish"
        top_2_finish_nxr = next_race.replace("winner", top_2_finish)
        top_3_finish_nxr = next_race.replace("winner", top_3_finish)

        # Obtém os dados das corridas de "top 2 finish" e "top 3 finish"
        top_2_finish_nxr = get_data_races(top_2_finish_nxr)
        top_3_finish_nxr = get_data_races(top_3_finish_nxr)
        
        # Aguarda 30 segundos antes de capturar os dados novamente
        time.sleep(30)
    except:
        print("Erro ao tentar capturar a próxima corrida")
        print("Provavelmente elas terminaram...")
        break