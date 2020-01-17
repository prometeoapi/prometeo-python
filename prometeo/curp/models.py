from collections import namedtuple


QueryResult = namedtuple('QueryResult', [
    'document_data',
    'personal_data',
    'pdf_url',
    'pdf',
])

DocumentData = namedtuple('DocumentData', {
    'foja',
    'clave_entidad_registro',
    'num_acta',
    'tomo',
    'anio_reg',
    'municipio_registro',
    'libro',
    'entidad_registro',
    'clave_municipio_registro',
})

PersonalData = namedtuple('DocumentData', [
    'sexo',
    'entidad',
    'nacionalidad',
    'status_curp',
    'nombres',
    'segundo_apellido',
    'clave_entidad',
    'doc_probatorio',
    'fecha_nacimiento',
    'primer_apellido',
    'curp',
])
