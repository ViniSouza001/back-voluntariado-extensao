from fastapi import APIRouter, Response, status

from app.models.vacancy import VacancyModality
from app.api.dependencies import ActualUser, BaseSession
from app.schemas.vacancy import CreateVacancies, ResponseVacancies, UpdateVacancies, ListVacancies
from app.services.vacancies import VacancieService
from app.services.vacancy_participants import VacancyParticipantService
from app.schemas.vacancy_participant import VacancyParticipantResponse
from app.schemas.vacancy_join_request import (
    DecideVacancyJoinRequest,
    VacancyJoinRequestResponse,
)
from app.services.vacancy_join_requests import VacancyJoinRequestService

router = APIRouter(prefix="/vacancies", tags=["vacancies"])

@router.post("", response_model=ResponseVacancies, status_code=status.HTTP_201_CREATED)
def create_vacancy(data: CreateVacancies, user: ActualUser, session: BaseSession):
    return VacancieService(session).create(data, user)

@router.get("", response_model=list[ListVacancies])
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


@router.get("/join-requests/me", response_model=list[VacancyJoinRequestResponse])
def list_my_vacancy_join_requests(user: ActualUser, session: BaseSession):
    return VacancyJoinRequestService(session).list_for_user(user)


@router.post(
    "/{id_vacancy}/join-requests",
    response_model=VacancyJoinRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vacancy_join_request(
    id_vacancy: int, user: ActualUser, session: BaseSession
):
    return VacancyJoinRequestService(session).create(id_vacancy, user)


@router.get(
    "/{id_vacancy}/join-requests",
    response_model=list[VacancyJoinRequestResponse],
)
def list_vacancy_join_requests(
    id_vacancy: int,
    user: ActualUser,
    session: BaseSession,
    pending_only: bool = True,
):
    return VacancyJoinRequestService(session).list_for_vacancy(
        id_vacancy, user, pending_only
    )


@router.patch(
    "/{id_vacancy}/join-requests/{id_request}",
    response_model=VacancyJoinRequestResponse,
)
def decide_vacancy_join_request(
    id_vacancy: int,
    id_request: int,
    data: DecideVacancyJoinRequest,
    user: ActualUser,
    session: BaseSession,
):
    return VacancyJoinRequestService(session).decide(
        id_vacancy, id_request, data.status, user
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
