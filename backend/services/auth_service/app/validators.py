"""Validadores de negocio — DNI peruano, reservados, etc."""

import re

_DNI_DIGITOS = re.compile(r"^\d{8}$")
_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_TELEFONO = re.compile(r"^\d{9}$")
_DNI_COEF = (3, 2, 7, 6, 5, 4, 3, 2)

DNI_RESERVADOS = frozenset({"00000000"})


def dni_peruano_valido(dni: str) -> bool:
    """DNI de 8 dígitos con dígito verificador (algoritmo estándar Perú)."""
    if not _DNI_DIGITOS.match(dni):
        return False
    if dni in DNI_RESERVADOS or len(set(dni)) == 1:
        return False
    suma = sum(int(dni[i]) * _DNI_COEF[i] for i in range(7))
    resto = suma % 11
    digito = 11 - resto
    if digito >= 10:
        digito -= 10
    return int(dni[7]) == digito


def email_valido(email: str) -> bool:
    return bool(_EMAIL.match(email.strip()))


def telefono_valido(telefono: str) -> bool:
    return bool(_TELEFONO.match(telefono))
