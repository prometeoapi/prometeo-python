from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class DocumentData(BaseModel):
    foja: str
    clave_entidad_registro: str
    num_acta: str
    tomo: str
    anio_reg: str
    municipio_registro: str
    libro: str
    entidad_registro: str
    clave_municipio_registro: str


class PersonalData(BaseModel):
    sexo: str
    entidad: str
    nacionalidad: str
    status_curp: str
    nombres: str
    segundo_apellido: str
    clave_entidad: str
    doc_probatorio: int
    fecha_nacimiento: datetime
    primer_apellido: str
    curp: str


class QueryResult(BaseModel):
    document_data: DocumentData
    personal_data: PersonalData
    pdf_url: str
    pdf: Optional[object]
