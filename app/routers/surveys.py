"""
Survey API router.
Endpoints for weekly survey data operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import WeeklySurvey
from app.schemas import WeeklySurveyResponse

router = APIRouter(
    prefix="/api",
    tags=["surveys"]
)


@router.get(
    "/surveys",
    response_model=List[WeeklySurveyResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all weekly surveys",
    description="Retrieve all weekly survey records from the database."
)
def get_all_surveys(db: Session = Depends(get_db)):
    """
    Get all weekly survey records.
    
    Returns:
        List of WeeklySurveyResponse objects containing all survey data.
    
    Raises:
        HTTPException: If database error occurs.
    """
    try:
        surveys = db.query(WeeklySurvey).all()
        return surveys
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
