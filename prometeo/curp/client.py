from enum import Enum
from datetime import datetime

from prometeo import base_client
from .models import QueryResult, DocumentData, PersonalData
from .exceptions import CurpError

TESTING_URL = 'https://test.curp-api.qualia.uy'
PRODUCTION_URL = 'https://api.curp-api.qualia.uy'


class Gender(Enum):
    MALE = 'H'
    FEMALE = 'M'


class State(Enum):
    AGUASCALIENTES = 'AS'
    BAJA_CALIFORNIA = 'BC'
    BAJA_CALIFORNIA_SUR = 'BS'
    CAMPECHE = 'CC'
    COAHUILA = 'CL'
    COLIMA = 'CM'
    CHIAPAS = 'CS'
    CHIHUAHUA = 'CH'
    CIUDAD_DE_MEXICO = 'DF'
    DURANGO = 'DG'
    GUANAJUATO = 'GT'
    GUERRERO = 'GR'
    HIDALGO = 'HG'
    JALISCO = 'JC'
    ESTADO_DE_MEXICO = 'MC'
    MICHOACAN = 'MN'
    MORELOS = 'MS'
    NAYARIT = 'NT'
    NUEVO_LEON = 'NL'
    OAXACA = 'OC'
    PUEBLA = 'PL'
    QUERETARO = 'QT'
    QUINTANA_ROO = 'QR'
    SAN_LUIS_POTOSI = 'SP'
    SINALOA = 'SL'
    SONORA = 'SR'
    TABASCO = 'TC'
    TAMAULIPAS = 'TS'
    TLAXCALA = 'TL'
    VERACRUZ = 'VZ'
    YUCATAN = 'YN'
    ZACATECA = 'ZS'
    NACIDO_EN_EL_EXTRANJERO = 'NE'


class CurpAPIClient(base_client.BaseClient):

    ENVIRONMENTS = {
        'testing': TESTING_URL,
        'production': PRODUCTION_URL,
    }

    def _make_result(self, response_data):
        document_data = response_data['document_data']
        personal_data = response_data['personal_data']
        return QueryResult(
            document_data=DocumentData(
                foja=document_data['foja'],
                clave_entidad_registro=document_data['claveEntidadRegistro'],
                num_acta=document_data['numActa'],
                tomo=document_data['tomo'],
                anio_reg=document_data['anioReg'],
                municipio_registro=document_data['municipioRegistro'],
                libro=document_data['libro'],
                entidad_registro=document_data['entidadRegistro'],
                clave_municipio_registro=document_data['claveMunicipioRegistro'],
            ),
            personal_data=PersonalData(
                sexo=personal_data['sexo'],
                entidad=personal_data['entidad'],
                nacionalidad=personal_data['nacionalidad'],
                status_curp=personal_data['statusCurp'],
                nombres=personal_data['nombres'],
                segundo_apellido=personal_data['segundoApellido'],
                clave_entidad=personal_data['claveEntidad'],
                doc_probatorio=personal_data['docProbatorio'],
                fecha_nacimiento=datetime.strptime(
                    personal_data['fechaNacimiento'], "%d/%m/%Y"
                ),
                primer_apellido=personal_data['primerApellido'],
                curp=personal_data['curp'],
            ),
        )

    def query(self, curp):
        response = self.call_api('POST', '/query', data={
            'curp': curp,
        })
        if response['errors'] is not None:
            raise CurpError(response['errors']['detail'])
        return self._make_result(response['data'])

    def reverse_query(
            self, state, birthdate, name, first_surname, last_surname, gender
    ):
        response = self.call_api('POST', '/reverse-query', data={
            'state': state.value,
            'birthdate': birthdate.strftime('%d/%m/%Y'),
            'name': name,
            'first_surname': first_surname,
            'last_surname': last_surname,
            'gender': gender.value,
        })
        if response['errors'] is not None:
            raise CurpError(response['errors']['detail'])
        return self._make_result(response['data'])