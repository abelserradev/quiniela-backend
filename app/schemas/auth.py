"""Schemas para autenticación (registro, login)."""
import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegistroRequest(BaseModel):
    usuario: str = Field(..., min_length=3, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=10)

    @field_validator("usuario")
    @classmethod
    def validar_usuario(cls, v: str) -> str:
        sanitizado = re.sub(r"[^a-zA-Z0-9_]", "", v.strip())
        if len(sanitizado) < 3:
            raise ValueError("El usuario debe tener al menos 3 caracteres alfanuméricos")
        return sanitizado

    @field_validator("nombre", "apellido")
    @classmethod
    def validar_nombre_apellido(cls, v: str) -> str:
        sanitizado = re.sub(r"[<>\"'`;{}\\]", "", v.strip())
        sanitizado = re.sub(r"(?i)(script|javascript|on\w+=|data:)", "", sanitizado)
        if not sanitizado or not re.search(r"[a-zA-ZáéíóúñÑ]", sanitizado):
            raise ValueError("Solo se permiten letras y espacios")
        return sanitizado

    @field_validator("password")
    @classmethod
    def validar_password(cls, v: str) -> str:
        if len(v) < 6 or len(v) > 10:
            raise ValueError("La contraseña debe tener entre 6 y 10 caracteres")
        especiales = set("!@#$%^&*()_+-=[]{}|;':\",./<>?")
        mayus = sum(1 for c in v if c.isupper())
        minus = sum(1 for c in v if c.islower())
        num_esp = sum(1 for c in v if c in especiales)
        digitos = sum(1 for c in v if c.isdigit())
        if mayus < 1:
            raise ValueError("Debe incluir al menos una letra mayúscula")
        if num_esp < 1 or num_esp > 2:
            raise ValueError("Debe incluir uno o dos caracteres especiales")
        if minus < 1:
            raise ValueError("Debe incluir letras minúsculas")
        if mayus + minus + num_esp + digitos != len(v):
            raise ValueError("Caracteres no permitidos")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegistroResponse(BaseModel):
    mensaje: str = "usuario registrado"


class LoginResponse(BaseModel):
    mensaje: str = "sesión iniciada"
