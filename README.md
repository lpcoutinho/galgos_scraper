# Galgos: scraper de Oddschecker
Raspando dados das corridas de galgos em https://www.oddschecker.com/greyhounds

Consulte os passos de construção em [steps.md](steps.md)


## Instale e execute

- Instale as bibliotecas necessárias
```shell
pip install -r requirements.txt
```
- [Instale o Crhome 114](https://www.edivaldobrito.com.br/en/how-to-install-google-chrome-on-ubuntu-and-derivatives/
)

- Crie o arquivo `.env` e adicione as credenciais do seu banco de dados. Utilize o exemplo `.env_example`

- O serviço `get_race_list.py` cria uma lista com as corridas do dia. Agende a tarefa de criar uma lista de corridas diariamente. Com `crontab`:
```shell
crontab -e
```
-Edite o arquivo para o tempo desejado. Sugestão, todo dia às 03:01h do servidor.

`5 3 * * * /root/app/get_race_list.sh >> /root/app/get_race_list_log.txt`   

Com o arquivo `race_list.csv` criado pelo serviço `get_race_list.py` estamos prontos para capturar os dados da próxima corrida
```shell
pyhton next_race.py
```

Para capturar os dados das próximas corridas em função do tempo
```shell
pyhton upcoming_races.py
```
Caso queira rodar os dois serviços [instale o Tmux](https://www.hostinger.com.br/tutoriais/como-usar-tmux-lista-de-comandos) e rode cada serviço em uma tela.

- Inicie uma nova sesão no Tmux
```shell
tmux
```

- Dentro da seesão inicie o serviço escolhido, como exemplo usaremos `next_race.py`
```shell
python3 next_race.py
```
- Utilize o atalho `ctrl+b+"` para criar uma nova tela.

- Passe para a nova tela com `ctrl+b+seta direcional para baixo` e inicie o outro serviço.
```shell
python3 upcoming_races.py
```

- Para sair da sessão Tmux sem fechar as aplicações utilize o atalho `ctrl+d`

- Para retornar a sessão utilize
```shell
tmux -a
```

## O Banco de dados para testes
Foi criada uma tabela no banco de dados PostgreSQL para garantir o armazenamento seguro das informações. Para isso, foi utilizado um Dockerfile para construir uma imagem contendo um banco de dados pré-configurado com o arquivo `init.sql`.

Para construir a imagem do Docker, execute o seguinte comando:

```shell
docker build -t galgos_db .
```

Para rodar o banco de dados:
```shell
docker run -d -p 5432:5432 --name galgos_db galgos_db
```
