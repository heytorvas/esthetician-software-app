from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware
from patients import router as patients_router
from appointments import router as appointments_router

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(patients_router, tags=["patients"])
app.include_router(appointments_router, tags=["appointments"])

@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}
