import time

import requests
import web3
from web3 import Web3
from settings.chains import chains, Chain

from abi.erc20 import ERC20_ABI

# Заданные сети и токены
tokens = [
    {"chain": "Ethereum", "ticker": "USDC", "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
    {"chain": "Ethereum", "ticker": "USDT", "address": "0xdac17f958d2ee523a2206206994597c13d831ec7"},
    {"chain": "Arbitrum", "ticker": "USDC", "address": "0xaf88d065e77c8cc2239327c5edb3a432268e5831"},
    {"chain": "Arbitrum", "ticker": "USDT", "address": "0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9"},
    {"chain": "Optimism", "ticker": "USDC", "address": "0x0b2c639c533813f4aa9d7837caf62653d097ff85"},
    {"chain": "Optimism", "ticker": "USDT", "address": "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58"},
    {"chain": "Avalanche", "ticker": "DAI.e", "address": "0xd586e7f844cea2f87f50152665bcbc2c279d8d70"},
    {"chain": "Avalanche", "ticker": "USDC.e", "address": "0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664"},
    {"chain": "Avalanche", "ticker": "USDT.e", "address": "0xc7198437980c041c805a1edcba50c1ce5db95118"},
    {"chain": "Avalanche", "ticker": "avDAI", "address": "0x47afa96cdc9fab46904a55a6ad4bf6660b53c38a"},
    {"chain": "Avalanche", "ticker": "avUSDC", "address": "0x46a51127c3ce23fb7ab1de06226147f446e4a857"},
    {"chain": "Avalanche", "ticker": "avUSDT", "address": "0x532e6537fea298397212f09a61e03311686f548e"},
    {"chain": "Polygon", "ticker": "USDC", "address": "0x3c499c542cef5e3811e1192ce70d8cc03d5c3359"},
    {"chain": "Polygon", "ticker": "DAI", "address": "0x8f3cf7ad23cd3cadbd9735aff958023239c6a063"},
    {"chain": "Polygon", "ticker": "USDC.e", "address": "0x2791bca1f2de4661ed88a30c99a7a9449aa84174"},
    {"chain": "Polygon", "ticker": "USDT", "address": "0xc2132d05d31c914a87c6611c10748aeb04b58e8f"},
    {"chain": "BSC", "ticker": "USDC", "address": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d"},
    {"chain": "BSC", "ticker": "USDT", "address": "0x55d398326f99059fF775485246999027B3197955"},
]


# Функция для отправки запроса и анализа результата
def make_request_with_retries(url, params, retries=5, delay=10):
    for attempt in range(retries):
        response = requests.post(url, json=params)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:  # Too Many Requests
            print(f"Received 429 Too Many Requests. Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            response.raise_for_status()  # Если другой статус, просто выбрасываем исключение
    raise Exception(f"Failed to get a successful response after {retries} attempts")

# Функция для отправки запроса и анализа результата
def check_swap_route(token_in: dict, chain_in: Chain, token_out: dict, chain_out: Chain, amount: int = 1000):
    w3_in = Web3(Web3.HTTPProvider(chain_in.rpc))
    checksum_token_in = w3_in.to_checksum_address(token_in["address"])
    token_in_contract = w3_in.eth.contract(address=checksum_token_in, abi=ERC20_ABI)
    decimals_in = token_in_contract.functions.decimals().call()

    w3_out = Web3(Web3.HTTPProvider(chain_out.rpc))
    checksum_token_out = w3_in.to_checksum_address(token_out["address"])
    token_out_contract = w3_out.eth.contract(address=checksum_token_out, abi=ERC20_ABI)
    decimals_out = token_out_contract.functions.decimals().call()

    # Масштабирование amountIn с учетом decimals
    amount_in_scaled = amount * (10 ** decimals_in)

    url = "https://api.crosscurve.fi/routing/scan"
    params = {
        "params": {
            "chainIdOut": chain_out.id,
            "tokenOut": token_out["address"],
            "chainIdIn": chain_in.id,
            "amountIn": str(amount_in_scaled),
            "tokenIn": token_in["address"]
        },
        "slippage": 0.1
    }

    response = make_request_with_retries(url, params)

    if response.status_code == 200:
        data = response.json()
        if data and "amountOut" in data[0]:
            amount_out_raw = float(data[0]["amountOut"])
            amount_out = amount_out_raw / (10 ** decimals_out)  # Масштабируем amountOut обратно

            if amount_out >= amount:
                return {
                    "from_token": token_in["ticker"],
                    "from_chain": chain_in.name,
                    "to_token": token_out["ticker"],
                    "to_chain": chain_out.name,
                    "amount_in": amount,
                    "amount_out": amount_out
                }
            return f"{chain_in.name} {token_in['ticker']} -> {chain_out.name} {token_out['ticker']} | {amount} : {amount_out}"
    return 0

# Основной цикл для перебора всех комбинаций
for token_in in tokens:
    chain_in = chains[token_in["chain"].lower()]  # Получаем объект Chain для входного токена
    for token_out in tokens:
        chain_out = chains[token_out["chain"].lower()]  # Получаем объект Chain для выходного токена
        if token_in != token_out or chain_in != chain_out:  # Проверка чтобы не делать обмен одного токена на него же
            result = check_swap_route(token_in, chain_in, token_out, chain_out)
            if result:
                # Проверяем, содержит ли результат ключи 'from_token' и 'from_chain'
                if isinstance(result, dict) and 'from_token' in result and 'from_chain' in result:
                    print(
                        f"Swap {result['from_token']} on {result['from_chain']} to {result['to_token']} on {result['to_chain']}: "
                        f"Amount In = {result['amount_in']}, Amount Out = {result['amount_out']:.6f}")
                else:
                    print(result)

# Основной цикл для перебора всех комбинаций
for token_in in tokens:
    chain_in = chains[token_in["chain"].lower()]  # Получаем объект Chain для входного токена
    for token_out in tokens:
        chain_out = chains[token_out["chain"].lower()]  # Получаем объект Chain для выходного токена
        if token_in != token_out or chain_in != chain_out:  # Проверка чтобы не делать обмен одного токена на него же
            result = check_swap_route(token_in, chain_in, token_out, chain_out)
            if result:
                # Проверяем, содержит ли результат ключи 'from_token' и 'from_chain'
                if 'from_token' in result and 'from_chain' in result:
                    print(
                        f"Swap {result['from_token']} on {result['from_chain']} to {result['to_token']} on {result['to_chain']}: "
                        f"Amount In = {result['amount_in']}, Amount Out = {result['amount_out']:.6f}")
                else:
                    print(result)