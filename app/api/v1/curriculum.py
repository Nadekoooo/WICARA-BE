from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.modules.curriculum import schemas, service

router = APIRouter()


@router.get("/subjects", response_model=schemas.SubjectListResponse)
def list_subjects(session: Session = Depends(get_session)) -> schemas.SubjectListResponse:
    subjects = service.list_active_subjects(session)
    return schemas.SubjectListResponse(
        items=[service.subject_to_schema(subject) for subject in subjects]
    )


@router.get("/knowledge-map", response_model=schemas.KnowledgeMapResponse)
def get_knowledge_map(
    subject: str = Query(..., min_length=1),
    session: Session = Depends(get_session),
) -> schemas.KnowledgeMapResponse:
    knowledge_map = service.get_knowledge_map(session, subject_code=subject)
    if knowledge_map is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject '{subject}' was not found or has no curriculum graph.",
        )
    return knowledge_map
