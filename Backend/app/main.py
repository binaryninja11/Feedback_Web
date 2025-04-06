import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# from app.views import router
from app.views import auth , students, teacher,admin

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",  # Common React dev server port
    "http://localhost:5173",  # Add this line for Vite
    "http://localhost:8000",
    "http://10.10.3.71",  # Add this line for your backend IP
]
# http://10.10.3.71:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# app.include_router(router.router)
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(teacher.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Backend! (/docs for Swagger UI)"}


if __name__ == '__main__':

    uvicorn.run("main:app", reload=True, host="0.0.0.0")
    # uvicorn.run("main:app", reload=True)
