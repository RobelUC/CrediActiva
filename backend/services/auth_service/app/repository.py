from datetime import datetime, timezone
from typing import Any

from app.database import SessionLocal
from app.models import Socio


def _parse_fecha(valor: datetime | str) -> datetime:
    if isinstance(valor, datetime):
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _to_dict(socio: Socio, *, incluir_hash: bool = False) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id_socio": socio.id_socio,
        "nombres": socio.nombres,
        "apellidos": socio.apellidos,
        "dni": socio.dni,
        "email": socio.email,
        "telefono": socio.telefono,
        "aporte_mensual": socio.aporte_mensual,
        "fecha_registro": socio.fecha_registro,
        "activo": socio.activo,
        "rol": socio.rol or "socio",
    }
    if incluir_hash:
        data["password_hash"] = socio.password_hash
    return data


def guardar_socio(registro: dict[str, Any]) -> dict[str, Any]:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.dni == registro["dni"]).first()
        fecha = _parse_fecha(registro.get("fecha_registro", datetime.now(timezone.utc)))

        if socio:
            socio.id_socio = registro.get("id_socio", socio.id_socio)
            socio.nombres = registro["nombres"]
            socio.apellidos = registro["apellidos"]
            socio.email = registro["email"]
            socio.telefono = registro.get("telefono", socio.telefono)
            socio.aporte_mensual = round(registro.get("aporte_mensual", socio.aporte_mensual), 2)
            socio.activo = registro.get("activo", socio.activo)
            if "rol" in registro and registro["rol"]:
                socio.rol = registro["rol"]
            if "password_hash" in registro and registro["password_hash"]:
                socio.password_hash = registro["password_hash"]
        else:
            socio = Socio(
                id_socio=registro["id_socio"],
                dni=registro["dni"],
                nombres=registro["nombres"],
                apellidos=registro["apellidos"],
                email=registro["email"],
                telefono=registro.get("telefono", ""),
                aporte_mensual=round(registro.get("aporte_mensual", 50.0), 2),
                fecha_registro=fecha,
                activo=registro.get("activo", True),
                password_hash=registro.get("password_hash"),
                rol=registro.get("rol", "socio"),
            )
            db.add(socio)

        db.commit()
        db.refresh(socio)
        return _to_dict(socio)


def obtener_por_dni(dni: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.dni == dni).first()
        return _to_dict(socio) if socio else None


def obtener_por_dni_con_password(dni: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.dni == dni).first()
        return _to_dict(socio, incluir_hash=True) if socio else None


def obtener_por_email(email: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.email == email.strip().lower()).first()
        return _to_dict(socio) if socio else None


def obtener_por_id(id_socio: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.id_socio == id_socio).first()
        return _to_dict(socio) if socio else None


def listar_socios(*, solo_activos: bool = False) -> list[dict[str, Any]]:
    with SessionLocal() as db:
        query = db.query(Socio)
        if solo_activos:
            query = query.filter(Socio.activo.is_(True))
        socios = query.order_by(Socio.fecha_registro.desc()).all()
        return [_to_dict(s) for s in socios]


def actualizar_socio(id_socio: str, datos: dict[str, Any]) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.id_socio == id_socio).first()
        if not socio:
            return None

        email = datos["email"].strip().lower()
        otro = db.query(Socio).filter(Socio.email == email, Socio.id_socio != id_socio).first()
        if otro:
            raise ValueError("El correo ya está registrado en otro socio.")

        socio.nombres = datos["nombres"].strip()
        socio.apellidos = datos["apellidos"].strip()
        socio.email = email
        socio.telefono = datos["telefono"]
        socio.aporte_mensual = round(datos.get("aporte_mensual", socio.aporte_mensual), 2)
        socio.activo = datos.get("activo", socio.activo)

        db.commit()
        db.refresh(socio)
        return _to_dict(socio)


def actualizar_password_socio(id_socio: str, password_hash: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.id_socio == id_socio).first()
        if not socio:
            return None
        socio.password_hash = password_hash
        db.commit()
        db.refresh(socio)
        return _to_dict(socio)


def eliminar_socio(id_socio: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.id_socio == id_socio).first()
        if not socio:
            return None
        socio.activo = False
        db.commit()
        db.refresh(socio)
        return _to_dict(socio)


def asignar_rol_por_dni(dni: str, rol: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.dni == dni).first()
        if not socio:
            return None
        socio.rol = rol
        db.commit()
        db.refresh(socio)
        return _to_dict(socio)


def borrar_socio_permanente(id_socio: str) -> dict[str, Any] | None:
    with SessionLocal() as db:
        socio = db.query(Socio).filter(Socio.id_socio == id_socio).first()
        if not socio:
            return None
        data = _to_dict(socio)
        db.delete(socio)
        db.commit()
        return data
