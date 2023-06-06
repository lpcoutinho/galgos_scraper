import time

from scraper import get_data_races, get_next_race, get_race_list
from utils import scraper

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
        print('\nBuscando a próxima corrida..')
        # Obtém o link da próxima corrida
        next_race = get_next_race(race_list)

        print('Capturando dados do mercado Winner', next_race,'\n')
        # Obtém os dados da corrida no mercado winner
        df_winner = get_data_races(next_race)

        
        # Cria os links para os mercados "top 2 finish" e "top 3 finish"
        top_2_finish_nxr = next_race.replace("winner", top_2_finish)
        top_3_finish_nxr = next_race.replace("winner", top_3_finish)

        # Obtém os dados das corridas de "top 2 finish" e "top 3 finish"
        print('\nCapturando dados do mercado Top 2', top_2_finish_nxr,'\n')
        top_2_finish_nxr = get_data_races(top_2_finish_nxr)
        print('\nCapturando dados do mercado Top 3', top_3_finish_nxr,'\n')
        top_3_finish_nxr = get_data_races(top_3_finish_nxr)

        # Aguarda 30 segundos antes de capturar os dados novamente
        time.sleep(30)
    except:
        print("Erro ao tentar capturar a próxima corrida")
        print("Provavelmente elas terminaram...")
        break
