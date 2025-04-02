from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    stdid = Column(String, index=True, nullable=False, unique=True)
    name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    level = Column(String, nullable=True)
    major = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete")

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String, index=True, nullable=False)
    major = Column(String, index=True, nullable=False)
    level = Column(Integer, index=True, nullable=False)
    start_year = Column(DateTime, nullable=False)
    semester = Column(Integer, index=True, nullable=False)
    active = Column(Boolean, default=True)
    teacher_id =Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    enrollments = relationship("Enrollment", back_populates="subject", cascade="all, delete")
    feedbacks = relationship("Feedback", back_populates="subject", cascade="all, delete")

    teacher = relationship("Teacher", back_populates="subjects")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    feedback = Column(Boolean, nullable=True)

    student = relationship("Student", back_populates="enrollments")
    subject = relationship("Subject", back_populates="enrollments")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    order = Column(Integer, index=True, nullable=False)
    header = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    requirement = Column(Boolean, default=False)
    type = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    feedbacks = relationship("Feedback", back_populates="question", cascade="all, delete")

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    answer = Column(Text, nullable=False)
    active = Column(Boolean, default=True)

    question = relationship("Question", back_populates="feedbacks")
    subject = relationship("Subject", back_populates="feedbacks")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    active = Column(Boolean, default=True)

    subjects = relationship("Subject", back_populates="teacher", cascade="all, delete")
