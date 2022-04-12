This library works by injecting a new module in the Web3.py instance, which allows
submitting "bundles" of transactions directly to miners. This is done by also creating
a middleware which captures calls to `eth_sendBundle` and `eth_callBundle`, and sends
them to an RPC endpoint which you have specified, which corresponds to `mev-geth`. 
To apply correct headers we use OpenmevProvider which injects the correct header on post 

## Example

```python
from eth_account.signers.local import LocalAccount
from web3 import Web3, HTTPProvider
from openmev import openmev
from eth_account.account import Account
import os

ETH_ACCOUNT_SIGNATURE: LocalAccount = Account.from_key(os.environ.get("ETH_SIGNATURE_KEY"))


w3 = Web3(HTTPProvider(os.environ.get("ETH_RPC_URL")))
openmev(w3, ETH_ACCOUNT_SIGNATURE)
```

Avaliable methods:
- `w3.openmev.sendBundle` Look in `examples/bundle.py` for usage examples
- `w3.openmev.sendPrivateTransaction` Look in `examples/private_swap.py` for usage examples

# Development and testing

Export private key and rpc url as env vars
```
export ETH_SIGNATURE_KEY=<0x...>
export ETH_RPC_URL=<http...>
```

Setup pre-reqs
```
./pre-install
```

Install Openmev
```
pip3.10 install
```

Run examples
```
python3.10 examples/private_swap.py
```
