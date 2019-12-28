# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

from six.moves.urllib.parse import parse_qs
import requests_mock

from prometeo import Client
from prometeo.curp import exceptions, Gender, State


CURP_DATA = {
    "document_data": {
        "foja": "",
        "claveEntidadRegistro": "25",
        "numActa": "00064",
        "tomo": "",
        "anioReg": "1988",
        "municipioRegistro": "GUASAVE",
        "libro": "0001",
        "entidadRegistro": "SINALOA",
        "claveMunicipioRegistro": "011"
    },
    "personal_data": {
        "sexo": "HOMBRE",
        "entidad": "DISTRITO FEDERAL",
        "nacionalidad": "MEXICO",
        "statusCurp": "RCN",
        "nombres": "JOHN",
        "segundoApellido": "PONCE",
        "claveEntidad": "DF",
        "docProbatorio": 1,
        "fechaNacimiento": "04/03/1988",
        "primerApellido": "DOE",
        "curp": 'ABCD880304HDFXNR45',
    }
}


@requests_mock.Mocker()
class TestClient(unittest.TestCase):

    def setUp(self):
        self.client = Client('test_key')

    def test_query_success(self, m):
        test_curp = 'ABCD880304HDFXNR45'
        m.post('/query', json={
            "errors": None,
            "data": CURP_DATA,
        })

        result = self.client.curp.query(test_curp)

        request_body = parse_qs(m.last_request.text)
        self.assertEqual(test_curp, request_body['curp'][0])
        self.assertEqual('SINALOA', result.document_data.entidad_registro)
        self.assertEqual(datetime(1988, 3, 4), result.personal_data.fecha_nacimiento)

    def test_curp_nonexistent(self, m):
        error_message = u"Estimada/o usuaria/o, la clave que " \
                        u"ingresaste no existe o no está validada."
        m.post('/query', json={
            "data": None,
            "errors": {
                "code": "180001",
                "detail": error_message,
            }
        })

        with self.assertRaises(exceptions.CurpError) as cm:
            self.client.curp.query('ABCD123445')

        self.assertEqual(error_message, cm.exception.message)

    def test_reverse_query(self, m):
        m.post('/reverse-query', json={
            "errors": None,
            "data": CURP_DATA,
        })

        state = State.SINALOA
        birthdate = datetime(1988, 3, 4)
        name = 'JOHN'
        first_surname = 'DOE'
        last_surname = 'PONCE'
        gender = Gender.MALE
        result = self.client.curp.reverse_query(
            state, birthdate, name, first_surname, last_surname, gender
        )

        request_body = parse_qs(m.last_request.text)
        self.assertEqual('SL', request_body['state'][0])
        self.assertEqual('04/03/1988', request_body['birthdate'][0])
        self.assertEqual(name, request_body['name'][0])
        self.assertEqual(first_surname, request_body['first_surname'][0])
        self.assertEqual(last_surname, request_body['last_surname'][0])
        self.assertEqual('H', request_body['gender'][0])

        self.assertEqual('SINALOA', result.document_data.entidad_registro)
        self.assertEqual(datetime(1988, 3, 4), result.personal_data.fecha_nacimiento)

    def test_reverse_query_no_result(self, m):
        error_message = u"Estimada/o usuaria/o, la clave que " \
                        u"ingresaste no existe o no está validada."
        m.post('/reverse-query', json={
            "data": None,
            "errors": {
                "code": "180001",
                "detail": error_message,
            }
        })

        state = State.SINALOA
        birthdate = datetime(1988, 3, 4)
        name = 'JOHN'
        first_surname = 'DOE'
        last_surname = 'PONCE'
        gender = Gender.MALE
        with self.assertRaises(exceptions.CurpError) as cm:
            self.client.curp.reverse_query(
                state, birthdate, name, first_surname, last_surname, gender
            )
        self.assertEqual(error_message, cm.exception.message)
