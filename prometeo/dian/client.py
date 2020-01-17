from enum import Enum
from datetime import datetime

from prometeo import exceptions, base_client, base_session
from .models import (
    CompanyInfo, Member, Representative, Name, Accountant, CapitalComposition, Location,
    Balance, RentDeclaration, Field, VATDeclaration, Numeration, NumerationRange,
    Retentions,
)

TESTING_URL = 'https://test.dian-api.qualia.uy'
PRODUCTION_URL = 'https://api.dian-api.qualia.uy'


class NumerationType(Enum):
    Authorization = 'authorization'
    Habilitation = 'habilitation'
    Inhabilitation = 'inhabilitation'


class Periodicity(Enum):
    QUARTERLY = 'q'
    BIMONTHLY = 'b'


class QuarterlyPeriod(Enum):
    JANUARY_APRIL = 1
    MAY_AUGUST = 2
    SEPTEMBER_DECEMBER = 3


class BimonthlyPeriod(Enum):
    JANUARY_FEBRUARY = 1
    MARCH_APRIL = 2
    MAY_JUNE = 3
    JULY_AUGUST = 4
    SEPTEMBER_OCTOBER = 5
    NOVEMBER_DECEMBER = 6


class MonthlyPeriod(Enum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


class DocumentType(Enum):
    """
    Document types used for :meth:`DianAPIClient.login`
    """
    TARJETA_IDENTIDAD = '12'
    CEDULA_CIUDADANIA = '13'
    CERTIFICADO_REGISTRADURIA = '14'
    TARJETA_EXTRANJERIA = '21'
    CEDULA_EXTRANJERIA = '22'
    PASAPORTE = '41'
    DOCUMENTO_IDENTIFICACION_EXTRANJERO = '42'
    SIN_IDENTIFICACION_EXTRANJERO = '43'
    DOCUMENTO_IDENTIFICACION_EXTRANJERO_PERSONA_JURIDICA = '44'
    CARNE_DIPLOMATICO = '46'


class Session(base_session.BaseSession):

    def get_company_info(self):
        """
        Get information about the company or person (form 001).

        :rtype: :class:`~prometeo.dian.models.CompanyInfo`
        """
        return self._client.get_company_info(self._session_key)

    def get_balances(self):
        """
        Get balances.

        :rtype: list of :class:`~prometeo.dian.models.Balance`
        """
        return self._client.get_balances(self._session_key)

    def get_rent_declaration(self, year):
        """
        Get rent declaration information (form 110 for companies and 210 for persons)

        :param year: Year of the declaration
        :type year: int

        :rtype: :class:`~prometeo.dian.models.RentDeclaration`
        """
        return self._client.get_rent_declaration(self._session_key, year)

    def get_vat_declaration(self, year, periodicity, period):
        """
        Get VAT declaration information (form 300)

        :param year: Year of the declaration
        :type year: int

        :param periodicity: Periodicity, either quarterly or bimonthly
        :type periodicity: :class:`Periodicity`

        :param period: Period of the declaration
        :type period: int

        :rtype: :class:`~prometeo.dian.models.VATDeclaration`
        """
        return self._client.get_vat_declaration(
            self._session_key, year, periodicity, period
        )

    def get_numeration(self, type, date_start, date_end):
        """
        Get bill numeration (form 1876)

        :param type: The type of numeration request to get
        :type type: :class:`NumerationType`

        :param date_start: Start date to filter
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End date to filter
        :type date_end: :class:`~datetime.datetime`

        :rtype: List of :class:`~prometeo.dian.models.Numeration`
        """
        return self._client.get_numeration(
            self._session_key, type, date_start, date_end
        )

    def get_retentions(self, year, period):
        """
        Get retentions information (form 350)

        :param year: Year of the retention
        :type year: int

        :param period: Period of the retention
        :type period: int

        :rtype: List of :class:`~prometeo.dian.models.Retentions`
        """
        return self._client.get_retentions(self._session_key, year, period)


class DianAPIClient(base_client.BaseClient):
    """
    API Client for DIAN API
    """

    ENVIRONMENTS = {
        'testing': TESTING_URL,
        'production': PRODUCTION_URL,
    }

    session_class = Session

    def login(self, document_type, document, password, nit=None):
        """
        Log in to DIAN

        :param document_type: The type of document for the ``document`` argument.
        :type document_type: :class:`DocumentType`

        :param document: The document of the person
        :type document: str

        :param password: The password used to log in
        :type password: str

        :param nit: The NIT of the company (used only when logging in as a company)
        :type nit: str

        :rtype: :class:`Session`
        """
        data = {
            'provider': 'dian',
            'document_type': document_type.value,
            'document': document,
            'password': password,
        }
        if nit is not None:
            data['nit'] = nit
        response = self.call_api('POST', '/login/', data=data)
        if response['status'] == 'logged_in':
            return Session(self, response['status'], response['session_key'])
        elif response['status'] == 'wrong_credentials':
            raise exceptions.WrongCredentialsError(response['message'])
        else:
            raise exceptions.ClientError(response['message'])

    def get_company_info(self, session_key):
        data = self.call_api('GET', '/company-info/', params={
            'session_key': session_key,
        })['info']
        return CompanyInfo(
            accountant=Accountant(
                document=data['accountant']['document'],
                start_date=datetime.strptime(
                    data['accountant']['start_date'], '%d/%m/%Y'
                ),
                name=data['accountant']['name'],
                professional_card=data['accountant']['professional_card'],
            ),
            capital_composition=CapitalComposition(**data['capital_composition']),
            reason=data['reason'],
            pdf_url=data['pdf_url'],
            pdf=base_client.Download(self, data['pdf_url']),
            location=Location(**data['location']),
            name=data['name'],
            constitution_date=datetime.strptime(data['constitution_date'], '%d/%m/%Y'),
            representation=[
                Representative(
                    representation_type=representative['representation_type'],
                    start_date=datetime.strptime(
                        representative['start_date'], '%d/%m/%Y'
                    ),
                    document_type=representative['document_type'],
                    document=representative['document'],
                    name=Name(**representative['name']),
                ) for representative in data['representation']
            ],
            members=[
                Member(
                    document_type=member['document_type'],
                    document=member['document'],
                    nationality=member['nationality'],
                    name=Name(**member['name']),
                    start_date=datetime.strptime(member['start_date'], '%d/%m/%Y'),
                ) for member in data['members']
            ],
        )

    def get_balances(self, session_key):
        data = self.call_api('GET', '/balances/', params={
            'session_key': session_key,
        })
        return [
            Balance(**balance) for balance in data['balances']
        ]

    def get_rent_declaration(self, session_key, year):
        data = self.call_api('GET', '/rent/', params={
            'session_key': session_key,
            'year': year,
        })
        return RentDeclaration(
            pdf_url=data['declaration']['pdf_url'],
            pdf=base_client.Download(self, data['declaration']['pdf_url']),
            fields=[Field(**field) for field in data['declaration']['fields'].values()],
            year=data['declaration']['year'],
            form_number=data['declaration']['form_number'],
            nit=data['declaration']['nit'],
            dv=data['declaration']['dv'],
            name=Name(**data['declaration']['name']),
            reason=data['declaration']['reason'],
            direction_code=data['declaration']['direction_code'],
            economic_activity=data['declaration']['economic_activity'],
            correction_code=data['declaration']['correction_code'],
            previous_form=data['declaration']['previous_form']
        )

    def get_vat_declaration(self, session_key, year, periodicity, period):
        data = self.call_api('GET', '/vat/', params={
            'session_key': session_key,
            'year': year,
            'periodicity': periodicity.value,
            'period': period.value,
        })
        return VATDeclaration(
            pdf_url=data['declaration']['pdf_url'],
            pdf=base_client.Download(self, data['declaration']['pdf_url']),
            fields=[Field(**field) for field in data['declaration']['fields'].values()],
            year=data['declaration']['year'],
            form_number=data['declaration']['form_number'],
            nit=data['declaration']['nit'],
            dv=data['declaration']['dv'],
            name=Name(**data['declaration']['name']),
            reason=data['declaration']['reason'],
            direction_code=data['declaration']['direction_code'],
            correction_code=data['declaration']['correction_code'],
            previous_form=data['declaration']['previous_form'],
            period=data['declaration']['period'],
        )

    def get_numeration(self, session_key, type, date_start, date_end):
        data = self.call_api('GET', '/numeration/', params={
            'session_key': session_key,
            'type': type.value,
            'date_start': date_start.strftime('%d/%m/%Y'),
            'date_end': date_end.strftime('%d/%m/%Y'),
        })
        numerations = []
        for numeration in data['numeration']:
            if numeration['name']:
                name = Name(**numeration['name'])
            else:
                name = None
            numerations.append(Numeration(
                address=numeration['address'],
                country=numeration['country'],
                department=numeration['department'],
                dv=numeration['dv'],
                municipality=numeration['municipality'],
                nit=numeration['nit'],
                pdf_url=numeration['pdf_url'],
                pdf_available=numeration['pdf_available'],
                reason=numeration['reason'],
                name=name,
                ranges=[
                    NumerationRange(
                        establishment=range['establishment'],
                        from_number=range['from'],
                        to_number=range['to'],
                        mode=range['mode'],
                        prefix=range['prefix'],
                        type=range['type'],
                    ) for range in numeration['ranges']
                ]
            ))
        return numerations

    def get_retentions(self, session_key, year, period):
        data = self.call_api('GET', '/retentions/', params={
            'session_key': session_key,
            'year': year,
            'period': period.value,
        })
        return Retentions(
            pdf_url=data['retentions']['pdf_url'],
            pdf=base_client.Download(self, data['retentions']['pdf_url']),
            fields=[Field(**field) for field in data['retentions']['fields'].values()],
            year=data['retentions']['year'],
            form_number=data['retentions']['form_number'],
            nit=data['retentions']['nit'],
            reason=data['retentions']['reason'],
            direction_code=data['retentions']['direction_code'],
            period=data['retentions']['period'],
        )
