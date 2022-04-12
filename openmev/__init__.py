from typing import Union, Optional

from eth_account.signers.local import LocalAccount
from eth_keys.datatypes import PrivateKey
from web3 import Web3
from web3._utils.module import attach_modules

from .middleware import construct_openmev_middleware
from .openmev import Openmev
from .provider import OpenmevProvider
from eth_typing import URI

DEFAULT_OPENMEV_RELAY = "https://api.sushirelay.com/v1"


def openmev(
    w3: Web3,
    signature_account: LocalAccount,
    endpoint_uri: Optional[Union[URI, str]] = None,
):
    """
    Injects the openmev module and middleware to w3.
    """

    openmev_provider = OpenmevProvider(signature_account, endpoint_uri)
    mev_middleware = construct_openmev_middleware(openmev_provider)
    w3.middleware_onion.add(mev_middleware)

    # attach modules to add the new namespace commands
    attach_modules(w3, {"openmev": (Openmev,)})