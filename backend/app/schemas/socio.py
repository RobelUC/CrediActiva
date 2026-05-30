import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_DNI_PATTERN = re.compile(r"^\d{8}$")


class SocioCreate(BaseModel):
    nombres: str = Field(..., min_length=2)
    apellidos: str = Field(..., min_length=2)
    dni: str = Field(..., min_length=8, max_length=8)
    email: str = Field(..., min_length=5)
    telefono: str = Field(..., min_length=9, max_length=9)
    aporte_mensual: float = Field(default=50.0, ge=0)

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor: str) -> str:
        if not _DNI_PATTERN.match(valor):
            raise ValueError("DNI debe tener 8 dígitos.")
        return valor


class SocioResponse(BaseModel):
    id_socio: str
    nombres: str
    apellidos: str
    dni: str
    email: str
    telefono: str
    aporte_mensual: float
    fecha_registro: datetime
    activo: bool = True
