from typing import List

from sqlalchemy.orm import Session

from app.crud import crud
from app.schemas import schema


def calculate(VP: int, P: int, F: int, G: int, VG: int, E: int) -> float:
    total = VP + P + F + G + VG + E
    if total == 0:
        return 0.0  # or return None, depending on your logic
    summ = VP * 1 + P * 3 + F * 5 + G * 7 + VG * 9 + E * 10
    rating = summ / total
    return rating

# calculate the subject answer
async def calculate_subject_answer(db: Session) -> List[schema.Teacher_with_Rating]:
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

    result

    return result


