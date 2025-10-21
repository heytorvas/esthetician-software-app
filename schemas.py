from typing import List
from uuid import UUID
from pydantic import BaseModel, computed_field, Field
from datetime import date, datetime
from enum import StrEnum, Enum

class ProceduresEnum(StrEnum):
    BODY = "BODY"
    FACIAL = "FACIAL"

class AppointmentSchema(BaseModel):
    patient_id: UUID
    procedures: List[ProceduresEnum]
    price: float
    signature: str


class AppointmentOutSchema(AppointmentSchema):
    id: UUID = Field(..., alias="_id")
    created_at: datetime

    class Config:
        populate_by_name = True


class GenderEnum(StrEnum):
    MALE = "male"
    FEMALE = "female"


class PatientSchema(BaseModel):
    name: str
    birth_date: date
    gender: GenderEnum
    address: str
    email: str
    phone: str = Field(..., pattern=r"^\d{11}$")
    recommendation: str


class PatientUpdateSchema(BaseModel):
    name: str | None = None
    birth_date: date | None = None
    gender: GenderEnum | None = None
    address: str | None = None
    email: str | None = None
    phone: str | None = Field(None, pattern=r"^\d{11}$")
    recommendation: str | None = None

class PatientOutSchema(PatientSchema):
    id: UUID = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

    @computed_field
    def age(self) -> int:
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

MAX_LEN = 300

class BodyFormSchema(BaseModel):
    main_complaint: str = Field(..., max_length=1000)
    signature: str = Field(...)

    epilepsy_seizure: bool = Field(...)
    regular_bowels: bool = Field(...)
    drinks_alcohol: bool = Field(...)
    pregnant: bool = Field(...)
    breastfeeding: bool = Field(...)
    smoker: bool = Field(...)

    recent_surgery: str = Field(..., max_length=MAX_LEN)
    drinks_water_frequently: str = Field(..., max_length=MAX_LEN)
    has_heart_condition: str = Field(..., max_length=MAX_LEN)
    good_sleep_quality: str = Field(..., max_length=MAX_LEN)
    exercises: str = Field(..., max_length=MAX_LEN)
    sedentary: str = Field(..., max_length=MAX_LEN)
    has_allergy: str = Field(..., max_length=MAX_LEN)
    balanced_diet: str = Field(..., max_length=MAX_LEN) 
    varicose_thrombosis_or_lesion: str = Field(..., max_length=MAX_LEN)
    any_hernia: str = Field(..., max_length=MAX_LEN)
    recent_fracture: str = Field(..., max_length=MAX_LEN) 
    cuts_or_wounds: str = Field(..., max_length=MAX_LEN)
    bone_or_muscle_degeneration: str = Field(..., max_length=MAX_LEN)
    works_or_studies: str = Field(..., max_length=MAX_LEN)
    acute_inflammation: str = Field(..., max_length=MAX_LEN)
    had_skin_cancer: str = Field(..., max_length=MAX_LEN)
    prosthesis_body_or_face: str = Field(..., max_length=MAX_LEN)
    orthopedic_problem: str = Field(..., max_length=MAX_LEN)
    uses_medication: str = Field(..., max_length=MAX_LEN)


class Hydration(str, Enum):
    DRY = "Dry"
    NORMAL = "Normal"
    DEHYDRATED = "Dehydrated"


class SkinThickness(str, Enum):
    THICK = "Thick"
    THIN = "Thin"
    VERY_THIN = "Very thin"


class Oiliness(str, Enum):
    ALIPIC = "Alipic"
    LIPIDIC = "Lipidic"
    NORMAL = "Normal"
    COMBINATION = "Combination"


class Phototype(int, Enum):
    TYPE_1 = 1
    TYPE_2 = 2
    TYPE_3 = 3
    TYPE_4 = 4
    TYPE_5 = 5
    TYPE_6 = 6


class AcneGrade(int, Enum):
    GRADE_1 = 1
    GRADE_2 = 2
    GRADE_3 = 3
    GRADE_4 = 4


class DermatologicalCondition(str, Enum):
    MILIUM = "Milium"
    COMEDONE = "Comedone"
    PAPULE = "Papule"
    PUSTULE = "Pustule"
    CYST = "Cyst"
    FOLLICULITIS = "Folliculitis"
    SCAR = "Scar"
    TELANGIECTASIA = "Telangiectasia"
    XANTHELASMA = "Xanthelasma"
    HYPERTRICHOSIS = "Hypertrichosis"
    WRINKLES = "Wrinkles"
    ACROMIA = "Acromia"
    HYPERCHROMIA = "Hyperchromia"
    FRECKLES = "Freckles"
    BLISTERS = "Blisters"
    ABSCESSES = "Abscesses"
    HYPOCHROMIA = "Hypochromia"
    NODULES = "Nodules"


class FacialFormSchema(BaseModel):
    main_complaint: str = Field(..., max_length=1000)
    signature: str = Field(...)

    epilepsy_seizure: bool = Field(...)
    regular_bowels: bool = Field(...)
    drinks_alcohol: bool = Field(...)
    pregnant: bool = Field(...)
    breastfeeding: bool = Field(...)
    smoker: bool = Field(...)

    previous_facial_treatment: str = Field(..., max_length=MAX_LEN)
    drinks_water_frequently: str = Field(..., max_length=MAX_LEN)
    consumes_alcohol: str = Field(..., max_length=MAX_LEN)
    exposes_to_sun_often: str = Field(..., max_length=MAX_LEN)
    uses_sunscreen: str = Field(..., max_length=MAX_LEN)
    good_sleep_quality: str = Field(..., max_length=MAX_LEN)
    physical_activity: str = Field(..., max_length=MAX_LEN)
    facial_creams: str = Field(..., max_length=MAX_LEN)
    medication: str = Field(..., max_length=MAX_LEN)
    allergy: str = Field(..., max_length=MAX_LEN)
    balanced_diet: str = Field(..., max_length=MAX_LEN)
    contraceptive: str = Field(..., max_length=MAX_LEN)
    acids_on_skin: str = Field(..., max_length=MAX_LEN)
    chemical_peel: str = Field(..., max_length=MAX_LEN)
    skin_cancer: str = Field(..., max_length=MAX_LEN)

    hydration: Hydration = Field(...)
    skin_thickness: SkinThickness = Field(...)
    oiliness: Oiliness = Field(...)
    phototype: Phototype = Field(...)
    acne_grade: AcneGrade = Field(...)
    conditions: List[DermatologicalCondition] = Field(...)