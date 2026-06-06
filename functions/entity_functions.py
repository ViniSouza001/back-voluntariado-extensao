from fastapi import HTTPException
from models.entidade import Entidade
from models.membro_entidade import MembroEntidade, CargoMembro

def criar_entidade (entidade_schema, usuario, session):
    entidade_existente = session.query(Entidade).filter(Entidade.nome_usuario == entidade_schema.nome_usuario).first()

    if entidade_existente:
        raise HTTPException(401, "Já existe uma entidade com este nome de usuário")
    else:
        nova_entidade = Entidade (
            entidade_schema.nome,
            entidade_schema.nome_usuario,
            entidade_schema.ramo,
            entidade_schema.descricao,
            entidade_schema.cidade,
            entidade_schema.uf,
        )
        
        session.add(nova_entidade)
        session.flush()

        novo_membro = MembroEntidade (
            id_usuario = usuario.id,
            id_entidade = nova_entidade.id,
            cargo = CargoMembro.admin
        )

        session.add(novo_membro)
        session.commit()
        session.refresh(nova_entidade)

        return nova_entidade