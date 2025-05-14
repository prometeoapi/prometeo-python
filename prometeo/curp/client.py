from enum import Enum
from datetime import datetime

from prometeo import base_client, utils
from .models import QueryResult, DocumentData, PersonalData
from .exceptions import CurpError

PRODUCTION_URL = "https://identity.prometeoapi.net"
SANDBOX_URL = "https://identity.sandbox.prometeoapi.com"


class Gender(Enum):
    """A person's gender"""

    MALE = "H"
    FEMALE = "M"


class State(Enum):
    """
    The state a person is registered
    """

    AGUASCALIENTES = "AS"
    BAJA_CALIFORNIA = "BC"
    BAJA_CALIFORNIA_SUR = "BS"
    CAMPECHE = "CC"
    COAHUILA = "CL"
    COLIMA = "CM"
    CHIAPAS = "CS"
    CHIHUAHUA = "CH"
    CIUDAD_DE_MEXICO = "DF"
    DURANGO = "DG"
    GUANAJUATO = "GT"
    GUERRERO = "GR"
    HIDALGO = "HG"
    JALISCO = "JC"
    ESTADO_DE_MEXICO = "MC"
    MICHOACAN = "MN"
    MORELOS = "MS"
    NAYARIT = "NT"
    NUEVO_LEON = "NL"
    OAXACA = "OC"
    PUEBLA = "PL"
    QUERETARO = "QT"
    QUINTANA_ROO = "QR"
    SAN_LUIS_POTOSI = "SP"
    SINALOA = "SL"
    SONORA = "SR"
    TABASCO = "TC"
    TAMAULIPAS = "TS"
    TLAXCALA = "TL"
    VERACRUZ = "VZ"
    YUCATAN = "YN"
    ZACATECA = "ZS"
    NACIDO_EN_EL_EXTRANJERO = "NE"


class CurpAPIClient(base_client.BaseClient):
    """
    API Client for CURP queries
    """

    ENVIRONMENTS = {
        "production": PRODUCTION_URL,
        "sandbox": SANDBOX_URL,
    }

    def _parse_date(self, date_str):
        if not date_str:
            return None
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _make_result(self, response_data):
        document_data = response_data.get("document_data", {})
        personal_data = response_data.get("personal_data", {})
        raw_birthdate = personal_data.get("fechaNacimiento")
        return QueryResult(
            document_data=DocumentData(
                foja=document_data.get("foja"),
                clave_entidad_registro=document_data.get("claveEntidadRegistro"),
                num_acta=document_data.get("numActa"),
                tomo=document_data.get("tomo"),
                anio_reg=document_data.get("anioReg"),
                municipio_registro=document_data.get("municipioRegistro"),
                libro=document_data.get("libro"),
                entidad_registro=document_data.get("entidadRegistro"),
                clave_municipio_registro=document_data.get("claveMunicipioRegistro"),
            ),
            personal_data=PersonalData(
                sexo=personal_data.get("sexo"),
                entidad=personal_data.get("entidad"),
                nacionalidad=personal_data.get("nacionalidad"),
                status_curp=personal_data.get("statusCurp"),
                nombres=personal_data.get("nombres"),
                segundo_apellido=personal_data.get("segundoApellido"),
                clave_entidad=personal_data.get("claveEntidad"),
                doc_probatorio=personal_data.get("docProbatorio"),
                fecha_nacimiento=self._parse_date(raw_birthdate),
                primer_apellido=personal_data.get("primerApellido"),
                curp=personal_data.get("curp"),
            ),
            pdf_url=response_data.get("pdf_url", ""),
            pdf=base_client.Download(self, response_data.get("pdf_url", "")),
        )

    @utils.adapt_async_sync
    async def query(self, curp):
        """
        Find the personal data associated with a CURP

        :param curp: The CURP of the person to query
        :type curp: str

        :rtype: :class:`~prometeo.curp.models.QueryResult`
        """
        response = await self.call_api(
            "POST",
            "/query",
            data={
                "curp": curp,
            },
        )
        if response["errors"] is not None:
            raise CurpError(response["errors"]["detail"])
        return self._make_result(response["data"])

    @utils.adapt_async_sync
    async def reverse_query(
        self, state, birthdate, name, first_surname, last_surname, gender
    ):
        """
        Search for a person by their personal information.

        :param state: The state where the person is registered
        :type state: :class:`State`

        :param birthdate: The person's birthdate
        :type birthdate: :class:`~datetime.datetime`

        :param name: The person's name
        :type name: str

        :param first_surname: The person's first surname
        :type first_surname: str

        :param last_surname: The person's last surname
        :type last_surname: str

        :param gender: The person's gender
        :type gender: :class:`Gender`

        :rtype: :class:`~prometeo.curp.models.QueryResult`
        """
        response = await self.call_api(
            "POST",
            "/reverse-query",
            data={
                "state": state.value,
                "birthdate": birthdate.strftime("%d/%m/%Y"),
                "name": name,
                "first_surname": first_surname,
                "last_surname": last_surname,
                "gender": gender.value,
            },
        )
        if response["errors"] is not None:
            raise CurpError(response["errors"]["detail"])
        return self._make_result(response["data"])
