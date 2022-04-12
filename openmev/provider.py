import logging
import os
from typing import Any, Union, Optional

from eth_account import Account, messages
from eth_account.signers.local import LocalAccount
from eth_typing import URI
from web3 import HTTPProvider
from web3._utils.request import make_post_request
from web3.types import RPCEndpoint, RPCResponse
from web3 import Web3

logging.basicConfig(level=logging.DEBUG)

def get_default_endpoint() -> URI:
    return URI(
        os.environ.get("OPENMEV_HTTP_PROVIDER_URI", "https://api.sushirelay.com/v1")
    )


class OpenmevProvider(HTTPProvider):
    logger = logging.getLogger("web3.providers.OpenmevProvider")

    def __init__(
        self,
        signature_account: LocalAccount,
        endpoint_uri: Optional[Union[URI, str]] = None,
        request_kwargs: Optional[Any] = None,
        session: Optional[Any] = None,
    ):
        _endpoint_uri = endpoint_uri or get_default_endpoint()
        super().__init__(_endpoint_uri, request_kwargs, session)
        self.signature_account = signature_account

    def make_request(self, method: RPCEndpoint, params: Any) -> RPCResponse:
        self.logger.debug(
            "Making request HTTP. URI: %s, Method: %s", self.endpoint_uri, method
        )
        request_data = self.encode_rpc_request(method, params)

        message = messages.encode_defunct(
            text=Web3.keccak(text=request_data.decode("utf-8")).hex()
        )
        signed_message = Account.sign_message(
            message, private_key=self.signature_account.privateKey.hex()
        )

        headers = self.get_request_headers() | {
            "X-Openmev-Signature": f"{self.signature_account.address}:{signed_message.signature.hex()}"
        }

        raw_response = make_post_request(
            self.endpoint_uri, request_data, headers=headers, timeout=20
        )
        response = self.decode_rpc_response(raw_response)
        self.logger.debug(
            "Getting response HTTP. URI: %s, " "Method: %s, Response: %s",
            self.endpoint_uri,
            method,
            response,
        )
        return response