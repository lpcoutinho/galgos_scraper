import os
import time
from datetime import datetime, timedelta

import cloudscraper
import pandas as pd
import psycopg2
import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from cloudscraper import exceptions
from dateutil import tz
from dotenv import load_dotenv
from loguru import logger
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from zenrows import ZenRowsClient

# Logger configs
logger.add("next_chrome.log", rotation="500 MB", compression="zip", enqueue=True)

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")
USERDB = os.getenv("USERDB")
PASSWORD = os.getenv("PASSWORD")

# URLs
top_2_finish = "top-2-finish"
top_3_finish = "top-3-finish"


# Obtém o horário londrino atual
def london_time():
    time_zone_uk = tz.gettz("Europe/London")
    london_time = datetime.now(time_zone_uk)
    london_time = london_time.replace(tzinfo=None)
    return london_time


def establish_connection():
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        database=DATABASE,
        user=USERDB,
        password=PASSWORD,
    )
    return conn


def ler_trecho():
    arquivo_contador = "contador_zen_rows.txt"

    # Abrir o arquivo de texto em modo leitura
    with open(arquivo_contador, "r") as arquivo:
        # Ler o valor atual do contador
        contador = int(arquivo.read())

    # Incrementar o contador
    contador += 1

    # Abrir o arquivo de texto em modo escrita
    with open(arquivo_contador, "w") as arquivo:
        # Escrever o novo valor do contador
        arquivo.write(str(contador))

    # Retornar o contador
    return contador


def get_next_race():
    current_time = london_time()
    logger.info(f"Horário londrino: {current_time}")

    # Calcula o horário limite (atual + 2 horas)
    limite = current_time + timedelta(hours=2)

    df = pd.read_csv("race_list.csv")

    df["quando"] = pd.to_datetime(
        df["quando"]
    )  # Converte a coluna "quando" para o formato de data e hora

    df = df[df["quando"] > current_time]  # Remove as corridas que já ocorreram

    next_races = df[
        df["quando"] <= limite
    ]  # Filtra as corridas que ocorrerão dentro das próximas duas horas
    # print(next_races)

    if not next_races.empty:
        next_races = next_races.sort_values("quando")  # Ordena as corridas por horário
        next_race_link = next_races.iloc[0]["link"]  # Obtém o link da próxima corrida

        tempo_para_inicio = next_races.iloc[0]["quando"] - current_time
        if (
            tempo_para_inicio.total_seconds() <= 7200
        ):  # Se a corrida ocorre nas próximas duas horas monitore
            logger.info(f"Monitorando a próxima corrida: {next_race_link}")
            return next_race_link
    return None


