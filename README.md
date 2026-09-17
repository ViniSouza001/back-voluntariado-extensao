# back-voluntariado-extensao
<p>Este é o back-end que estou estruturando para o nosso projeto de voluntários</p>
<br>
    <h1>Instalação</h1>
<br>

<p>
    <img src="./assets/gif/villager.gif" width=30 align="middle">&nbsp;&nbsp;
    Entrar na pasta do backend com um terminal (recomendo usar o PowerShell)
</p>

<p>
    <img src="./assets/gif/ghast.gif" width=50 align="middle">&nbsp;&nbsp;
    Criar ambiente virtual
</p>

```shell
python -m venv .venv
```

<p>
    <img src="./assets/gif/warden_sniffing.webp" width=50 align="middle">
    Instalar as dependências
</p>

```shell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
<br>
<!-- TUTORIAL PARA RODAR O BACK-END -->
<h1>Arquivo .env</h1>

<p>
    <img src="./assets/gif/steve_dancing.webp" width=60 align="middle">
    No terminal powershell, dentro da pasta do backend, você pode rodar o comando
</p>

```shell
Copy-Item .env.example .env
```

<p>
    <img src="./assets/gif/steve_dancing.webp" width=60 align="middle">
    Ou você pode copiar todo o conteúdo do arquivo .env.example e colar dentro de um arquivo .env
</p>

<h1>Configurar arquivo .env</h1>

```env
APPLICATION_NAME="Você pode colocar qualquer nome personalizado"
DEPURATION=true
URL_DATABASE=sqlite:///data/database.db <-- Esse é o padrão

SECRET_KEY=coloque-uma-chave-secreta-aqui  <-- Próximo tópico explica isso
ALGORITHM=HS256 <-- Tipo de hash, pode alterar ou pode deixar assim mesmo

MINUTES_EXPIRE_ACCESS_TOKEN=30
MINUTES_EXPIRE_CONFIRMATION_EMAIL=15
MINUTES_RESEND_CONFIRMATION_EMAIL=5

ORIGENS_CORS=http://localhost:3000,http://localhost:5173
URL_FRONTEND=http://localhost:5173

EMAIL_ENABLED=true  <-- deixar "true" para a experiência completa de emissão de e-mail
USER_EMAIL=
PASSWORD_EMAIL=
SENDER_EMAIL=
SERVER_EMAIL=smtp.gmail.com
PORT_EMAIL=587
```

<p>
    <img src="./assets/gif/piglin_dancing.gif" width=60 align="middle">&nbsp;&nbsp;
    Para gerar uma chave secreta para o .env no terminal powershell ou no cmd, escreva o código abaixo:
</p>

```shell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

<p>
    <img src="./assets/gif/piglin_dancing.gif" width=60 align="middle">&nbsp;&nbsp;
    Copie o código monstruoso do terminal (botão direito do mouse copia o conteúdo selecionado em prompts) e cole o código monstruoso na variável SECRET_KEY do arquivo .env substituido o texto "coloque-uma-chave-secreta-aqui". A geração de chave secretas podem ser feitas por sites também caso seja preferível, esta é apenas uma opção fácil, mas funcional e seguro também
</p>

<p>
    <img src="./assets/gif/zumbizinho.gif" width=100 align="middle">
    Caso o comando não funcione, você pode apenas ver se na raiz do projeto backend tem as pastas "data" e "uploads"
</p>

<p>
    <img src="./assets/gif/notch.webp" width=70 align="middle">
    Criar e atualizar o banco de dados
</p>

<p>
    Na primeira instalação, o comando abaixo cria as tabelas. Se você já tem um banco local, ele aplica somente as migrações que ainda faltam, sem precisar recriar o banco.
</p>

```shell
python -m alembic upgrade head
```

<h1>Atualizar um banco que já existe</h1>

<p>
    <img src="./assets/gif/notch.webp" width=70 align="middle">
    Antes de atualizar, confira a variável <code>URL_DATABASE</code> no seu <code>.env</code>. O Alembic vai alterar exatamente esse banco. O <code>.env.example</code> aponta para <code>data/banco.db</code>; se você já usava outro nome ou caminho, mantenha o caminho do seu banco atual para não criar um banco novo por engano.
</p>

<p>
    <img src="./assets/gif/warden_sniffing.webp" width=50 align="middle">
    Se o banco SQLite já contém dados, faça uma cópia do arquivo indicado em <code>URL_DATABASE</code> antes de executar a atualização.
</p>

<p>
    <img src="./assets/gif/notch.webp" width=70 align="middle">
    Dentro da pasta do backend, com as dependências instaladas e o <code>.env</code> configurado, verifique a versão atual, aplique as migrações e confira novamente:
</p>

```shell
python -m alembic current
python -m alembic upgrade head
python -m alembic current
```

<p>
    A migração mais recente deste projeto é <code>d7c81a4e69b2</code>.
</p>

<h1>O que mudou no banco e na API</h1>

<p>
    <img src="./assets/gif/ghast.gif" width=50 align="middle">
    Agora existe a tabela <code>vacancies</code> para as vagas voluntárias. As vagas têm modalidade <code>remote</code> ou <code>in_person</code>. Para vagas presenciais, a API exige logradouro, cidade e UF; CEP, número e complemento são opcionais. Ao atualizar um banco que já tinha vagas, a migração marca como remotas as vagas antigas sem modalidade e remove a antiga coluna <code>location</code>. Confira esses dados antes de atualizar se você já cadastrou vagas.
</p>

<p>
    <img src="./assets/gif/villager.gif" width=40 align="middle">
    Um usuário pode pertencer a somente uma entidade. A pessoa que cria a entidade vira <code>admin</code>; os papéis possíveis são <code>admin</code>, <code>editor</code> e <code>member</code>. Administradores e editores podem criar, editar e excluir vagas da própria entidade. Somente um administrador pode alterar o papel de outro membro, e a entidade precisa manter pelo menos um administrador.
</p>

<p>
    <img src="./assets/gif/zumbizinho.gif" width=70 align="middle">
    Se a migração parar com a mensagem de que há usuários ligados a mais de uma entidade, resolva esses vínculos no banco antes de executar <code>python -m alembic upgrade head</code> novamente. A atualização não escolhe automaticamente qual entidade manter.
</p>

<p>
    <img src="./assets/gif/steve_dancing.webp" width=60 align="middle">
    Nas vagas, datas e horas recebidas sem fuso são interpretadas como horário de Brasília. O backend guarda o instante em UTC no banco, sem informação de fuso na coluna, e devolve as datas em horário de Brasília nas respostas da API.
</p>

<p>
    <img src="./assets/gif/villager.gif" width=40 align="middle">
    Iniciar o backend
</p>

<br>
<br>

```shell
python -m uvicorn app.main:app --reload
```

<p>
    <img src="./assets/gif/steve_dancing.webp" width=70 align="middle">
    API: http://127.0.0.1:8000
</p>

<p>
    <img src="./assets/gif/wolf.gif" width=60 align="middle">&nbsp;&nbsp;
    Documentação Swagger: http://127.0.0.1:8000/docs
</p>
