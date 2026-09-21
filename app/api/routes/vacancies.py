from fastapi import APIRouter, Response, status

from app.models.vacancy import VacancyModality
from app.api.dependencies import ActualUser, BaseSession
from app.schemas.vacancy import CreateVacancies, ResponseVacancies, UpdateVacancies, ListVacancies
from app.services.vacancies import VacancieService
from app.services.vacancy_participants import VacancyParticipantService
from app.schemas.vacancy_participant import VacancyParticipantResponse

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


@router.get(
    "/{id_vacancy}/participants",
    response_model=list[VacancyParticipantResponse],
)
def list_vacancy_participants(
    id_vacancy: int,
    user: ActualUser,
    session: BaseSession,
):
    return VacancyParticipantService(session).list_participants(
        id_vacancy, user
    )


@router.delete(
    "/{id_vacancy}/participants/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def leave_vacancy(
    id_vacancy: int,
    user: ActualUser,
    session: BaseSession,
) -> Response:
    VacancyParticipantService(session).leave_vacancy(id_vacancy, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{id_vacancy}/participants/{id_user}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_vacancy_participant(
    id_vacancy: int,
    id_user: int,
    user: ActualUser,
    session: BaseSession,
) -> Response:
    VacancyParticipantService(session).remove_participant(
        id_vacancy, id_user, user
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.patch("/{id_vacancy}", response_model=ResponseVacancies)
def update_vacancy(id_vacancy: int, data: UpdateVacancies, user: ActualUser, session: BaseSession):
    return VacancieService(session).update(id_vacancy, data, user)

@router.delete("/{id_vacancy}")
def delete_vacancy(id_vacancy: int, user: ActualUser, session: BaseSession):
    return VacancieService(session).delete(id_vacancy, user)
