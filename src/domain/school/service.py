from sqlalchemy.orm import Session
from . import models, schemas
from ..role.models import UserRole
from sqlalchemy import func
from fastapi import HTTPException
from resources.strings import SCHOOL_DOES_NOT_EXIST_ERROR, SCHOOL_DELETE_SUCCESSFUL, SCHOOL_UPDATE_SUCCESSFUL
import re

def get_school(db: Session, school_id: str):
    return db.query(models.School).filter(models.School.school_id == school_id).first()

def get_schools(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.School).offset(skip).limit(limit).all()

def get_schools_by_params(db: Session, selected_fields: list, filters:list, ordering:list, skip: int = 0, limit: int = 100):
    orm_attributes = [getattr(models.School, field) for field in selected_fields]
    return db.query(models.School).with_entities(*orm_attributes).filter(*filters).order_by(*ordering).offset(skip).limit(limit).all()

def create_school(db: Session, school: schemas.SchoolBase):
    try:
        db_school = models.School(**school.model_dump())
        db.add(db_school)
        db.commit()
        db.refresh(db_school)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_school

def update_school(db: Session, school_id: str, school: schemas.SchoolUpdate):
    try:
        db_school = db.query(models.School).filter(models.School.school_id == school_id).first()
        if not db_school:
            raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)        
        for key, value in school.model_dump(exclude_none=True).items():
            setattr(db_school, key, value)
        db.commit()
        db.refresh(db_school)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": SCHOOL_UPDATE_SUCCESSFUL}

def delete_school(db: Session, school_id: str):
    try:
        db_school = db.query(models.School).filter(models.School.school_id == school_id).first()
        if not db_school:
            raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)
        db.delete(db_school)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": SCHOOL_DELETE_SUCCESSFUL}

def get_school_classes(db: Session, school_id: str):
    # Filter the query by the given school_id
    result = db.query(
        models.Class.id.label('class_id'),
        models.Class.grade,
        models.Class.section,
        # Subquery to find the teacher
        (db.query(models.UserRole.user_id)
         .filter(UserRole.level_id == models.Class.id, UserRole.level == 'teacher')
         .limit(1)
         .as_scalar()).label('class_teacher'),
        # Subquery to count the number of students
        (db.query(func.count())
         .filter(UserRole.level_id == models.Class.id, UserRole.level == 'student')
         .scalar()).label('student_count')
    ).filter(models.Class.school_id == school_id).all()  # Filter by school_id

    for row in result:
        print(f"Class ID: {row.class_id}, Grade: {row.grade}, Section: {row.section}, Teacher: {row.class_teacher}, Students: {row.student_count}")
    return result

def create_school_class(db: Session, school_class: schemas.ClassBase):
    try:
        db_class = models.Class(**school_class.model_dump())
        db.add(db_class)
        db.commit()
        db.refresh(db_class)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return db_class

def delete_school_class(db: Session, school_id: str, class_id: str):
    try:
        db_school = db.query(models.Class).filter(
            (models.Class.school_id == school_id) & (models.Class.class_id == class_id)).first()
        if not db_school:
            raise HTTPException(status_code=404, detail=SCHOOL_DOES_NOT_EXIST_ERROR)
        db.delete(db_school)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=_extract_detail_text(str(e)))
    return {"message": SCHOOL_DELETE_SUCCESSFUL}

def _extract_detail_text(error_message: str) -> str:
    match = re.search(r"DETAIL:\s+(.*)", error_message)

    if match:
        detail_text = match.group(1)
        return detail_text
    else:
        return "Error occurred while processing the request"

