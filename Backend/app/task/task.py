from typing import List

from sqlalchemy.orm import Session

from app.crud import crud
from app.schemas import schema

def get_rating_label(score: float) -> str:
    if score >= 9.0:
        return "Excellent"
    elif score >= 8.0:
        return "Very Good"
    elif score >= 6.0:
        return "Good"
    elif score >= 4.0:
        return "Fair"
    elif score >= 2.0:
        return "Poor"
    else:
        return "Very Poor"


def calculate(VP: int, P: int, F: int, G: int, VG: int, E: int) -> float:
    total = VP + P + F + G + VG + E
    if total == 0:
        return 0.0  # or return None, depending on your logic
    summ = VP * 1 + P * 3 + F * 5 + G * 7 + VG * 9 + E * 10
    rating = summ / total
    return rating

# calculate the subject answer
async def calculate_subject_answer_teacher(db: Session) -> List[schema.Teacher_with_Rating]:
    # Get the feedbacks grouped by subject
    feedbacks = await crud.get_subject_id_answer_question_type_true(db=db)

    # Get all teachers and their subject_ids
    teachers_with_id = await crud.get_all_teachers_id_subject_id(db=db)

    result = []

    for t in teachers_with_id:
        answer_count = {
            "excellent": 0,
            "very_Good": 0,
            "good": 0,
            "fair": 0,
            "poor": 0,
            "very_Poor": 0
        }

        for sub_id in t.subject_ids:
            if sub_id in feedbacks:
                for key in answer_count:
                    answer_count[key] += feedbacks[sub_id].get(key, 0)

        # Calculate the rating
        rating = calculate(
            VP=answer_count["very_Poor"],
            P=answer_count["poor"],
            F=answer_count["fair"],
            G=answer_count["good"],
            VG=answer_count["very_Good"],
            E=answer_count["excellent"]
        )

        result.append(schema.Teacher_with_Rating(
            teacher_name=t.teacher_name,
            rating=round(rating, 2)
        ))

    return result


async def calculate_subject_ratings(db: Session) -> List[schema.Subject_Rating]:
    feedbacks = await crud.get_subject_id_answer_question_type_true(db=db)

    result = []

    for subject_id, scores in feedbacks.items():
        rating = calculate(
            VP=scores["very_Poor"],
            P=scores["poor"],
            F=scores["fair"],
            G=scores["good"],
            VG=scores["very_Good"],
            E=scores["excellent"]
        )

        subject = await crud.get_subject_by_id(db, subject_id)
        result.append(schema.Subject_Rating(
            subject_id=subject_id,
            subject_name=subject.subject_name,
            rating=round(rating, 2)
        ))

    return result

