from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.language import normalize_language_code
from app.db.session import get_session
from app.modules.accounts.dependencies import get_optional_current_account
from app.modules.accounts.models import UserAccount
from app.modules.curriculum import schemas, service

router = APIRouter()


def _locale_query() -> str | None:
    return Query(default=None, pattern="^(id|en)$")


def _resolve_locale(locale: str | None, account: UserAccount | None) -> str:
    if locale:
        return normalize_language_code(locale, fallback="id")
    profile = account.learner_profile if account else None
    if profile and profile.preferred_language:
        return normalize_language_code(profile.preferred_language, fallback="id")
    return "id"


@router.get("/subjects", response_model=schemas.SubjectListResponse)
def list_subjects(
    locale: str | None = _locale_query(),
    account: UserAccount | None = Depends(get_optional_current_account),
    session: Session = Depends(get_session),
) -> schemas.SubjectListResponse:
    resolved_locale = _resolve_locale(locale, account)
    subjects = service.list_active_subjects(session)
    return schemas.SubjectListResponse(
        items=[
            service.subject_to_schema(
                subject,
                locale=resolved_locale,
                for_knowledge_graph_selector=True,
            )
            for subject in subjects
        ]
    )


@router.get("/knowledge-map", response_model=schemas.KnowledgeMapResponse)
def get_knowledge_map(
    subject: str = Query(..., min_length=1),
    locale: str | None = _locale_query(),
    account: UserAccount | None = Depends(get_optional_current_account),
    session: Session = Depends(get_session),
) -> schemas.KnowledgeMapResponse:
    resolved_locale = _resolve_locale(locale, account)
    knowledge_map = service.get_knowledge_map(
        session,
        subject_code=subject,
        locale=resolved_locale,
        user=account,
    )
    if knowledge_map is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject '{subject}' was not found or has no curriculum graph.",
        )
    return knowledge_map


@router.get(
    "/knowledge-map/concepts/{concept_code}",
    response_model=schemas.ConceptDetailResponse,
)
def get_concept_detail(
    concept_code: str,
    subject: str | None = Query(default=None, min_length=1),
    locale: str | None = _locale_query(),
    account: UserAccount | None = Depends(get_optional_current_account),
    session: Session = Depends(get_session),
) -> schemas.ConceptDetailResponse:
    resolved_locale = _resolve_locale(locale, account)
    detail = service.get_concept_detail(
        session,
        concept_code=concept_code,
        subject_code=subject,
        locale=resolved_locale,
        user=account,
    )
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concept '{concept_code}' was not found.",
        )
    return detail
