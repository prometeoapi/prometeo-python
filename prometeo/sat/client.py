from datetime import datetime
from enum import Enum

from prometeo import exceptions, base_client, base_session
from .models import (
    CFDIBill, CFDIDownloadItem, DownloadRequest as DownloadRequestModel,
    PdfFile, DownloadFile, AcknowledgementResult as AcknowledgementResultModel,
)


TESTING_URL = 'https://test.sat-api.qualia.uy'
PRODUCTION_URL = 'https://api.sat-api.qualia.uy'


class LoginScope(Enum):
    CFDI = 'cfdi'
    SIAT = 'siat'


class DownloadAction(Enum):
    BULK_DOWNLOAD = 'bulk_download'
    METADATA_DOWNLOAD = 'metadata_download'
    PDF_EXPORT = 'pdf_export'
    LIST = 'list'


class BillStatus(Enum):
    ANY = 'any'
    CANCELLED = 'cancelled'
    VALID = 'valid'


class Motive(Enum):
    ALL = 'all'
    AF = 'af'
    DE = 'de'
    CO = 'co'
    FC = 'fc'
    MONTHLY = 'monthly'


class DocumentType(Enum):
    ALL = 'all'
    CT = 'ct'
    B = 'b'
    PL = 'pl'
    XF = 'xf'
    XC = 'xc'


class Status(Enum):
    ALL = 'all'
    RECEIVED = 'received'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'


class SendType(Enum):
    ALL = 'all'
    N = 'n'
    C = 'c'


class Session(base_session.BaseSession):

    def logout(self):
        """
        Logs out of SAT. You won't be able to use this session after logout.
        """
        self._client.logout(self._session_key)

    def get_emitted_bills(self, date_start, date_end, status):
        """
        List all emitted bills in a range of dates.

        :param date_start: Start date to filter
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End date to filter
        :type date_end: :class:`~datetime.datetime`

        :param status: Status of the bills
        :type status: :class:`BillStatus`

        :rtype: List of :class:`~prometeo.sat.models.CFDIBill`
        """
        return self._client.get_emitted(
            self._session_key, date_start, date_end, status, DownloadAction.LIST
        )

    def download_emitted_bills(self, date_start, date_end, status):
        """
        Creates a request to download all the emitted bills in a range of dates.

        :param date_start: Start date to filter
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End date to filter
        :type date_end: :class:`~datetime.datetime`

        :param status: Status of the bills
        :type status: :class:`BillStatus`

        :rtype: List of :class:`~DownloadRequest`
        """
        requests = self._client.get_emitted(
            self._session_key, date_start, date_end,
            status, DownloadAction.BULK_DOWNLOAD
        )
        return [
            DownloadRequest(
                self._client,
                self._session_key,
                request.request_id,
            ) for request in requests
        ]

    def get_received_bills(self, year, month, status):
        """
        List all received bills in a range of dates.

        :param year: Year of the received bills
        :type year: int

        :param month: Month of the received bills
        :type month: int

        :param status: Status of the bills
        :type status: :class:`BillStatus`

        :rtype: List of :class:`~prometeo.sat.models.CFDIBill`
        """
        return self._client.get_received(
            self._session_key, year, month, status, DownloadAction.LIST
        )

    def download_received_bills(self, year, month, status):
        """
        Creates a request to download all the received bills in a range of dates.

        :param date_start: Start date to filter
        :type date_start: :class:`~datetime.datetime`

        :param date_end: End date to filter
        :type date_end: :class:`~datetime.datetime`

        :param status: Status of the bills
        :type status: :class:`BillStatus`

        :rtype: List of :class:`~DownloadRequest`
        """
        requests = self._client.get_received(
            self._session_key, year, month, status, DownloadAction.BULK_DOWNLOAD
        )
        return [
            DownloadRequest(
                self._client,
                self._session_key,
                request.request_id,
            ) for request in requests
        ]

    def get_downloads(self):
        """
        Gets a list of available downloads

        :rtype: List of :class:`DownloadRequest`
        """
        return [
            DownloadRequest(
                self._client,
                self._session_key,
                request.request_id,
            ) for request in self._client.get_downloads(self._session_key)
        ]

    def get_acknowledgements(
            self, year, month_start, month_end,
            motive, document_type, status, send_type
    ):
        """
        Gets a list of acknowledgements for a range of dates

        :param year: The year of the acknowledgements
        :type year: int

        :param month_start: Start month to filter
        :type month_start: int

        :param month_end: End month to filter
        :type month_end: int

        :param motive: Motive
        :type motive: :class:`Motive`

        :param document_type: Document type
        :type document_type: :class:`DocumentType`

        :param status: Status
        :type status: :class:`Status`

        :param send_type: Send type
        :type send_type: :class:`SendType`

        :rtype: List of :class:`AcknowledgementResult`
        """
        acks = self._client.get_acknowledgements(
            self._session_key, year, month_start, month_end,
            motive, document_type, status, send_type
        )
        return [
            AcknowledgementResult(self._client, self._session_key, ack) for ack in acks
        ]


