from fastapi import APIRouter, HTTPException, Query
from schemas import AppointmentSchema, AppointmentOutSchema, ProceduresEnum
from uuid import uuid4
from datetime import datetime
from constants import db, APPOINTMENTS_SHEET
from commons import paginate
from patients import get_patient_by_id
import json

router = APIRouter()

@router.post("/appointments", response_model=AppointmentOutSchema)
def create_appointment(payload: AppointmentSchema):
    patient, _ = get_patient_by_id(payload.patient_id)
    if not patient:
        raise HTTPException(status_code=400, detail="Invalid patient_id")
    dt = datetime.now().isoformat()
    appointment_id = str(uuid4())
    data = payload.model_dump()
    # Remove patient_id from data JSON, store in its own column
    patient_id = str(data.pop("patient_id"))
    if "procedures" in data:
        data["procedures"] = [p.value if hasattr(p, "value") else str(p) for p in data["procedures"]]
    if "birth_date" in data and hasattr(data["birth_date"], "isoformat"):
        data["birth_date"] = data["birth_date"].isoformat()
    data["created_at"] = dt
    db.append(f"{APPOINTMENTS_SHEET}!A:C", [[appointment_id, patient_id, json.dumps(data, ensure_ascii=False)]] )
    return AppointmentOutSchema(id=appointment_id, patient_id=patient_id, **data)

@router.get("/appointments", response_model=list[AppointmentOutSchema])
def get_appointments(page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    rows = db.read(f"{APPOINTMENTS_SHEET}!A:C")
    appointments = []
    for row in rows[1:]:
        data = json.loads(row[2], encoding="utf-8")
        data["id"] = row[0]
        data["patient_id"] = row[1]
        appointments.append(AppointmentOutSchema(**data))
    return paginate(appointments, page, limit)

@router.get("/appointments/{appointment_id}", response_model=AppointmentOutSchema)
def get_appointment(appointment_id: str):
    rows = db.read(f"{APPOINTMENTS_SHEET}!A:C")
    for row in rows[1:]:
        if row[0] == appointment_id:
            data = json.loads(row[2], encoding="utf-8")
            data["id"] = row[0]
            data["patient_id"] = row[1]
            return AppointmentOutSchema(**data)

@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: str):
    rows = db.read(f"{APPOINTMENTS_SHEET}!A:F")
    for idx, row in enumerate(rows[1:], start=1):
        if row[0] == appointment_id:
            db.delete_row(APPOINTMENTS_SHEET, idx)
            return {"detail": "Appointment deleted"}
    raise HTTPException(status_code=404, detail="Appointment not found")
