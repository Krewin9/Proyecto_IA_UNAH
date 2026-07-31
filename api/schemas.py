from typing import Optional

from pydantic import BaseModel, Field


class DatosPrestamo(BaseModel):
    loan_amnt: float = Field(
        ...,
        gt=0,
        description="Monto solicitado del préstamo"
    )

    term: str = Field(
        ...,
        description="Plazo del préstamo: 36 months o 60 months"
    )

    purpose: str = Field(
        ...,
        description="Propósito del préstamo"
    )

    annual_inc: float = Field(
        ...,
        gt=0,
        description="Ingreso anual del solicitante"
    )

    verification_status: str = Field(
        ...,
        description="Estado de verificación de ingresos"
    )

    emp_length: str = Field(
        ...,
        description="Antigüedad laboral"
    )

    home_ownership: str = Field(
        ...,
        description="Situación de vivienda"
    )

    dti: float = Field(
        ...,
        ge=0,
        description="Relación deuda-ingreso"
    )

    fico_range_low: Optional[float] = Field(
        default=None,
        ge=300,
        le=850,
        description="Puntaje crediticio aproximado"
    )

    inq_last_6mths: float = Field(
        ...,
        ge=0,
        description="Consultas crediticias en los últimos seis meses"
    )

    total_acc: float = Field(
        ...,
        ge=0,
        description="Número total de cuentas crediticias"
    )

    mort_acc: Optional[float] = Field(
        default=None,
        ge=0,
        description="Número de cuentas hipotecarias"
    )

    pub_rec: float = Field(
        ...,
        ge=0,
        description="Número de registros públicos negativos"
    )

    delinq_2yrs: float = Field(
        ...,
        ge=0,
        description="Cantidad de moras en los últimos dos años"
    )

    pub_rec_bankruptcies: Optional[float] = Field(
        default=None,
        ge=0,
        description="Número de bancarrotas registradas"
    )

class ResultadoPrediccion(BaseModel):
    codigo_riesgo: int
    riesgo: str

    