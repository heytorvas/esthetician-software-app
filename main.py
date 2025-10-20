from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware
from patients import router as patients_router
from appointments import router as appointments_router
from fastapi import Depends
from auth import get_current_user, router as auth_router


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth_router, tags=["login"])
app.include_router(patients_router, tags=["patients"], dependencies=[Depends(get_current_user)])
app.include_router(appointments_router, tags=["appointments"], dependencies=[Depends(get_current_user)])

@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}
