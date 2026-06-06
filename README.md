# back-voluntariado-extensao
<p>Este é o back-end que estou estruturando para o nosso projeto de voluntários</p>
<br>
    <h1>Atualização de tabelas no banco</h1>
<br>

<p>
    <img src="./assets/gif/notch.webp" width=60 align="middle">&nbsp;&nbsp;
    Para funcionar a parte do cadastro de entidades, e dos cargos de admins nas entidades
</p>

<p>
    <img src="./assets/gif/notch.webp" width=60 align="middle">&nbsp;&nbsp;
    Primeiro vamos rodar o seguinte código em um terminal aberto na pasta raíz do projeto (back-volutnariado-extensao)
</p>

```shell
alembic revision --autogenerate -m "creation entity and member_entity"
```

<p>
    <img src="./assets/gif/notch.webp" width=60 align="middle">&nbsp;&nbsp;
    É para ele responder com algumas mensagens como abaixo:
</p>

```shell
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.schemas
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.tables
INFO  [alembic.runtime.plugins] setting up autogenerate plugin alembic.autogenerate.types
```

<p>
    <img src="./assets/gif/notch.webp" width=60 align="middle">&nbsp;&nbsp;
    Se apareceu isso é porque não deu erro. Só mandar mais o código abaixo para atualizar o banco 
</p>

```shell
alembic upgrade head
```

<p>
    <img src="./assets/gif/notch.webp" width=60 align="middle">&nbsp;&nbsp;
    Dessa forma, se ele não retornar erro, seu banco já é para ter criado as tabelas "entidades" e "membros_entidades"
</p>