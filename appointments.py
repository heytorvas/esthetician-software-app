from fastapi import APIRouter, HTTPException, Query
from schemas import AppointmentSchema, AppointmentOutSchema
from uuid import UUID, uuid4
from datetime import datetime
from constants import APPOINTMENTS_COLLECTION, PATIENTS_COLLECTION
from commons import paginate
from database import get_database

db = get_database()

router = APIRouter()

@router.post("/appointments", response_model=AppointmentOutSchema)
async def create_appointment(payload: AppointmentSchema):
    patient = await db[PATIENTS_COLLECTION].find_one({"_id": payload.patient_id})
    if not patient:
        raise HTTPException(status_code=400, detail="Invalid patient_id")

    appointment_id = uuid4()
    data = payload.model_dump()
    data["_id"] = appointment_id
    data["created_at"] = datetime.now()

    if "procedures" in data:
        data["procedures"] = [p.value if hasattr(p, "value") else str(p) for p in data["procedures"]]

    await db[APPOINTMENTS_COLLECTION].insert_one(data)

    return AppointmentOutSchema(**data)

@router.get("/appointments", response_model=list[AppointmentOutSchema])
async def get_appointments(page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    appointments_cursor = db[APPOINTMENTS_COLLECTION].find()
    appointments_list = await appointments_cursor.to_list(length=None)
    appointments = [AppointmentOutSchema(**a) for a in appointments_list]
    return paginate(appointments, page, limit)

@router.get("/appointments/{appointment_id}", response_model=AppointmentOutSchema)
async def get_appointment(appointment_id: UUID):
    appointment = await db[APPOINTMENTS_COLLECTION].find_one({"_id": appointment_id})
    if appointment:
        return AppointmentOutSchema(**appointment)
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: UUID):
    result = await db[APPOINTMENTS_COLLECTION].delete_one({"_id": appointment_id})
    if result.deleted_count == 1:
        return {"detail": "Appointment deleted"}
    raise HTTPException(status_code=404, detail="Appointment not found")