def get_data_races(race):
    print("Extraindo dados da URL...")
    url_parts = race.split("/")

    onde = url_parts[4]
    quando = url_parts[5]
    mercado = url_parts[6]
    date = datetime.now().date()
    quando = f"{date} {quando}"

    try:
        logger.info(
            f"Fazendo uma requisição para obter o conteúdo da página da corrida. {race}"
        )
        scraper = cloudscraper.create_scraper()
        response = scraper.get(race)

        soup = BeautifulSoup(response.text, "lxml")

        # consulte o html
        with open("next_cloudscraper.html", "w") as file:
            file.write(soup.prettify())

    except exceptions.CloudflareChallengeError as e:
        logger.error(f"Erro Cloudflare Challenge: {str(e)}")

        try:
            logger.info("Cloudscraper não funcionou, tentando ZenrowsClient")
            client = ZenRowsClient("06150d7907d520dc9f432f52ec80e77606a9f8cd")
            params = {"antibot": "true"}
            # params = {"js_render":"true","antibot":"true","premium_proxy":"true"}

            ler_trecho()

            response = client.get(race, params=params)
            # response = client.get(race)

            soup = BeautifulSoup(response.text, "lxml")

            # # consulte o html
            # with open("next_zen.html", "w") as file:
            #     file.write(soup.prettify())

        except Exception as e:
            print(str(e))
            logger.error(str(e))

    try:
        if "www.zenrows" in soup.find("p").text:
            logger.warning(f"Zenrows não funcionou: {soup.find('p').text}")

        # Se o HTML possuir o atributo ng-app, utilizar undetected_chromedriver
        elif soup.html.has_attr("ng-app") and soup.html["ng-app"] == "ocAngularApp":
            logger.info("Pega informações por <li>")
            logger.warning("Passe")
            pass

        else:
            # Se o HTML não possuir o atributo ng-app pegue os dados apenas com cloudscraper e BeautifulSoup
            logger.info("Pegando informações por div <div>")

            # Encontra os elementos da lista de cães usando a classe CSS 'diff-row evTabRow bc'
            dog_list = soup.find_all("tr", class_="diff-row evTabRow bc")
            # print(dog_list)
            if dog_list == []:
                logger.warning("Mercado não está aberto aguarde 30s")
                time.sleep(30)
                pass

            else:
                data = []
                print("Dados encontrados")
                # Itera sobre os elementos da lista de cães
                for dog in dog_list:
                    trap = dog.find("span", class_="trap").text
                    galgo = dog.find("a", class_="popup selTxt").text
                    odds = dog.find("td", class_="bc")
                    odd_frac = odds["data-o"]
                    odd_dec = odds["data-odig"]
                    data_fodds = odds["data-fodds"]
                    time_scrape = datetime.now()

                    print(trap)
                    print(galgo)
                    print(odd_dec)
                    print(data_fodds)
                    print(time_scrape)

                    data.append(
                        [
                            trap,
                            galgo,
                            odd_dec,
                            odd_frac,
                            data_fodds,
                            onde,
                            quando,
                            mercado,
                            time_scrape,
                        ]
                    )
                    try:
                        logger.info(
                            f"Inserindo informações no banco de dados trap: {trap}, galgo: {galgo}, odd_dec: {odd_dec}, onde: {onde}, quando:{quando}, mercado:{mercado}"
                        )

                        # Estabelece a conexão com o banco de dados
                        conn = establish_connection()
                        cur = conn.cursor()

                        # # Executa a consulta SQL para inserir os dados no banco de dados
                        query = """
                                INSERT INTO odds (odd, nome_pista, quando, trap, nome_galgo, mercado, start_odd)
                                VALUES (%s, %s, %s, %s, %s, %s,%s)
                                ON CONFLICT (nome_pista, quando, trap, nome_galgo, mercado)
                                DO UPDATE SET odd = EXCLUDED.odd;
                        """
                        # print(query)

                        data_sql = (
                            odd_dec,
                            onde,
                            quando,
                            trap,
                            galgo,
                            mercado,
                            odd_dec,
                        )
                        cur.execute(query, data_sql)
                        conn.commit()

                        cur.close()
                        conn.close()
                        print("Banco de dados atualizado.\n")
                        logger.info("Banco de dados atualizado.")
                    except Exception as e:
                        logger.error(
                            f"Erro ao salvar informações no banco de dados: {str(e)}"
                        )

                # Cria um DataFrame a partir dos dados coletados
                try:
                    # print(data)
                    df = pd.DataFrame(
                        data,
                        columns=[
                            "trap",
                            "galgo",
                            "odd_dec",
                            "odd_frac",
                            "data_fodds",
                            "onde",
                            "quando",
                            "mercado",
                            "time_scrape",
                        ],
                    )

                    # Salva o DataFrame em um arquivo CSV
                    if not os.path.isfile("dados.csv"):
                        logger.info("Arquivo não encontrado, criando 'dados.csv")
                        df.to_csv("dados.csv", index=False)
                    else:
                        df_existing = pd.read_csv("dados.csv")
                        df_updated = pd.concat([df_existing, df], ignore_index=True)
                        df_updated.to_csv("dados.csv", index=False)

                    print(df)
                    return df
                except Exception as e:
                    logger.error(f"Erro ao criar csv {str(e)}")

    except scraper.simpleException as e:
        logger.error(str(e))

    # print(df)
    # return df


while True:
    try:
        start_time = time.time()
        next_race = get_next_race()
        # print("next_race", next_race)

        logger.info(f"Capturando dados do mercado Winner {next_race}")
        # Obtém os dados da corrida no mercado winner
        df_winner = get_data_races(next_race)

        # Cria os links para os mercados "top 2 finish" e "top 3 finish"
        top_2_finish_nxr = next_race.replace("winner", top_2_finish)
        top_3_finish_nxr = next_race.replace("winner", top_3_finish)

        # Obtém os dados das corridas de "top 2 finish" e "top 3 finish"
        logger.info(f"Capturando dados do mercado Top 2 {top_2_finish_nxr}")
        top_2_finish_nxr = get_data_races(top_2_finish_nxr)

        logger.info(f"Capturando dados do mercado Top 3 {top_3_finish_nxr}")
        top_3_finish_nxr = get_data_races(top_3_finish_nxr)
        # Aguarda 30 segundos antes de capturar os dados novamente
        duration = time.time() - start_time
        wait_time = 30 - duration
        logger.info(f"spended {duration} seconds. waiting {wait_time} seconds")
        if wait_time > 0:
            time.sleep(wait_time)
    except:
        logger.warning("Sem corridas, esperando 30 minutos")
        time.sleep(1800)
        continue
