from fastapi import APIRouter, status

from app.api.dependencies import BaseSession
from app.models.vacancies import VacancyModality
from app.api.dependencies import ActualUser
from app.schemas.vacancies import CreateVacancies, ResponseVacancies, UpdateVacancies, ListVacancies
from app.services.vacancies import VacancieService

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

@router.post("", response_model=ResponseVacancies, status_code=status.HTTP_201_CREATED)
def create_vacancy(data: CreateVacancies, user: ActualUser, session: BaseSession):
    return VacancieService(session).create(data, user)

@router.get("/", response_model=list[ListVacancies])
def list_vacancies(
    session: BaseSession,
    id: int | None = None,
    city: str | None = None,
    uf: str | None = None,
    branch: str | None = None,
    id_entity: int | None = None,
    title: str | None = None,
    modality: VacancyModality | None = None
    ):
    return VacancieService(session).list(
        id=id,
        city=city,
        uf=uf,
        branch=branch,
        id_entity=id_entity,
        title=title,
        modality=modality
    )

@router.patch("/{id_vacancy}", response_model=ResponseVacancies)
def update_vacancy(id_vacancy: int, data: UpdateVacancies, user: ActualUser, session: BaseSession):
    return VacancieService(session).update(id_vacancy, data, user)

@router.delete("/{id_vacancy}")
def delete_vacancy(id_vacancy: int, user: ActualUser, session: BaseSession):
    return VacancieService(session).delete(id_vacancy, user)