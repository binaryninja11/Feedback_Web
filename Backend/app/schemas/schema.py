from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class TaskType(str, Enum):
    image = "image"
    text = "text"
    video = "video"


class CategoryBase(BaseModel):
    category_name: str
    main_image_id: Optional[int] = None
    description: str
    skill: str = None


