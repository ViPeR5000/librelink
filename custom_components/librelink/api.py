""" I used the https://libreview-unofficial.stoplight.io/docs/libreview-unofficial/ as a starting point to use the Abbot Libreview API"""


from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout
from .const import LOGIN_URL, CONNECTION_URL, PRODUCT, VERSION_APP, APPLICATION

import logging


_LOGGER = logging.getLogger(__name__)


################################################################
#          """API used for all data except login """    #
################################################################


class LibreLinkApiClient:
    def __init__(self, token: str, base_url:str, session: aiohttp.ClientSession) -> None:
        """Sample API Client."""
        self._token = token
        self._session = session
        self.connection_url = base_url + CONNECTION_URL

    async def async_get_data(self) -> any:
        """Get data from the API."""
        APIreponse = await api_wrapper(
            self._session,
            method="get",
            url= self.connection_url,
            headers={
                "product": PRODUCT,
                "version": VERSION_APP,
                "Application": APPLICATION,
                "Authorization": "Bearer " + self._token,
            },
            data={},
        )


        _LOGGER.debug(
            "Array size : %s",
            len(APIreponse["data"]),
        )
        _LOGGER.debug(
            "API Response : %s",
            APIreponse,
        )

        return APIreponse





class LibreLinkApiLogin:
    def __init__(
        self, username: str, password: str, base_url: str, session: aiohttp.ClientSession
    ) -> None:
        """Sample API Client."""
        self._username = username
        self._password = password
        self.login_url = base_url + LOGIN_URL
        self._session = session

    async def async_get_token(self) -> any:
        """Get token from the API."""
        reponseLogin = await api_wrapper(
            self._session,
            method="post",
            url=self.login_url,
            headers={
                "product": PRODUCT,
                "version": VERSION_APP,
                "Application": APPLICATION,
            },
            data={"email": self._username, "password": self._password},
        )
        #        print (reponseLogin["data"]["authTicket"]["token"])
        monToken = reponseLogin["data"]["authTicket"]["token"]

        _LOGGER.debug(
            "Token : '%s''",
            monToken,
        )
        return monToken


################################################################
#            """Utilitises """               #
################################################################


@staticmethod
async def api_wrapper(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    data: dict | None = None,
    headers: dict | None = None,
) -> any:
    """Get information from the API."""
    try:
        async with async_timeout.timeout(10):
            response = await session.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
            )
            if response.status in (401, 403):
                raise LibreLinkApiAuthenticationError(
                    "Invalid credentials",
                )
            response.raise_for_status()
            #
            return await response.json()

    except asyncio.TimeoutError as exception:
        raise LibreLinkApiCommunicationError(
            "Timeout error fetching information",
        ) from exception
    except (aiohttp.ClientError, socket.gaierror) as exception:
        raise LibreLinkApiCommunicationError(
            "Error fetching information",
        ) from exception
    except Exception as exception:  # pylint: disable=broad-except
        raise LibreLinkApiError("Something really wrong happened!") from exception


class LibreLinkApiError(Exception):
    """Exception to indicate a general API error."""


class LibreLinkApiCommunicationError(LibreLinkApiError):
    """Exception to indicate a communication error."""


class LibreLinkApiAuthenticationError(LibreLinkApiError):
    """Exception to indicate an authentication error."""
