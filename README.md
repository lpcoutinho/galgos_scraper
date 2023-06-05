# Galgos: scraper de Oddschecker
Raspando dados das corridas de galgos em https://www.oddschecker.com/greyhounds

Consulte os passos de construção em [steps.md](steps.md)


## Instale e execute

- Crie o arquivo `.env` e adicione as credenciais do seu banco de dados. Utilize o exemplo `.env_example`

- Instale as bibliotecas necessárias
```shell
pip install -r requirements.txt
```

Para capturar os dados da próxima corrida
```shell
pyhton next_race.py
```

Para capturar os dados das próximas corridas em função do tempo
```shell
pyhton upcoming_races.py
```

## O Banco de dados para testes
Foi criada uma tabela no banco de dados PostgreSQL para garantir o armazenamento seguro das informações. Para isso, foi utilizado um Dockerfile para construir uma imagem contendo um banco de dados pré-configurado com o arquivo `init.sql`.

Para construir a imagem do Docker, execute o seguinte comando:

```shell
docker build -t galgos_docker .
```

Para rodar o banco de dados:
```shell
docker run -d -p 5432:5432 --name galgos_db galgos_docker
```

## Sugestões

- Rodar os dois serviços utilizando tmux
- Realizar o scraper em threads