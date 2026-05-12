from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

# cria a conexão do banco de dados
db = create_engine("sqlite:///database/banco.db") # começa com 3 barras, se quiser criar uma pasta, é só digitar o nome da pasta/nome_do_arquivo

# cria a base do banco
Base = declarative_base()