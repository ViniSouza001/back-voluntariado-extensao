from fastapi import APIRouter, status

from app.api.dependencies import BaseSession
from app.schemas.vacancies import CreateVacancies, ResponseVacancies, UpdateVacancies, DeleteVacancies, ListVacancies
from app.services.vacancies import VacancieService

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

@router.post("", response_model=ResponseVacancies, status_code=status.HTTP_201_CREATED)
def create_vacancy(data: CreateVacancies, session: BaseSession):
    return VacancieService(session).create(data)

@router.get("/", response_model=list[ListVacancies])
def list_vacancies(session: BaseSession, city: str | None = None, uf: str | None = None, branch: str | None = None, id_entity: int | None = None, title: str | None = None):
    return VacancieService(session).list(city, uf, branch, id_entity, title)

@router.delete("/{id_vacancy}")
def delete_vacancy(id_vacancy: int, session: BaseSession):
    return VacancieService(session).delete(id_vacancy)