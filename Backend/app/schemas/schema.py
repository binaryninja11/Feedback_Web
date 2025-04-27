import datetime
from typing import Optional, Union, Dict

from fastapi import Query
from pydantic import BaseModel, Field
from enum import Enum
from datetime import date  # Fix for start_year

class Major(str, Enum):
    se = "Software Engineering"
    bm = "Business Management"
    it = "Information Technology"
    ad = "Art and Design"
    me = "Mechanical Engineering"

class QuestionType(str, Enum):
    multiple = "Multiple Choice"
    comment = "Comment"

class MultipleChoiceQuestion(str, Enum):
    excellent = "Excellent"
    very_Good = "Very Good"
    good = "Good"
    fair = "Fair"
    poor = "Poor"
    very_Poor = "Very Poor"

class AcademicYearOrSemester(str, Enum):
    academic_year = "academic"
    semester = "semester"

class SignUpStudent(BaseModel):
    stdid: str
    password: str
    level: int = Field(ge=1, le=4)  # Fixed

    major: Major

class CreateStudent(SignUpStudent):
    is_active: bool = True

class Student(BaseModel):
    id: int
    stdid: str
    level: int
    major: Major
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None  # Fixed Optional[str]

class SignUpTeacher(BaseModel):
    tid: str
    name: str
    last_name: str
    password: str

class Teacher(BaseModel):
    id: int
    tid: str
    name: str
    last_name: str
    is_active: bool

    class Config:
        from_attributes = True

class CreateSubject(BaseModel):
    subject_name: str
    major: Major
    level: int = Field(ge=1, le=4)  # Fixed
    start_year: date  # Fixed
    semester: int
    teacher_tid: str

class Subject(BaseModel):
    id: int
    subject_name: str
    major: Major
    level: int
    start_year: date  # Fixed
    semester: int
    is_active: bool
    teacher_id: str

    class Config:
        from_attributes = True

class CreateEnrollments(BaseModel):
    subject_id: int
    level: int = Field(ge=1, le=4)  # Fixed
    major: Major

class CreateEnrollment(BaseModel):
    subject_id: int
    stdid: str


class Enrollment(BaseModel):
    id: int
    student_id: int
    subject_id: int
    feedback: bool
    is_active: bool

    class Config:
        from_attributes = True

class StudentId(BaseModel):
    id: int

    class Config:
        from_attributes = True

class EnrollmentStudentSubjects(BaseModel):
    subject_id: int
    subject_name: str
    feedback: bool

    class Config:
        from_attributes = True



class CreateQuestion(BaseModel):
    header: Optional[str] = None
    body: str
    requirement: bool
    type: QuestionType

class ResponseQuestionWithActive(BaseModel):
    id: int
    header: Optional[str] = None
    body: str
    requirement: bool
    type: QuestionType

    class Config:
        from_attributes = True

class ResponseQuestion(BaseModel):
    id: int
    order: int
    header: Optional[str] = None
    body: str
    requirement: bool
    type: QuestionType
    is_active: bool

    class Config:
        from_attributes = True


class post_student_feedback(BaseModel):
    question_id: int
    answer: str

class create_feedback_with_qtype(BaseModel):
     question_id: int
     answer: str
     type: bool

class CreateAcademicYear(BaseModel):
    aos: AcademicYearOrSemester

class ResponseTeacher(BaseModel):
    tid: str
    name: str
    last_name: str

    class Config:
        from_attributes = True


class ResponseSujectIdName(BaseModel):
    subject_id: int
    subject_name: str

    class Config:
        from_attributes = True

class ChangeQuestionOrder(BaseModel):
    question_id_order_one: int
    question_id_order_two: int

class Action_to_archive(BaseModel):
    is_active: bool = False

class Subject_id_answer(BaseModel):
    subject_id: int
    excellent: int
    very_Good: int
    good: int
    fair: int
    poor: int
    very_Poor: int

    class Config:
        from_attributes = True

class Teacher_id_subject_id(BaseModel):
    teacher_id: int
    teacher_name : str
    subject_ids: list[int]

    class Config:
        from_attributes = True

class Teacher_with_Rating(BaseModel):
    teacher_name: str
    rating: float

    class Config:
        from_attributes = True

class Subject_Rating(BaseModel):
    subject_id: int
    subject_name: str
    rating: float = 0.0

    class Config:
        from_attributes = True

class FeedbackName(BaseModel):
    excellent: int = 0
    very_Good: int = 0
    good: int = 0
    fair: int = 0
    poor: int = 0
    very_Poor: int = 0


class SubjectDetail(BaseModel):
    subject_id: int
    teacher_name: str
    subject_name: str
    major: Major
    level: int
    start_year: date
    semester: int
    feedback: FeedbackName
    avarage: str

    class Config:
        from_attributes = True

class GetFilterBody(BaseModel):
    level: Optional[int] = None
    major: Optional[Major] = None
    semester: Optional[int] = None
    teacherId: Optional[str] = None


class ResponseFilter(BaseModel):
    subject_id: int
    subject_name: str
    average_Rating: str
    teacher_Name: str
    major: Major
    level: int
    semester: int

    class Config:
        from_attributes = True

class ResponseComment(BaseModel):
    question_body: str
    answer: str

    class Config:
        from_attributes = True

class ResponseQuestionWithAnswer(BaseModel):
    question_body: str
    answer: Dict[str, int]

    class Config:
        from_attributes = True

class CurrentSemesterResponseModel(BaseModel):
    semester: int

    class Config:
        from_attributes = True