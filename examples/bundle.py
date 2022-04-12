"""
Minimal viable example of openmev usage with dynamic fee transactions.
"""

import os

from eth_account.account import Account
from eth_account.signers.local import LocalAccount
from openmev import openmev
from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound
from web3.types import TxParams
import time

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

    print(
        f"Sender account balance: {Web3.fromWei(w3.eth.get_balance(sender.address), 'ether')} ETH"
    )
    print(
        f"Receiver account balance: {Web3.fromWei(w3.eth.get_balance(receiver.address), 'ether')} ETH"
    )

    # bundle two EIP-1559 (type 2) transactions, pre-sign one of them
    # NOTE: chainId is necessary for all EIP-1559 txns
    # NOTE: nonce is required for signed txns

    nonce = w3.eth.get_transaction_count(sender.address)
    base_fee = list(dict(w3.eth.fee_history(1, 'latest'))["baseFeePerGas"])[1]
    tx1: TxParams = {
        "to": receiver.address,
        "value": Web3.toWei(0.01, "ether"),
        "gas": 25000,
        "maxFeePerGas": base_fee,
        "maxPriorityFeePerGas": w3.eth.max_priority_fee,
        "nonce": nonce,
        "chainId": 1,
        "type": 2,
        "data":"0x"
    }
    tx1_signed = sender.sign_transaction(tx1)

    tx2: TxParams = {
        "to": receiver.address,
        "value": Web3.toWei(0.01, "ether"),
        "gas": 25001,
        "maxFeePerGas": base_fee,
        "maxPriorityFeePerGas": w3.eth.max_priority_fee,
        "nonce": nonce + 1,
        "chainId": 1,
        "type": 2,
        "data":"0x"
    }

    bundle = [
        {"signed_transaction": tx1_signed.rawTransaction},
        {"signer": sender, "transaction": tx2},
    ]

    # send bundle to be executed in the next 5 blocks
    block = w3.eth.block_number

    # try:
    #     sim_result = w3.openmev.simulate(bundle, block+1, block, int(time.time() + 13))
    #     print("sim result", sim_result)
    # except Exception as e:
    #     print("sim error", e)

    results = []
    for target_block in [block + k for k in [1, 2]]:
        results.append(
            w3.openmev.send_bundle(bundle, target_block_number=target_block)
        )
        print(f"Bundle sent to miners in block {target_block}")

    # wait for all results
    results[-1].wait()
    try:
        receipt = results[-1].receipts()
        print(f"Bundle was executed in block {receipt[0].blockNumber}")
    except TransactionNotFound:
        print("Bundle was not executed")
        return

    print(
        f"Sender account balance: {Web3.fromWei(w3.eth.get_balance(sender.address), 'ether')} ETH"
    )
    print(
        f"Receiver account balance: {Web3.fromWei(w3.eth.get_balance(receiver.address), 'ether')} ETH"
    )


if __name__ == "__main__":
    main()