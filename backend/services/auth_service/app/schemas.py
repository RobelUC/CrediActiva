import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.validators import telefono_valido

_DNI = re.compile(r"^\d{8}$")


class SocioCreate(BaseModel):
    nombres: str = Field(..., min_length=2)
    apellidos: str = Field(..., min_length=2)
    dni: str = Field(..., min_length=8, max_length=8)
    email: str = Field(..., min_length=5)
    telefono: str = Field(..., min_length=9, max_length=9)
    aporte_mensual: float = Field(default=50.0, ge=0)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor: str) -> str:
        if not _DNI.match(valor):
            raise ValueError("DNI debe tener 8 dígitos.")
        if valor == "00000000":
            raise ValueError("Este DNI está reservado para el sistema.")
        return valor


class SocioUpdate(BaseModel):
    nombres: str = Field(..., min_length=2)
    apellidos: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    telefono: str = Field(..., min_length=9, max_length=9)
    aporte_mensual: float = Field(default=50.0, ge=0)
    activo: bool = True

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor: str) -> str:
        if not telefono_valido(valor):
            raise ValueError("El teléfono debe tener 9 dígitos (celular Perú).")
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


class PerfilSocioUpdate(BaseModel):
    nombres: str = Field(..., min_length=2)
    apellidos: str = Field(..., min_length=2)
    email: str = Field(..., min_length=5)
    telefono: str = Field(..., min_length=9, max_length=9)
    aporte_mensual: float = Field(default=50.0, ge=0)


class RegistroAuth(BaseModel):
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    dni: str = Field(..., min_length=8, max_length=8)
    email: EmailStr
    telefono: str = Field(..., min_length=9, max_length=9)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("dni")
    @classmethod
    def validar_dni_registro(cls, valor: str) -> str:
        if not _DNI.match(valor):
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos.")
        if valor == "00000000":
            raise ValueError("Este DNI está reservado para el sistema.")
        return valor

    @field_validator("telefono")
    @classmethod
    def validar_telefono_registro(cls, valor: str) -> str:
        if not telefono_valido(valor):
            raise ValueError("El teléfono debe tener 9 dígitos (celular Perú).")
        return valor

    @field_validator("nombres", "apellidos")
    @classmethod
    def validar_nombre(cls, valor: str) -> str:
        limpio = valor.strip()
        if not limpio.replace(" ", "").isalpha():
            raise ValueError("Solo se permiten letras y espacios.")
        return limpio


class LoginAuth(BaseModel):
    dni: str = Field(..., min_length=8, max_length=8)
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("dni")
    @classmethod
    def validar_dni_login(cls, valor: str) -> str:
        if not _DNI.match(valor):
            raise ValueError("El DNI debe tener 8 dígitos.")
        return valor


class UsuarioAuth(BaseModel):
    id: str
    dni: str
    nombres: str
    apellidos: str
    email: str
    rol: Literal["socio", "admin"]


class AuthResponse(BaseModel):
    exito: bool
    mensaje: str
    usuario: UsuarioAuth | None = None


class ConsultaDniResponse(BaseModel):
    dni: str
    nombres: str
    apellidos: str
