# back-voluntariado-extensao
<p>Este é o back-end que estou estruturando para o nosso projeto de voluntários</p>
<br>
    <h1>Instalação</h1>
<br>

<p>
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30 align="middle">&nbsp;&nbsp;
    Após fazer a clonagem do repositório no computador, segue os passos abaixo:
</p>

<p>
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30 align="middle">&nbsp;&nbsp;
    Criar um arquivo na pasta raiz do projeto (back-voluntariado-extensao) chamado .env
</p>

<p>
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30 align="middle">&nbsp;&nbsp;
    Nesse arquivo você pode copiar as duas linhas abaixo
</p>

```env
SECRET_KEY=pGiggPz2p8xndOWQnTBY6fN3G3asyUa4
ALGORITHM=HS256
```
<p>
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30 align="middle">&nbsp;&nbsp;
    Dentro da pasta "notes" você pode abrir o arquivo dependencias.txt
</p>
<p>
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30 align="middle">&nbsp;&nbsp;
    Após isso você vai copiar o conteúdo no arquivo, abrir um terminal na raiz da pasta do projeto e mandar esse comando (precisa ter o Python instalado na máquina)
</p>
<p>
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30 align="middle">&nbsp;&nbsp;
    Para que não tiver o Pyhton, segue o link
</p>
<p>
    <img src="https://img1.picmix.com/output/stamp/normal/0/4/2/8/2648240_62c56.gif" width=30 align="middle">&nbsp;&nbsp;
    <a href="https://www.python.org/ftp/python/3.14.5/python-3.14.5-arm64.exe">Instalador</a>
</p>

<br>
<!-- ------------------------ -->
<h1>Configuração do banco</h1>
<br>

<p>
    <img src="https://preview.redd.it/trying-to-find-the-original-artist-behind-these-pixel-art-v0-h7mzbi1myiie1.gif?width=617&auto=webp&s=ec0a87a19a6bdbded3ec493aff2d987ce147ce07" width=50 align="middle">&nbsp;&nbsp;
    Ao terminar a configuração anterior, bora para a criação do banco (você só executa 1 vez)
</p>
<p>
    <img src="https://preview.redd.it/trying-to-find-the-original-artist-behind-these-pixel-art-v0-h7mzbi1myiie1.gif?width=617&auto=webp&s=ec0a87a19a6bdbded3ec493aff2d987ce147ce07" width=50 align="middle">&nbsp;&nbsp;
    Com o terminal ainda aberto na pasta do projeto, você vai rodar a linha de comando:
</p>

```shell
alembic init alembic
```
<p>
    <img src="https://preview.redd.it/trying-to-find-the-original-artist-behind-these-pixel-art-v0-h7mzbi1myiie1.gif?width=617&auto=webp&s=ec0a87a19a6bdbded3ec493aff2d987ce147ce07" width=50 align="middle">&nbsp;&nbsp;
    Dessa forma, dois itens serão criados: Um arquivo chamado "Alembic.ini" e uma pasta chamada "alembic"
</p>

<!-- --------------------------------- -->
<h2>Configuração arquivo alembic.ini</h2>

<p>
    <img src="https://media.tenor.com/3YHLRFmS-SYAAAAj/minecraft.gif" width=50 align="middle">
    Dentro do arquivo "alembic.init" você vai editar a linha 89 dele, que é para estar escrito o seguinte:
</p>

```python
sqlalchemy.url = driver://user:pass@localhost/dbname
```
<p>
    <img src="https://media.tenor.com/3YHLRFmS-SYAAAAj/minecraft.gif" width=50 align="middle">
    E você vai mudar para:
</p>

```python
sqlalchemy.url = sqlite:///database/banco.db
```

<!-- ----------------------------- -->
<h2>Configuração arquivo env.py</h2>

<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Agora dentro da pasta "alembic" você vai abrir o arquivo "env.py" e logo abaixo da linha 6 onde está escrito
</p>

```python
from alembic import context
```

<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Você pode quebrar 2 linhas e digitar o código abaixo:
</p>

```python
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
```

<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Depois um pouco abaixo do seu código, você vai procurar onde está escrito:
</p>

```python
target_metadata = None
```
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Acima dessa linha, você vai adicionar uma importação, digitando o seguinte:
</p>

```python
from database.database import Base
```
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    E logo abaixo, você vai fazer outra importação que é o seguinte:
</p>

```python
import models
```
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    E no target_metadata (na linha de baixo) você vai substituir o "None" por "Base.metadata", com o código ficando da seguinte maneira:
</p>

```python
from database.database import Base
import models
target_metadata = Base.metadata
```
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    (Essa última configuração no arquivo "env.py" sempre será alterada quando eu criar as novas tabelas do banco de dados, mas mandarei os tutoriais conforme altero)
</p>
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Com tudo isso configurado, vamos agora criar o banco de dados. Talvez funciona com aquele mesmo terminal que você estava aberto, mas eu sugiro você fechar o terminal e abrir outro na pasta raiz do projeto, talvez ele tenha que recarregar algumas alterações. Com um novo terminal aberto vamos rodar o seguinte comando:
</p>

```python
alembic revision --autogenerate -m "Inital migration"
```
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Se ele retornar o seguinte comando no terminal:
</p>

```shell
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
[...]
```
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Você pode digitar o próximo e último comando:
</p>

```shell
alembic upgrade head
```
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Agora você pode consultar agora dentro da sua pasta "database" que será gerado um arquivo banco.db, ele é o arquivo do "banco de dados" onde será guardado todas as informações que você armazenar e modificar.
</p>
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    Suponho que vocês não tenham essa extensão baixada, mas para ver melhor este arquivo banco.db você pode instalar no VS Code uma extensão chamada SQLite Viewer (O desenho é de um SQL com uma pena azul), isso vai melhorar a sua visualização no arquivo.
</p>
<p>
    <img src="https://minecraft.wiki/images/thumb/Warden_sniffing.gif/300px-Warden_sniffing.gif?3e874" width=50 align="middle">
    OBS: Isso é só um visualizador, você não vai conseguir alterar nada direto pelo arquivo do banco. Somente pelas rotas.
</p>