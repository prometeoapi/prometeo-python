from typing import Optional, Union
from pydantic import BaseModel
from datetime import datetime


class DocumentData(BaseModel):
    foja: Optional[str] = None
    clave_entidad_registro: str
    num_acta: str
    tomo: Optional[str] = None
    anio_reg: str
    municipio_registro: str
    libro: Optional[str] = None
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
    doc_probatorio: Union[int, str]  # Allowing for both int and str types
    fecha_nacimiento: datetime
    primer_apellido: str
    curp: str


class QueryResult(BaseModel):
    document_data: DocumentData
    personal_data: PersonalData
    pdf_url: Optional[str] = None
    pdf: Optional[object] = None
