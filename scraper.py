import os
import re
import time
from datetime import datetime, timedelta

import cloudscraper
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webdriver import By

from utils import establish_connection, london_time

from selenium.webdriver.chrome.options import Options

# Configura as opções do Chrome para executar em modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")

# URLs
url_base = "https://www.oddschecker.com/greyhounds"
pattern = r"/greyhounds/[a-zA-Z-]+/\d{2}:\d{2}/winner"
top_2_finish = "top-2-finish"
top_3_finish = "top-3-finish"

# Query
query = "INSERT INTO odds (odd, nome_pista, quando, trap, nome_galgo, mercado) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (nome_pista, quando, trap, nome_galgo, mercado) DO UPDATE SET odd = excluded.odd"

data = []

# Cria o scraper usando o CloudScraper
scraper = cloudscraper.create_scraper()
# print(scraper.get(url_base).content)

# Faz a requisição para obter o conteúdo da página
request = scraper.get(url_base)
request = request.text

# Cria um objeto Beautiful Soup a partir do conteúdo da página
soup = BeautifulSoup(request, "html.parser")
# print(soup.prettify())


# Constrói um dataframe com as corridas do dia
def get_race_list(soup):
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

    return race_list

currnt_time = datetime.now()
# Busca o link da próxima corrida no horário londrino
def get_next_race(df):
    # Filtra as corridas que ocorrerão após o horário londrino atual
    # currnt_time = datetime.now()
    # next_race = df[df["quando"] > london_time()].head(1)
    next_race = df[df["quando"] > currnt_time].head(1) # para testar no horário brasileiro
    
    # Obtém o link da próxima corrida
    next_race = next_race.iloc[0]["link"]
    
    # Imprime o link da próxima corrida para monitoramento
    print("\nMonitorando a próxima corrida:\n", next_race, "\n")

    return next_race


def get_upcoming_races(df, minutes):
    # Calcula o tempo limite (x minutos a partir da hora atual)
    time_limit = london_time() + timedelta(minutes=minutes)

    # Filtra as corridas cujo horário esteja dentro do intervalo
    # upcoming_races = df[(df["quando"] > london_time()) & (df["quando"] <= time_limit)]
    upcoming_races = df[(df["quando"] > currnt_time) & (df["quando"] <= time_limit)]
    
    # Obtém os links das corridas futuras como uma lista
    upcoming_races_links = upcoming_races["link"].tolist()

    # Imprime os links das corridas futuras para fins de verificação
    print("\n", upcoming_races_links, "\n")

    return upcoming_races_links


def get_data_races(race):
    # Extraindo dados da URL
    url_parts = race.split("/")

    onde = url_parts[4]
    quando = url_parts[5]
    mercado = url_parts[6]
    date = datetime.now().date()
    quando = f"{date} {quando}"

    try:
        # Fazendo uma requisição para obter o conteúdo da página da corrida
        request = scraper.get(race)
        request = request.text

        # Criando um objeto BeautifulSoup para analisar o conteúdo HTML da página
        soup = BeautifulSoup(request, "html.parser")

        # Se o HTML possuir o atributo ng-app, utilizar undetected_chromedriver 
        if soup.html.has_attr("ng-app") and soup.html["ng-app"] == "ocAngularApp":
            print("pega por lista <li>")
            
            # Inicializa o driver do Chrome usando as opções configuradas
            driver = uc.Chrome(options=chrome_options)
            driver.get(race)

            # Tira um print da tela
            driver.save_screenshot("screenshot.png")
            
            # Clique no popup (se existir)
            time.sleep(5)
            try:
                driver.find_element(
                    By.XPATH, "/html/body/div[2]/div/div/div/button[1]"
                ).click()
            except:
                pass
            
            # Obtém o conteúdo HTML da página após as interações no navegador
            html_content = driver.page_source

            # Cria um objeto BeautifulSoup para analisar o conteúdo HTML da página
            soup = BeautifulSoup(html_content, "html.parser")

            # # consulte o html
            # with open("race_list_list.html", "w") as file:
            #     file.write(soup.prettify())

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

                # data.append([trap, galgo, odd_dec, onde, quando, mercado])
                data.append(
                    [trap, galgo, odd_dec, odd_frac, data_fodds, onde, quando, mercado]
                )

                # Estabelece a conexão com o banco de dados
                conn = establish_connection()
                cur = conn.cursor()
                
                # Executa a consulta SQL para inserir os dados no banco de dados
                query = query
                data_sql = (odd_dec, onde, quando, trap, galgo, mercado)
                cur.execute(query, data_sql)
                conn.commit()
                
                cur.close()
                conn.close()
                
            # Encerra o driver do Chrome
            driver.quit()
        else:
            # Se o HTML não possuir o atributo ng-app pegue os dados apenas com cloudscraper e BeautifulSoup 
            print("\npega por div <div>\n")

            # Encontra os elementos da lista de cães usando a classe CSS 'diff-row evTabRow bc'
            dog_list = soup.find_all("tr", class_="diff-row evTabRow bc")

            data = []

            # Itera sobre os elementos da lista de cães
            for dog in dog_list:
                trap = dog.find("span", class_="trap").text
                galgo = dog.find("a", class_="popup selTxt").text
                odds = dog.find("td", class_="bc")
                odd_frac = odds["data-o"]
                odd_dec = odds["data-odig"]
                data_fodds = odds["data-fodds"]

                data.append(
                    [trap, galgo, odd_dec, odd_frac, data_fodds, onde, quando, mercado]
                )

                # Estabelece a conexão com o banco de dados
                conn = establish_connection()
                cur = conn.cursor()

                # Executa a consulta SQL para inserir os dados no banco de dados
                query = query
                data_sql = (odd_dec, onde, quando, trap, galgo, mercado)
                cur.execute(query, data_sql)
                conn.commit()

                cur.close()
                conn.close()

            # print(data)

        # Cria um DataFrame a partir dos dados coletados
        try:
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
                ],
            )

            # Salva o DataFrame em um arquivo CSV
            if not os.path.isfile("dados.csv"):
                df.to_csv("dados.csv", index=False)
            else:
                df_existing = pd.read_csv("dados.csv")
                df_updated = pd.concat([df_existing, df], ignore_index=True)
                df_updated.to_csv("dados.csv", index=False)

        except:
            print("Erro ao criar csv")

    except scraper.simpleException as e:
        print(e)

    print(df)
    return df

# Cria uma lista de corridas e exibe quantas temos hoje
# race_list = get_race_list(soup)
# print("\n Total de corridas hoje:", race_list.shape[0])

# while True:
#     try:
#         next_race = get_next_race(race_list)
#         df_winner = get_data_races(next_race)

#         top_2_finish_nxr = next_race.replace("winner", top_2_finish)
#         top_3_finish_nxr = next_race.replace("winner", top_3_finish)

#         top_2_finish_nxr = get_data_races(top_2_finish_nxr)
#         top_3_finish_nxr = get_data_races(top_3_finish_nxr)

#         time.sleep(30)

#     except:
#         print("Erro ao tentar capturar a próxima corrida")
#         print("Provavelmente elas terminaram...")
#         break
