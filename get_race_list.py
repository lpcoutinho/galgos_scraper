import re
from datetime import datetime

import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup

from utils import london_time

# URLs
url_base = "https://www.oddschecker.com/greyhounds"
pattern = r"/greyhounds/[a-zA-Z-]+/\d{2}:\d{2}/winner"
top_2_finish = "top-2-finish"
top_3_finish = "top-3-finish"

# Cria o scraper usando o CloudScraper
scraper = cloudscraper.create_scraper()


# # # consulte o html
# with open("race_list_list.html", "w") as file:
#     file.write(soup.prettify())


# Constrói um dataframe com as corridas do dia
# Até o momento não o scraper não quebra neste ponto - 06/12/2023
def get_race_list():
    data = []

    # Faz a requisição para obter o conteúdo da página
    request = scraper.get(url_base)
    request = request.text

    # Cria um objeto Beautiful Soup a partir do conteúdo da página
    soup = BeautifulSoup(request, "html.parser")
    # print(soup.prettify())

    # Verificar se a tag 'html' contém o atributo 'ng-app="ocAngularApp"'
    if soup.html.has_attr("ng-app") and soup.html["ng-app"] == "ocAngularApp":
        # print("O atributo ng-app='ocAngularApp' existe.")
        # Encontrar todas as tags 'li' que possuem a classe 'group accordian-parent beta-body' e o atributo 'data-day'
        races = soup.find_all(
            "li", class_="group accordian-parent beta-body", attrs={"data-day": True}
        )

        for race in races:
            # Encontrar todas as tags 'a' dentro da tag 'li'
            races = race.find_all("a")
            for link in races:
                # Obter o atributo 'href' do link
                link = link.get("href")
                # Verificar se o link corresponde ao padrão definido
                if re.match(pattern, link):
                    # Formatar o link completo adicionando o prefixo 'https://www.oddschecker.com'
                    link = "https://www.oddschecker.com" + link
                    # Adicionar o link à lista de dados
                    data.append(link)

    else:
        # print("O atributo ng-app='ocAngularApp' não existe.\n")
        # Função auxiliar para encontrar o contêiner das corrida
        def find_race_meets_container(tag):
            return (
                tag.name == "div"
                and tag.has_attr("class")
                and "race-meets-container" in tag["class"]
            )

        # Encontra o contêiner das corridas do Reino Unido e Irlanda
        uk_container = soup.find(find_race_meets_container)

        # Encontra todas as tags 'div' com a classe 'race-details' dentro do contêiner
        races = uk_container.find_all("div", class_="race-details")

        for race in races:
            # Encontra todas as tags 'a' dentro da tag 'div'
            races = race.find_all("a")
            for link in races:
                # Obtém o atributo 'href' do link
                link = link.get("href")
                # Verifica se o link corresponde ao padrão definido
                if re.match(pattern, link):
                    # Formata o link completo adicionando o prefixo 'https://www.oddschecker.com'
                    link = "https://www.oddschecker.com" + link
                    # Adiciona o link à lista de dados
                    data.append(link)

    # Cria um DataFrame com os links das corridas
    df = pd.DataFrame(data, columns=["link"])

    # Extrai o nome do local da corrida a partir do link
    df["lugar"] = df["link"].apply(
        lambda link: re.search(r"/greyhounds/([^/]+)/\d{2}:\d{2}/", link).group(1)
    )

    # Extrai a data e hora da corrida a partir do link
    df["quando"] = df["link"].apply(
        lambda link: re.search(r"/\d{2}:\d{2}/", link).group().strip("/")
    )

    # Converte a coluna "quando" para o formato de data e hora
    df["quando"] = pd.to_datetime(df["quando"])

    # Extrai o tipo de mercado da corrida a partir do link
    df["mercado"] = df["link"].apply(
        lambda link: re.search(r"/winner", link).group().strip("/")
    )

    # Ordena o DataFrame com base na coluna "quando"
    race_list = df.sort_values("quando")
    race_list.to_csv("race_list.csv", index=False)
    print(
        "\n         Lista de corridas criada.\n\nHorário do servidor:",
        datetime.now(),
        "\nHorário Londrino:   ",
        london_time(),
        "\n",
    )
    print(race_list)
    return race_list


get_race_list()
