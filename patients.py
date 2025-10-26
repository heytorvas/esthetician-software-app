from fastapi import APIRouter, HTTPException, Query
from uuid import UUID, uuid4
from typing import List
from datetime import datetime
from schemas import PatientSchema, PatientUpdateSchema, PatientOutSchema, RecordTypeEnum, AppointmentOutSchema, BodyFormSchema, FacialFormSchema, ProceduresEnum
from constants import PATIENTS_COLLECTION, APPOINTMENTS_COLLECTION, RECORDS_COLLECTION
from commons import paginate
from database import get_database, serialize_for_mongo

db = get_database()

router = APIRouter()

@router.post("/patients", response_model=PatientOutSchema)
async def create_patient(payload: PatientSchema) -> PatientOutSchema:
    dt = datetime.now()
    patient_id = uuid4()
    data = payload.model_dump()
    data["_id"] = patient_id
    data["created_at"] = dt
    data["updated_at"] = dt

    # Serialize all data for MongoDB (UUID/datetime to string)
    mongo_data = serialize_for_mongo(data)
    await db[PATIENTS_COLLECTION].insert_one(mongo_data)

    return PatientOutSchema(**data)

@router.get("/patients", response_model=List[PatientOutSchema])
async def get_patients(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    name: str = Query(None)
) -> List[PatientOutSchema]:
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}

    patients_cursor = db[PATIENTS_COLLECTION].find(query).sort("name")
    patients_list = await patients_cursor.to_list(length=None)
    patients = [PatientOutSchema(**p) for p in patients_list]

    return paginate(patients, page, limit)

@router.get("/patients/{patient_id}", response_model=PatientOutSchema)
async def get_patient(patient_id: UUID) -> PatientOutSchema:
    patient = await db[PATIENTS_COLLECTION].find_one({"_id": serialize_for_mongo(patient_id)})
    if patient:
        return PatientOutSchema(**patient)
    raise HTTPException(status_code=404, detail="Patient not found")

@router.patch("/patients/{patient_id}", response_model=PatientOutSchema)
async def update_patient(patient_id: UUID, payload: PatientUpdateSchema) -> PatientOutSchema:
    update_data = payload.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now()
    # Serialize both filter and update for MongoDB
    updated_patient = await db[PATIENTS_COLLECTION].find_one_and_update(
        {"_id": serialize_for_mongo(patient_id)},
        {"$set": serialize_for_mongo(update_data)},
        return_document=True
    )

    if not updated_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return PatientOutSchema(**updated_patient)

@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: UUID) -> dict:
    result = await db[PATIENTS_COLLECTION].delete_one({"_id": serialize_for_mongo(patient_id)})
    if result.deleted_count == 1:
        return {"detail": "Patient deleted"}
    raise HTTPException(status_code=404, detail="Patient not found")

@router.get("/patients/{patient_id}/appointments", response_model=list[AppointmentOutSchema])
async def get_patient_appointments(patient_id: UUID, page: int = Query(1, ge=1), limit: int = Query(10, ge=1)):
    appointments_cursor = db[APPOINTMENTS_COLLECTION].find({"patient_id": serialize_for_mongo(patient_id)}).sort("appointment_date", 1)
    appointments_list = await appointments_cursor.to_list(length=None)
    appointments = [AppointmentOutSchema(**a) for a in appointments_list]
    return paginate(appointments, page, limit)

@router.post("/patients/{patient_id}/records/{record}", response_model=dict)
async def create_record(patient_id: UUID, record: RecordTypeEnum, payload: BodyFormSchema | FacialFormSchema):
    existing_record = await db[RECORDS_COLLECTION].find_one({"patient_id": serialize_for_mongo(patient_id), "record": record.value})
    if existing_record:
        raise HTTPException(status_code=409, detail=f"Record for {type.value} already exists.")

    record_id = uuid4()
    data = {
        "_id": record_id,
        "patient_id": patient_id,
        "record": record.value,
        "form": payload.model_dump(),
        "created_at": datetime.now(),
    }
    await db[RECORDS_COLLECTION].insert_one(serialize_for_mongo(data))
    return {"id": str(record_id)}

@router.get("/patients/{patient_id}/records", response_model=dict)
async def get_records(patient_id: UUID):
    records_cursor = db[RECORDS_COLLECTION].find({"patient_id": serialize_for_mongo(patient_id)})
    records = {
        "body": None,
        "facial": None
    }
    async for record in records_cursor:
        if record["record"] == "body":
            records["body"] = record["form"]
        elif record["record"] == "facial":
            records["facial"] = record["form"]
    
    return records

@router.get("/options/patients")
async def get_patient_options():
    patients_cursor = db[PATIENTS_COLLECTION].find({}, {"_id": 1, "name": 1}).sort("name")
    patients_list = await patients_cursor.to_list(length=None)
    options = [{"id": str(p["_id"]), "name": p["name"]} for p in patients_list]
    return options