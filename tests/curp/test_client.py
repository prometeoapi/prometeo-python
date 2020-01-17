# -*- coding: utf-8 -*-
from datetime import datetime

import six
from six.moves.urllib.parse import parse_qs
import requests_mock

from prometeo.curp import exceptions, Gender, State
from tests.base_test_case import BaseTestCase


@requests_mock.Mocker()
class TestClient(BaseTestCase):

    def test_query_success(self, m):
        test_curp = 'ABCD880304HDFXNR45'
        self.mock_post_request(m, '/query', 'successful_curp')
        result = self.client.curp.query(test_curp)

        request_body = parse_qs(m.last_request.text)
        self.assertEqual(test_curp, request_body['curp'][0])
        self.assertEqual('SINALOA', result.document_data.entidad_registro)
        self.assertEqual(datetime(1988, 3, 4), result.personal_data.fecha_nacimiento)

    def test_curp_nonexistent(self, m):
        error_message = u"Estimada/o usuaria/o, la clave que " \
                        u"ingresaste no existe o no está validada."
        self.mock_post_request(m, '/query', 'inexistent_curp')

        with self.assertRaises(exceptions.CurpError) as cm:
            self.client.curp.query('ABCD123445')

        self.assertIn(error_message, cm.exception.message)

    def test_reverse_query(self, m):
        self.mock_post_request(m, '/reverse-query', 'successful_curp')

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
        self.mock_post_request(m, '/reverse-query', 'inexistent_curp')

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
        self.assertIn(error_message, cm.exception.message)

    def test_pdf_url(self, m):
        test_curp = 'ABCD880304HDFXNR45'
        self.mock_post_request(m, '/query', 'successful_curp')
        result = self.client.curp.query(test_curp)
        self.assertEqual("/pdf/50ad2ba127ae4cc384fd265e585a1f67.pdf", result.pdf_url)

    def test_download_pdf(self, m):
        test_curp = 'ABCD880304HDFXNR45'
        pdf_url = "/pdf/50ad2ba127ae4cc384fd265e585a1f67.pdf"
        pdf_content = 'pdf content'
        self.mock_post_request(m, '/query', 'successful_curp')
        m.get(pdf_url, text=pdf_content)

        result = self.client.curp.query(test_curp)
        self.assertEqual(six.ensure_binary(pdf_content), result.pdf.get_file())
