# O problema

Eu, como desenvolvedor, preciso acessar o site https://www.oddschecker.com/greyhounds e extrair dados das corridas de galgos no Reino Unido e Irlanda para cada um dos três mercados: vencedor, segundo colocado e terceiro colocado. Devo pegar odds apenas da plataforma Bet32 e armazenar os valores capturados em um banco de dados PostgreSQL.

### Info
- Caso a corrida ainda não tenha começado nos campos de odds será exibido o valor SP;
- As odds começam a ser exibidas em aproximadamente 2h antes do início de cada corrida;
- Odds para os mercados de segundo e terceiro colocados ficam disponíveis até o fim da corrida;

# A construção

## Libs

- https://pypi.org/project/cloudscraper/
- https://www.selenium.dev/
- https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- https://github.com/ultrafunkamsterdam/undetected-chromedriver
- https://pandas.pydata.org/
- https://pypi.org/project/psycopg2-binary/

## Capturando dados de corridas
Ao tentar acessar [o endereço que exibe as corridas do dia](https://www.oddschecker.com/greyhounds) nos deparamos com duas estruturas de HTML diferentes: uma em formato de lista e outra em formato de tabela. Para capturar os dados das corridas, foi necessário adotar duas abordagens distintas.

Em ambos os modelos de HTML, utilizamos a biblioteca BeautifulSoup para extrair as informações. No entanto, a diferença crucial está na necessidade de simular um navegador para capturar os dados exibidos em forma de lista. Isso se deve ao fato de que o acesso direto ao endereço onde as informações estão hospedadas é bloqueado pelo antibot CloudFlare.

### Pulando o CloudFlare e acessando a página de corridas
Para contornar a segurança do CloudFlare e acessar as informações, utilizamos as bibliotecas cloudscraper, que envia uma requisição ao endereço informado e recebe o HTML como resposta. 

No entanto, nos casos em que foi necessário simular um navegador para interagir com a página, utilizamos a biblioteca undetected-chromedriver. Essa biblioteca permite automatizar a interação com o navegador Chrome de forma não detectável, garantindo que as ações sejam executadas sem acionar mecanismos de detecção de bots.

### `get_next_race`
Inicialmente foi criada função `get_next_race` que acessa [o endereço que exibe as corridas do dia](https://www.oddschecker.com/greyhounds) e construir um dataframe com a lista das corridas e seus respectivos links.

Além de converter para o horário londrino, foi preciso transformar os dados de horário para que exibam também o dia e posteriormente serem salvos sem erros no banco de dados. 

Neste ponto o script exibe um erro de formatação que não comprometirá seu desenvolvimento. Isso acontece devido ao formato em que as horas são exibidas no site. '08:35', '11:48', etc.

Após obter os dados das corridas e seus links, foram criados dois serviços, `next_race.py` e `upcoming_races.py`. Falaremos deles a seguir.

### `next_race.py`
A ferramenta `next_race.py` é responsável por monitorar continuamente a próxima corrida. Ela utiliza o dataframe criado com a função `get_next_race` para obter o link da próxima corrida e acessa a página correspondente para extrair os dados relevantes dessa corrida.

Após finalizar o horário da corrida atual, a ferramenta avança para o próximo horário disponível e repete o processo até que todas as corridas tenham ocorrido. Dessa forma, ela mantém o monitoramento contínuo das corridas, garantindo que os dados sejam capturados de forma atualizada.

### `upcoming_races.py`
A ferramenta `upcoming_races.py` segue uma abordagem semelhante à anterior. Ela cria uma lista de corridas com base em um intervalo de tempo em minutos e itera sobre essa lista para capturar os dados de cada corrida até que todas as corridas tenham ocorrido.

Essa ferramenta oferece a flexibilidade de definir até qual ponto no tempo o serviço deve monitorar as corridas. Por padrão, esse limite é definido em 60 minutos, mas pode ser facilmente alterado de acordo com as necessidades específicas. Dessa forma, é possível ajustar o alcance de monitoramento conforme desejado.

### Salvando no banco de dados
Dentro das ferramentas `next_race.py` e `upcoming_races.py` estão os métodos que salvam as informações capturadas em um banco de dados PostgreSQL.
