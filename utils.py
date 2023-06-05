import os
from datetime import datetime, timedelta

import cloudscraper
import psycopg2
from bs4 import BeautifulSoup
from dateutil import tz
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Acesse as variáveis de ambiente carregadas
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")

url_base = "https://www.oddschecker.com/greyhounds"


def scraper():
    # Cria o scraper
    scraper = cloudscraper.create_scraper()

    # Busca as corridas da página
    request = scraper.get(url_base)
    request = request.text
    # request

    soup = BeautifulSoup(request, "html.parser")
    # print(soup.prettify())
    return soup


# Pega o horário londrino
def london_time():
    time_zone_uk = tz.gettz("Europe/London")

    london_time = datetime.now(time_zone_uk)
    london_time = london_time.replace(tzinfo=None)

    return london_time


# print(london_time())

# Cria conexão com banco de dados
# def establish_connection():
#     conn = psycopg2.connect(
#         host=HOST,
#         port=PORT,
#         database=DATABASE,
#         user=USER,
#         password=PASSWORD,
#     )
#     return conn


def establish_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="galgos",
        user="postgres",
        password="postgres",
    )
    return conn
