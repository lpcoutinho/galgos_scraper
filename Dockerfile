# Use a imagem base do PostgreSQL
FROM postgres:latest

# Defina as variáveis de ambiente para o PostgreSQL
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres
ENV POSTGRES_DB galgos

# Copie um script SQL para ser executado durante a inicialização do banco de dados
COPY init.sql /docker-entrypoint-initdb.d/

# Defina o volume para armazenar os dados do banco de dados
VOLUME ./data

# Exponha a porta padrão do PostgreSQL
EXPOSE 5432
