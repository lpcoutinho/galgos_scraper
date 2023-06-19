from datetime import datetime, timedelta

import pandas as pd
from dateutil import tz


def london_time():
    time_zone_uk = tz.gettz("Europe/London")

    london_time = datetime.now(time_zone_uk)
    london_time = london_time.replace(tzinfo=None)
    print(time_zone_uk)
    return london_time


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


import datetime


def response_log(response):
    # Obtém a hora atual
    hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define o nome do arquivo
    nome_arquivo = "response.txt"

    # Abre o arquivo no modo de escrita e adiciona o conteúdo
    with open(nome_arquivo, "a") as arquivo:
        # Escreve a hora atual
        arquivo.write(hora_atual + "\n")

        # Escreve o conteúdo
        arquivo.write(response.text + "\n")
