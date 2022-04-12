"""
Minimal viable example of openmev private swap.
"""

import os

from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from openmev import openmev
from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound
from web3.types import TxParams
import eth_abi
import time

SUSHI_ROUTER = '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'
WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

def env(key: str) -> str:
    return os.environ.get(key)


def main() -> None:
    # account to send the transfer and sign transactions
    sender: LocalAccount = Account.from_key(env("ETH_SIGNATURE_KEY"))
    # account to receive the transfer
    receiver: LocalAccount = Account.from_key(env("ETH_SIGNATURE_KEY"))
    # account to establish openmev reputation
    # NOTE: it should not store funds
    signature: LocalAccount = Account.from_key(env("ETH_SIGNATURE_KEY"))

    w3 = Web3(HTTPProvider(env("ETH_RPC_URL")))
    openmev(w3, signature)

    nonce = w3.eth.get_transaction_count(sender.address)
    base_fee = list(dict(w3.eth.fee_history(1, 'latest'))["baseFeePerGas"])[1]
    
    amountOutMin = 10000000
    path = list([WETH,USDC])
    to = receiver.address
    deadline = int(time.time() + 120)
    abiEncoded = eth_abi.encode_abi(['uint', 'address[]', 'address', 'uint'], [amountOutMin, path, to, deadline])
    funcSelector = 'swapExactETHForTokens(uint,address[],address,uint)'
    callHash = w3.sha3(text=funcSelector)
    callHashAbr = callHash[0:4].hex()
    encodedCall = callHashAbr + abiEncoded.hex()
    
    tx1: TxParams = {
        "to": SUSHI_ROUTER,
        "value": Web3.toWei(0.1, "ether"),
        "gas": 150000,
        "maxFeePerGas": base_fee,
        "maxPriorityFeePerGas": w3.eth.max_priority_fee,
        "nonce": nonce,
        "chainId": 1,
        "type": 2,
        "data": encodedCall
    }
    tx1_signed = sender.sign_transaction(tx1)

    try:
        # send private tx to be executed in the next 1 blocks
        block = w3.eth.block_number
        # print('signed tx ', tx1_signed.rawTransaction)
        send_result = w3.openmev.send_private_transaction({"signed_transaction":tx1_signed.rawTransaction}, max_block_number=block+1)
        send_result.wait()
        receipt = send_result.receipt()
        print("send private tx result", receipt)
    except Exception as e:
        print("send private tx error", e)
        

if __name__ == "__main__":
    main()