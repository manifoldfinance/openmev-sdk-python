from typing import Callable
from web3 import Web3
from web3.middleware import Middleware
from web3.types import RPCEndpoint, RPCResponse
from typing import Any
from .provider import OpenmevProvider

OPENMEV_METHODS = [
    "eth_sendBundle",
    "eth_callBundle",
    "eth_sendRawTransaction",
    "eth_cancelRawTransaction",
]


def construct_openmev_middleware(
    openmev_provider: OpenmevProvider,
) -> Middleware:
    """Captures Openmevs RPC requests and sends them to the Openmevs endpoint
    while also injecting the required authorization headers
    Keyword arguments:
    openmev_provider -- An HTTP provider instantiated with any authorization headers
    required
    """

    def openmev_middleware(
        make_request: Callable[[RPCEndpoint, Any], Any], w3: Web3
    ) -> Callable[[RPCEndpoint, Any], RPCResponse]:
        def middleware(method: RPCEndpoint, params: Any) -> RPCResponse:
            if method not in OPENMEV_METHODS:
                return make_request(method, params)
            else:
                # otherwise intercept it and POST it
                return openmev_provider.make_request(method, params)

        return middleware

    return openmev_middleware