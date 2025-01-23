This Python script enables automated token swaps on the Solana blockchain using the Raydium API. It includes functionality to retrieve swap quotes, construct and sign transactions, and send them to the network. Designed for seamless integration and easy customization.

For more details, see the official Raydium API documentation: https://docs.raydium.io/raydium/traders/trade-api


Requirements:
    Python 3.9+
    Solana SDKs: solders, spl.token, requests

Usage:
    Easily perform token swaps by calling perform_swap_baseIn(INPUT_MINT, OUTPUT_MINT, AMOUNT, SLIPPAGE) with your desired parameters.

