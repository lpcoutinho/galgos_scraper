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
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from utils import ler_trecho

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")
USERDB = os.getenv("USERDB")
PASSWORD = os.getenv("PASSWORD")

# import cloudscraper
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


def get_next_race():
    current_time = london_time()
    print("Horário londrino:", current_time)

    # Calcula o horário limite (atual + 2 horas)
    limite = current_time + timedelta(hours=2)
    print(limite)

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
            print("\nMonitorando a próxima corrida:\n", next_race_link, "\n")
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
        print("Fazendo uma requisição para obter o conteúdo da página da corrida...\n")
        scraper = cloudscraper.create_scraper()
        response = scraper.get(race)
        # print(response.text)
        # response_log(response)
        # response = response.text
    except exceptions.CloudflareChallengeError as e:
        print("Erro Cloudflare Challenge:", str(e))
        # proxy = (
        #     "http://76574a8de357e6663ca07da88a64532437ddf5f5:@proxy.zenrows.com:8001"
        # )
        proxy = "http://76574a8de357e6663ca07da88a64532437ddf5f5:antibot=true@proxy.zenrows.com:8001"
        proxies = {"http": proxy, "https": proxy}
        # response = requests.get(race, proxies=proxies, verify=False)
        response = requests.get(race, proxies=proxies)
        # response = response.text
        # response_log(response)
        ler_trecho()
    except exceptions.CloudflareCaptchaError as e:
        print("Erro Cloudflare Captcha:", str(e))
    # except exceptions.CloudflareConnectionError as e:
    #     print("Erro de conexão com o Cloudflare:", str(e))
    # except exceptions.HTTPError as e:
    #     print("Erro HTTP:", str(e))
    except Exception as e:
        print("Erro desconhecido pelo scraper:", str(e))

    try:
        print(
            "\nCriando um objeto BeautifulSoup para analisar o conteúdo HTML da página...\n"
        )
        # print(response.text)

        # soup = BeautifulSoup(response, "html.parser")
        # soup = BeautifulSoup(response, "html5lib")
        soup = BeautifulSoup(response.text, "lxml")
        # soup = BeautifulSoup(response.text, "lxml-xml")
        # print('soup criado')

        # consulte o html
        # with open("race_list_list.html", "w") as file:
        #     file.write(soup.prettify())
    except Exception as e:
        print("Erro desconhecido pelo BeautifulSoup:", str(e))

    try:
        # Se o HTML possuir o atributo ng-app, utilizar undetected_chromedriver
        if soup.html.has_attr("ng-app") and soup.html["ng-app"] == "ocAngularApp":
            print("Pega informações por <li>")

            print("Acessando o site...")
            try:
                # Configura as opções do Chrome para executar em modo headless
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                # Inicializa o driver do Chrome usando as opções configuradas
                driver = uc.Chrome(options=chrome_options)
                # driver = uc.Chrome()
                driver.get(race)

                time.sleep(15)
                # Tira um print da tela
                driver.save_screenshot("screenshot.png")

                print("Aguarde...")
                # Clique no popup (se existir)

                try:
                    # Esperar até que um elemento seja visível
                    element = WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located(
                            (By.XPATH, "/html/body/div[2]/div/div/div/button[1]")
                        )
                    )

                    # Realizar ações no elemento após a espera
                    element.click()
                    # driver.find_element(
                    #     By.XPATH, "/html/body/div[2]/div/div/div/button[1]"
                    # ).click()
                    print("Popup selecionado")
                except Exception as e:
                    print("Popup não encontrado")
                    print(e)
                    time.sleep(2)
                    # pass

                # Obtém o conteúdo HTML da página após as interações no navegador
                html_content = driver.page_source

                # Cria um objeto BeautifulSoup para analisar o conteúdo HTML da página
                soup = BeautifulSoup(html_content, "html.parser")

                # # consulte o html
                # with open("race_list_list.html", "w") as file:
                #     file.write(soup.prettify())

                print("Procurando odds")
                # Encontrar o tbody desejado pelo id
                tbody = soup.find("tbody", id="t1")

                data = []

                # Iterar sobre todos os elementos tr dentro do tbody
                for tr in tbody.find_all("tr", class_="diff-row evTabRow bc"):
                    trap = tr.find("td", class_="trap-cell").text
                    galgo = tr.find("td", class_="sel nm basket-active").text
                    odds = tr.find("td", class_="bc")
                    odd_frac = odds["data-o"]
                    odd_dec = odds["data-odig"]
                    data_fodds = odds["data-fodds"]
                    time_scrape = datetime.now()
                    # data.append([trap, galgo, odd_dec, onde, quando, mercado])
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
                        print(
                            f"Inserindo informações no banco de dados trap: {trap}, galgo: {galgo}, odd_dec: {odd_dec}, onde: {onde}, quando:{quando}, mercado:{mercado}"
                        )
                        # Estabelece a conexão com o banco de dados
                        conn = establish_connection()
                        cur = conn.cursor()

                        # # Executa a consulta SQL para inserir os dados no banco de dados
                        # query = "INSERT INTO odds (odd, nome_pista, quando, trap, nome_galgo, mercado) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (nome_pista, quando, trap, nome_galgo, mercado) DO UPDATE SET odd = excluded.odd"
                        query = """
                            INSERT INTO odds (odd, nome_pista, quando, trap, nome_galgo, mercado)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (nome_pista, quando, trap, nome_galgo, mercado)
                            DO UPDATE SET odd = EXCLUDED.odd;
                        """
                        # print(query)
                        data_sql = (odd_dec, onde, quando, trap, galgo, mercado)
                        cur.execute(query, data_sql)
                        conn.commit()

                        cur.close()
                        conn.close()
                        print("Banco de dados atualizado.\n")
                    except Exception as e:
                        print(
                            "Erro ao salvar informações no banco de dados:",
                            str(e),
                            "\n",
                        )

                # Encerra o driver do Chrome
                driver.quit()
                print("Encerrando o driver")

            except SessionNotCreatedException as e:
                print("Erro na criação da sessão do WebDriver:", str(e))
            except WebDriverException as e:
                print("Erro genérico do WebDriver:", str(e))
            except Exception as e:
                print("Erro desconhecido, provável bloqueio do antibot:", str(e))
        else:
            # Se o HTML não possuir o atributo ng-app pegue os dados apenas com cloudscraper e BeautifulSoup
            print("\nPegando informações por div <div>\n")

            # Encontra os elementos da lista de cães usando a classe CSS 'diff-row evTabRow bc'
            dog_list = soup.find_all("tr", class_="diff-row evTabRow bc")

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
                    print(
                        f"Inserindo informações no banco de dados trap: {trap}, galgo: {galgo}, odd_dec: {odd_dec}, onde: {onde}, quando:{quando}, mercado:{mercado}"
                    )
                    # Estabelece a conexão com o banco de dados
                    conn = establish_connection()
                    cur = conn.cursor()

                    # # Executa a consulta SQL para inserir os dados no banco de dados
                    query = """
                            INSERT INTO odds (odd, nome_pista, quando, trap, nome_galgo, mercado)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (nome_pista, quando, trap, nome_galgo, mercado)
                            DO UPDATE SET odd = EXCLUDED.odd;
                    """
                    # print(query)

                    data_sql = (odd_dec, onde, quando, trap, galgo, mercado)
                    cur.execute(query, data_sql)
                    conn.commit()

                    cur.close()
                    conn.close()
                    print("Banco de dados atualizado.\n")
                except Exception as e:
                    print("Erro ao salvar informações no banco de dados:", str(e), "\n")

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
                "Arquivo não encontrado, criando 'dados.csv"
                df.to_csv("dados.csv", index=False)
            else:
                df_existing = pd.read_csv("dados.csv")
                df_updated = pd.concat([df_existing, df], ignore_index=True)
                df_updated.to_csv("dados.csv", index=False)

        except Exception as e:
            print("Erro ao criar csv")
            print(e)

    except scraper.simpleException as e:
        print(e)

    print(df)
    return df


while True:
    try:
        next_race = get_next_race()
        print("next_race", next_race)

        print("Capturando dados do mercado Winner", next_race, "\n")
        # Obtém os dados da corrida no mercado winner
        df_winner = get_data_races(next_race)

        # Cria os links para os mercados "top 2 finish" e "top 3 finish"
        top_2_finish_nxr = next_race.replace("winner", top_2_finish)
        top_3_finish_nxr = next_race.replace("winner", top_3_finish)

        # Obtém os dados das corridas de "top 2 finish" e "top 3 finish"
        print("\nCapturando dados do mercado Top 2", top_2_finish_nxr, "\n")
        top_2_finish_nxr = get_data_races(top_2_finish_nxr)

        print("\nCapturando dados do mercado Top 3", top_3_finish_nxr, "\n")
        top_3_finish_nxr = get_data_races(top_3_finish_nxr)
        # Aguarda 30 segundos antes de capturar os dados novamente
        time.sleep(30)
    except:
        break
