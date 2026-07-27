class ErroAplicacao(Exception):
    codigo_status = 400

    def __init__(self, detalhe: str):
        self.detalhe = detalhe
        super().__init__(detalhe)


class ErroAutenticacao(ErroAplicacao):
    codigo_status = 401


class ErroNaoEncontrado(ErroAplicacao):
    codigo_status = 404


class ErroConflito(ErroAplicacao):
    codigo_status = 409


class ErroValidacao(ErroAplicacao):
    codigo_status = 422
