# back-voluntariado-extensao
<p>Este é o back-end que estou estruturando para o nosso projeto de voluntários</p>
<br>
    <h1>Instalação</h1>
<br>
<div style="display: flex; align-items: center; gap: 10px">
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" style="margin-bottom: 10px" width=30>Após fazer a clonagem do repositório no computador, segue os passos abaixo:
</div>
<div style="display: flex; align-items: center; gap: 10px">
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" style="margin-bottom: 10px" width=30>Criar um arquivo na pasta raiz do projeto (back-voluntariado-extensao) chamado .env
</div>
<div style="display: flex; align-items: center; gap: 10px">
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" style="margin-bottom: 10px" width=30>Nesse arquivo você pode copiar as duas linhas abaixo
</div>

```env
SECRET_KEY=pGiggPz2p8xndOWQnTBY6fN3G3asyUa4
ALGORITHM=HS256
```
<div style="display: flex; align-items: center; gap: 10px">
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" style="margin-bottom: 10px" width=30> Dentro da pasta "notes" você pode abrir o arquivo dependencias.txt
</div>
<div style="display: flex; align-items: center; gap: 10px; justify-content: center; text-align: center;">
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" style="margin-bottom: 10px" width=30>Após isso você vai copiar o conteúdo no arquivo, abrir um terminal na raiz da pasta do projeto e mandar esse comando (precisa ter o Python instalado na máquina)
</div>
<div style="display: flex; align-items: center; gap: 10px">
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30>Para que não tiver o Pyhton, segue o link
</div>
<div style="display: flex; align-items: center; gap: 10px">
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30><a href="https://www.python.org/ftp/python/3.14.5/python-3.14.5-arm64.exe">Instalador</a>
</div>

<br>
<img src="https://preview.redd.it/trying-to-find-the-original-artist-behind-these-pixel-art-v0-h7mzbi1myiie1.gif?width=617&auto=webp&s=ec0a87a19a6bdbded3ec493aff2d987ce147ce07" width=100>
<h1>Configuração do banco</h1>
<br>

<p>Ao terminar a configuração anterior, bora para a criação do banco (você só executa 1 vez)</p>
<ul>
    <li>Com o terminal ainda aberto na pasta do projeto, você vai rodar a linha de comando:</li>
</ul>

```shell
alembic init alembic
```

<p>Dessa forma, dois itens serão criados: Um arquivo chamado "Alembic.ini" e uma pasta chamada "alembic"</p>

<div style="display: flex; align-items: center; gap: 10px;">
<img src="https://media.tenor.com/3YHLRFmS-SYAAAAj/minecraft.gif" width=70>
<h2>Configuração arquivo alembic.ini</h2>
</div>
<br>
<p>Dentro do arquivo "alembic.init" você vai editar a linha 89 dele, que é para estar escrito o seguinte:</p>

```python
sqlalchemy.url = driver://user:pass@localhost/dbname
```

<p>E você vai mudar para:</p>

```python
sqlalchemy.url = sqlite:///database/banco.db
```

<div style="display: flex; align-items: center; gap: 10px;">
<img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=70>
<h2>Configuração arquivo env.py</h2>
</div>

<p>Agora dentro da pasta "alembic" você vai abrir o arquivo "env.py" e logo abaixo da linha 6 onde está escrito</p>

```python
from alembic import context
```

<p>Você pode quebrar 2 linhas e digitar o código abaixo:</p>

```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
```
<p>Depois um pouco abaixo do seu código, você vai procurar onde está escrito:</p>

```python
target_metadata = None
```
<p>Acima dessa linha, você vai adicionar uma importação, digitando o seguinte:</p>

```python
from models.usuario import Base
```
<p>E no target_metadata (na linha de baixo) você vai substituir o "None" por "Base.metadata", com o código ficando da seguinte maneira:</p>

```python
from models.usuario import Base
target_metadata = Base.metadata
```
<p>(Essa última configuração no arquivo "env.py" sempre será alterada quando eu criar as novas tabelas do banco de dados, mas mandarei os tutoriais conforme altero)</p>
<p>Último passo para a configuração: Esse passo é importante para o alembic conseguir achar sua pasta. Na sua pasta de projeto raiz (back-voluntariado-extensao) você vai criar uma pasta chamada "database" sem as aspas.</p>
<p>Com tudo isso configurado, vamos agora criar o banco de dados. Talvez funciona com aquele mesmo terminal que você estava aberto, mas eu sugiro você fechar o terminal e abrir outro na pasta raiz do projeto, talvez ele tenha que recarregar algumas alterações. Com um novo terminal aberto vamos rodar o seguinte comando:</p>

```python
alembic revision --autogenerate -m "Inital migration"
```
<p>Se ele retornar o seguinte comando no terminal:</p>

```shell
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
[...]
```
<p>Você pode digitar o próximo e último comando:</p>

```shell
alembic upgrade head
```
<p>Agora você pode consultar agora dentro da sua pasta "database" que será gerado um arquivo banco.db, ele é o arquivo do "banco de dados" onde será guardado todas as informações que você armazenar e modificar.</p>
<p>Suponho que vocês não tenham essa extensão baixada, mas para ver melhor este arquivo banco.db você pode instalar no VS Code uma extensão chamada SQLite Viewer (O desenho é de um SQL com uma pena azul), isso vai melhorar a sua visualização no arquivo.
OBS: Isso é só um visualizador, você não vai conseguir alterar nada direto pelo arquivo do banco. Somente pelas rotas.</p>