class SatAPIClient(base_client.BaseClient):
    """
    API Client for SAT API
    """

    ENVIRONMENTS = {
        'testing': TESTING_URL,
        'production': PRODUCTION_URL,
    }

    session_class = Session

    def login(self, rfc, password, scope):
        """
        Log in to SAT

        :param rfc: RFC of the person to log in
        :type rfc: str

        :param password: Password used to login, also known as CIEC
        :type password: str

        :param scope: Depending on the type of information to query, use
                      ``LoginScope.CFDI`` to download bill xmls or
                      ``LoginScope.SIAT`` to download acknowledgements.
        :type scope: :class:`LoginScope`

        :rtype: :class:`Session`
        """
        response = self.call_api('POST', '/login/', data={
            'provider': 'sat',
            'rfc': rfc,
            'password': password,
            'scope': scope.value,
        })
        if response['status'] == 'logged_in':
            return Session(self, response['status'], response['session_key'])
        elif response['status'] == 'wrong_credentials':
            raise exceptions.WrongCredentialsError(response['message'])
        else:
            raise exceptions.ClientError(response['message'])

    def logout(self, session_key):
        self.call_api('GET', '/logout/', params={
            'session_key': session_key,
        })

    def _handle_bill_parsing(self, action, data):
        if action == DownloadAction.LIST:
            return [
                CFDIBill(
                    id=bill['id'],
                    emitter_rfc=bill['emitter_rfc'],
                    emitter_reason=bill['emitter_reason'],
                    receiver_rfc=bill['receiver_rfc'],
                    receiver_reason=bill['receiver_reason'],
                    emitted_date=datetime.strptime(
                        bill['emitted_date'], '%Y-%m-%dT%H:%M:%S'
                    ),
                    certification_date=datetime.strptime(
                        bill['certification_date'], '%Y-%m-%dT%H:%M:%S'
                    ),
                    certification_pac=bill['certification_pac'],
                    total_value=bill['total_value'],
                    effect=bill['effect'],
                    status=BillStatus(bill['status']),
                ) for bill in data
            ]
        elif action == DownloadAction.BULK_DOWNLOAD:
            return [
                DownloadRequestModel(request_id=request['request_id'])
                for request in data
            ]
        elif action == DownloadAction.METADATA_DOWNLOAD:
            return [
                DownloadRequestModel(request_id=request['request_id'])
                for request in data
            ]
        elif action == DownloadAction.PDF_EXPORT:
            return [
                PdfFile(pdf_url=download['pdf_url'])
                for download in data
            ]

    def get_emitted(self, session_key, date_start, date_end, status, action):
        data = self.call_api('GET', '/cfdi/emitted/', params={
            'session_key': session_key,
            'date_start': date_start.strftime('%d/%m/%Y'),
            'date_end': date_end.strftime('%d/%m/%Y'),
            'status': status.value,
            'action': action.value,
        })
        return self._handle_bill_parsing(action, data['emitted'])

    def download_emitted(self, session_key, bill_id):
        data = self.call_api('GET', '/cfdi/emitted/{}/'.format(bill_id), params={
            'session_key': session_key,
        })
        return DownloadFile(**data['download'])

    def get_received(self, session_key, year, month, status, action):
        data = self.call_api('GET', '/cfdi/received/', params={
            'session_key': session_key,
            'year': year,
            'month': month,
            'status': status.value,
            'action': action.value,
        })
        return self._handle_bill_parsing(action, data['received'])

    def download_received(self, session_key, bill_id):
        data = self.call_api('GET', '/cfdi/received/{}/'.format(bill_id), params={
            'session_key': session_key,
        })
        return DownloadFile(**data['download'])

    def get_downloads(self, session_key):
        data = self.call_api('GET', '/cfdi/download/', params={
            'session_key': session_key,
        })
        return [
            CFDIDownloadItem(**item) for item in data['downloads']
        ]

    def get_download(self, session_key, request_id):
        data = self.call_api('GET', '/cfdi/download/{}/'.format(request_id), params={
            'session_key': session_key,
        })
        return DownloadFile(**data['download'])

    def get_acknowledgements(
            self, session_key, year, month_start, month_end,
            motive, document_type, status, send_type
    ):
        data = self.call_api('GET', '/ccee/acknowledgment/', params={
            'session_key': session_key,
            'year': year,
            'month_start': month_start,
            'month_end': month_end,
            'motive': motive.value,
            'document_type': document_type.value,
            'status': status.value,
            'send_type': send_type.value,
        })
        return [
            AcknowledgementResultModel(**result) for result in data['results']
        ]

    def download_acknowledgement(self, session_key, ack_id):
        data = self.call_api('GET', '/ccee/acknowledgment/{}/'.format(ack_id), params={
            'session_key': session_key,
        })
        return DownloadFile(**data['download'])


class AcknowledgementResult(object):
    """
    Info on an acknowledgement, returned by :meth:`Session.get_acknowledgements`
    """

    def __init__(self, client, session_key, data):
        self._client = client
        self._session_key = session_key
        self.id = data.id
        self.period = data.period
        self.motive = data.motive
        self.document_type = data.document_type
        self.send_type = data.send_type
        self.file_name = data.file_name
        self.reception_date = data.reception_date
        self.status = data.status

    def get_download(self):
        """
        Download the acknowledgement data

        :rtype: :class:`Download`
        """
        download = self._client.download_acknowledgement(self._session_key, self.id)
        return base_client.Download(self._client, download.download_url)


class DownloadRequest(object):
    """
    A request for bulk downloading of bills.
    """
    def __init__(self, client, session_key, request_id):
        self._download = None
        self._client = client
        self._session_key = session_key
        self.request_id = request_id

    def get_download(self):
        """
        Download the generated zip file with all the xmls

        :rtype: :class:`Download`
        """
        if self._download is None:
            download = self._client.get_download(self._session_key, self.request_id)
            self._download = base_client.Download(self._client, download.download_url)
        return self._download

    def is_ready(self):
        """
        Check if the request is ready to download.

        :rtype: bool
        """
        try:
            self.get_download()
            return True
        except exceptions.NotFoundError:
            return False
