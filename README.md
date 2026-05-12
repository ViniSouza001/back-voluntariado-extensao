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

<!-- TUTORIAL PARA RODAR O BACK-END -->
<h1>Tutorial para rodar o back-end</h1>

<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    Para o back-end funcionar, vamos primeiramente continuar com o terminal na pasta raiz do projeto (back-voluntariado-extensao)
</p>
<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    Nesse terminal nós vamos rodar o seguinte comando:
</p>

```cmd
uvicorn main:app --reload
```
<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    Supostamente é para ele dar uma mensagem parecida com essa:
</p>

```cmd
INFO:     Will watch for changes in these directories: ['C:\\Desktop\\Coding\\proj facul\\back-voluntariado-extensao']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [16916] using StatReload
```
<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    Com isso, nosso back-end já está funcionando. No próprio terminal do VS Code você pode segurar a tecla 'Enter' e dar um clique no link que ele passa "http://127.0.0.1:8000", irá abrir uma aba do navegador padrão com esse link
</p>
<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    Se ele responder com uma tela de
</p>

```JSON
{"detail": "Not found"}
```
<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    Desinstale o banco de dados, e refaça o tutorial
</p>
<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    É nada, mensagem de "Not found" é normal
</p>

<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    No link que está no navegador "http://127.0.0.1:8000/" você vai escrever um "docs" na frente da barra, ficando assim: "http://127.0.0.1:8000/docs"
</p>
<p>
    <img src="https://media0.giphy.com/media/v1.Y2lkPTZjMDliOTUyZGRpazJxMXEyZHp0MnYycmY5bHVlMGt6cWdraXpqbzZ6aDM1eXNkbSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Nx4C51UKPqEpsYDz58/giphy.gif" width=60 align="middle">
    A tela que aparecerá é a própria documentação da biblioteca que eu usei, nela vai aparecer todas as rotas que existem no back-end e o que cada rota solicita de obrigatório para manipular os dados
</p>

<h1>Testando rota /auth/register </h1>
<p>
    <img src="./assets/piglin-dancing.gif" width=80 align="middle">
    A única rota que vai aparecer é uma de verde, do tipo POST, vai ter o nome do caminho "/auth/register" e na frente o nome da função "Criar Conta". Você pode clicar em qualquer parte do verde para expandir ela  
</p>
<p>
    <img src="./assets/piglin-dancing.gif" width=80 align="middle">
    O que realmente vale para nós no momento é o botão "Try it out" e o pedaço de Json que está abaixo da escrita "Example Value | Schema", no momento ele está dessa forma:
</p>

```JSON
{
  "nome": "string",
  "email": "string",
  "senha": "string",
  "data_nasc": "2026-05-12",
  "cidade": "string",
  "uf": "string",
  "confirmado": false,
  "admin": false
}
```
<p>
    <img src="./assets/piglin-dancing.gif" width=80 align="middle">
    Para você dar aquela testada marota, primeiro clica no botão "Try it out" no canto direito logo abaixo da parte verde da rota que você clicou
</p>
<p>
    <img src="./assets/piglin-dancing.gif" width=80 align="middle">
    Agora o JSON está liberado para você testar maroto. Para fazer o teste, vou deixar um exemplo aqui abaixo (que funciona) e você pode alterar os dados da maneira que você quer, mas não adicionar campo nem remover
</p>

```JSON
{
  "nome": "Vinicius Vieira de Souza",
  "email": "vinicius@teste.com",
  "senha": "123456",
  "data_nasc": "2005-07-13",
  "cidade": "Pedreira",
  "uf": "SP",
  "confirmado": false,
  "admin": true
}
```
<p>
    <img src="./assets/piglin-dancing.gif" width=80 align="middle">
    Se você seguiu os passos corretamente e o back-end colaborou com você, então rolando a tela um pouco mais para baixo, você vai ver um código com status 200 (código 200 significa "sucesso") e um retorno parecido com isso:
</p>

```JSON
{
  "Mensagem": "Usuario cadastrado com sucesso com e-mail vinicius@teste.com"
}
```
<p>
    <img src="./assets/piglin-dancing.gif" width=80 align="middle">
    Agora quando você ir no seu arquivo "banco.db" dentro da pasta "database", e ir na coluna "usuarios", vai ter o seu usuário cadastrado, com a senha criptografada e as demais informações disponíveis.
</p>
<p>
    <img src="./assets/piglin-dancing.gif" width=80 align="middle">
    O importante é o back-end não deixar passar erros, por exemplo, você não colocar a informação de "nome", "email", "senha" ou colocar uma "data_nasc" diferente, por exemplo "13-07-2005". Não é o padrão que o back-end reconhece.
</p>