import requests
from base64 import b64decode
from solders.keypair import Keypair
from spl.token.instructions import get_associated_token_address
from solders.pubkey import Pubkey as PublicKey
from solana.rpc.api import Client
from solders.transaction import VersionedTransaction
from solders.message import to_bytes_versioned

# Constants
RPC_URL = "YOUR_RPC_URL"
OWNER = Keypair.from_base58_string("YOUR_PRIVATE_KEY")
WALLET_ADDRESS = "YOUR_PUBLIC_KEY"


def fetch_swap_quote(input_mint, output_mint, amount, slippage):
    """
    Fetches a swap quote from the Raydium API.

    :param input_mint: Mint address of the input token
    :param output_mint: Mint address of the output token
    :param amount: Amount of input tokens
    :param slippage: Allowed slippage in percentage
    :return: JSON response from the API
    """
    url = (f"https://transaction-v1.raydium.io/compute/swap-base-in?inputMint={input_mint}"
           f"&outputMint={output_mint}&amount={amount}&slippageBps={slippage * 100}&txVersion=V0")
    response = requests.get(url)
    return response.json()


def create_swap_transaction(input_mint, output_mint, amount, slippage):
    """
    Creates a raw swap transaction using the Raydium API.

    :param input_mint: Mint address of the input token
    :param output_mint: Mint address of the output token
    :param amount: Amount of input tokens
    :param slippage: Allowed slippage in percentage
    :return: VersionedTransaction object or None in case of error
    """
    url = "https://transaction-v1.raydium.io/transaction/swap-base-in"
    swap_quote = fetch_swap_quote(input_mint, output_mint, amount, slippage)

    data = {
        'computeUnitPriceMicroLamports': "600000",  # Priority fee in micro-lamports (adjust as needed for transaction speed)
        'swapResponse': swap_quote,  # Response from the Raydium API containing the swap details
        'txVersion': 'V0',  # 'V0' for versioned transactions, 'LEGACY' for legacy transactions
        'wallet': WALLET_ADDRESS,  # Public key of the user's wallet
        'wrapSol': True,  # Set to True if input token is native SOL (wrap SOL to wSOL automatically)
        'unwrapSol': True,  # Set to True if output token is native SOL (unwrap wSOL to SOL automatically)
        'inputAccount': str(get_associated_token_address(
            owner=PublicKey.from_string(WALLET_ADDRESS),  # Owner's public key
            mint=PublicKey.from_string(input_mint)  # Mint address of the input token
        )),
        'outputAccount': str(get_associated_token_address(
            owner=PublicKey.from_string(WALLET_ADDRESS),  # Owner's public key
            mint=PublicKey.from_string(output_mint)  # Mint address of the output token
        ))
    }
    try:
        response = requests.post(url, json=data).json()
        transaction_data = response['data'][0]['transaction']
        transaction_bytes = b64decode(transaction_data)
        transaction = VersionedTransaction.from_bytes(transaction_bytes)
        return transaction
    except Exception as e:
        print(f"Error while deserializing transaction data: {e}")
        return None


def send_transaction(raw_transaction):
    """
    Signs and sends a transaction to the Solana blockchain.

    :param raw_transaction: Unsigned VersionedTransaction object
    :return: Transaction ID
    """
    client = Client(RPC_URL)
    signature = OWNER.sign_message(to_bytes_versioned(raw_transaction.message))
    signed_transaction = VersionedTransaction.populate(raw_transaction.message, [signature])
    tx_id = client.send_transaction(signed_transaction)
    return tx_id


def perform_swap_baseIn(input_mint, output_mint, amount, slippage=10):
    """
    Executes a token swap on Raydium.

    :param input_mint: Mint address of the input token
    :param output_mint: Mint address of the output token
    :param amount: Amount of input tokens
    :param slippage: Allowed slippage in percentage (default: 10)
    :return: Transaction ID
    """
    raw_transaction = create_swap_transaction(input_mint, output_mint, amount, slippage)
    if raw_transaction:
        tx_id = send_transaction(raw_transaction)
        print(f"Transaction successful: TXID {tx_id}")
        return tx_id
    else:
        print("Transaction creation failed.")
        return None


# Example usage
perform_swap_baseIn(
    input_mint="So11111111111111111111111111111111111111112",
    output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    amount=100000
)
