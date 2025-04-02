from sqlalchemy.orm import Session
from app.models.dbmodel import Category, Image, Image_main
from app.schemas.schema import CreateCategory, CreateImage
from fastapi import HTTPException

def create_category(db: Session, ct: CreateCategory):
    try:
        new_category = Category(
            category_name=ct.category_name,
            main_image_id=ct.main_image_id,
            description=ct.description,
            skill=ct.skill  # This will trigger the setter
        )

        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while creating category: {e}")



def get_category_by_id(db: Session, category_id: int):
    category = db.query(Category).filter(Category.id == category_id).first()
    return category


def get_categories(db: Session):
    try:
        return db.query(Category).all()
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while getting categories: {e}")





def get_category_by_name(db: Session, category_name: str):
    try:
        return db.query(Category).filter(Category.category_name == category_name).first()
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while getting category by name: {e}")


def create_imge_main(db: Session, name: str = None, name_base64: str = None, category_id: int = None):
    try:
        image_main = Image_main(
            name=name,
            name_base64=name_base64,
            category_id=category_id
        )
        db.add(image_main)
        db.commit()
        db.refresh(image_main)
        return image_main
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while creating image_main: {e}")


def image_main_check_by_category_id(db: Session, category_id: int):
    return db.query(Image_main).filter(Image_main.category_id == category_id).first()


def change_main_img(db: Session, img_base64: str, category_id: int):
    try:
        category = get_category_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404,detail=f"Category with ID {category_id} not found")

        image_main = image_main_check_by_category_id(db, category_id)

        if not image_main:
            image_main = create_imge_main(db, name_base64=img_base64, category_id=category_id)
            category.main_image_id = image_main.id
            db.commit()
            return f"Main image created and updated for category ID {category_id}"
        else:
            db.query(Image_main).filter(Image_main.category_id == category_id).update({"name_base64": img_base64})
            db.commit()
            return f"Main image updated for category ID {category_id}"
    except HTTPException:  # Let 404 errors propagate correctly
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"Error in change_main_img: {e}")

def check_image_by_base64(db: Session, name_base64: str):
    return db.query(Image).filter(Image.name_base64 == name_base64).first()

def get_image_by_id(db: Session, img_id: int):
    return db.query(Image).filter(Image.id == img_id).first()

def get_images_by_category_id(db: Session, category_id: int):
    return db.query(Image).filter(Image.category_id == category_id).all()

def create_image(db: Session, img: CreateImage):
    try:
        new_image = Image(
            name=img.name,
            name_base64=img.name_base64,
            category_id=img.category_id
        )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)
        return new_image
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while creating image: {e}")

def del_category(db: Session, category_id: int):
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            db.delete(category)
            db.commit()
            return f"Category {category_id} deleted"
        else:
            raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

    except HTTPException:  # Let 404 errors propagate correctly
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while deleting category: {e}")



def del_image(db: Session, img_id: int):
    try:
        image = db.query(Image).filter(Image.id == img_id).first()
        if image is None:
            raise HTTPException(status_code=404, detail=f"Image {img_id} not found")

        db.delete(image)
        db.commit()
        return {"message": f"Image {img_id} deleted"}  # Returning a JSON response

    except HTTPException:  # Let 404 errors propagate correctly
        raise
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while deleting image: {e}")



def get_image_by_category_id(db: Session, category_id: int):
    try:
        return db.query(Image).filter(Image.category_id == category_id).all()
    except Exception as e:
        db.rollback()
        raise Exception(f"An error occurred while getting images: {e}")