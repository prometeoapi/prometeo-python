from collections import namedtuple


CFDIBill = namedtuple('CFDIBill', [
    'id',
    'emitter_rfc',
    'emitter_reason',
    'receiver_rfc',
    'receiver_reason',
    'emitted_date',
    'certification_date',
    'certification_pac',
    'total_value',
    'effect',
    'status'
])


CFDIDownloadItem = namedtuple('CFDIDownloadItem', [
    'request_id',
    'type',
    'count'
])


DownloadRequest = namedtuple('DownloadRequest', [
    'request_id'
])


PdfFile = namedtuple('PdfFile', [
    'pdf_url'
])


DownloadFile = namedtuple('DownloadFile', [
    'download_url'
])


AcknowledgementResult = namedtuple('AcknowledgementResult', [
    'id',
    'period',
    'motive',
    'document_type',
    'send_type',
    'file_name',
    'reception_date',
    'status'
])
