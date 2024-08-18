import time
import requests
import logging
from web3 import Web3
from settings.chains import chains, Chain
from abi.erc20 import ERC20_ABI

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат сообщения
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        logging.FileHandler('swap_routes.log', mode='w')  # Вывод в файл
    ]
)

logger = logging.getLogger(__name__)


# Функция для получения decimals с обработкой повторных попыток
def get_decimals_with_retries(contract, retries=1, delay=1):
    for attempt in range(retries):
        try:
            return contract.functions.decimals().call()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Unexpected error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    logger.error(f"Failed to get decimals after {retries} attempts, skipping token.")
    return None


# Функция для отправки запроса и анализа результата
def make_request_with_retries(url, params, retries=1, delay=1):
    for attempt in range(retries):
        response = requests.post(url, json=params)
        if response.status_code == 200:
            return response
        elif response.status_code == 429:  # Too Many Requests
            logger.warning(f"Received 429 Too Many Requests. Retrying in {delay} seconds...")
            time.sleep(delay)
        else:
            response.raise_for_status()  # Если другой статус, просто выбрасываем исключение
    logger.error(f"Failed to get a successful response after {retries} attempts")
    raise Exception(f"Failed to get a successful response after {retries} attempts")


# Функция для отправки запроса и анализа результата
def check_swap_route(token_in: dict, chain_in: Chain, token_out: dict, chain_out: Chain, swap_only_in_plus: bool,
                     swap_plus_size: float, max_swap_loss: float, slippage: float, amount: float = 1000):
    w3_in = Web3(Web3.HTTPProvider(chain_in.rpc))
    checksum_token_in = w3_in.to_checksum_address(token_in["address"])
    token_in_contract = w3_in.eth.contract(address=checksum_token_in, abi=ERC20_ABI)
    decimals_in = get_decimals_with_retries(token_in_contract)

    if decimals_in is None:
        logger.warning(f"Skipping token {token_in['ticker']} on {chain_in.name} due to missing decimals.")
        return None  # Переход к следующему токену, если не удалось получить decimals

    w3_out = Web3(Web3.HTTPProvider(chain_out.rpc))
    checksum_token_out = w3_out.to_checksum_address(token_out["address"])
    token_out_contract = w3_out.eth.contract(address=checksum_token_out, abi=ERC20_ABI)
    decimals_out = get_decimals_with_retries(token_out_contract)

    if decimals_out is None:
        logger.warning(f"Skipping token {token_out['ticker']} on {chain_out.name} due to missing decimals.")
        return None  # Переход к следующему токену, если не удалось получить decimals

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
        "slippage": slippage
    }

    response = make_request_with_retries(url, params)

    if response.status_code == 200:
        data = response.json()
        if data and "amountOutWithoutSlippage" in data[0]:
            amount_out_raw = float(data[0]["amountOutWithoutSlippage"])
            amount_out = amount_out_raw / (10 ** decimals_out)  # Масштабируем amountOut обратно
            if swap_only_in_plus:
                if amount_out - amount > swap_plus_size:
                    return {
                        "from_token": token_in["ticker"],
                        "from_chain": chain_in.name,
                        "to_token": token_out["ticker"],
                        "to_chain": chain_out.name,
                        "amount_in": amount,
                        "amount_out": amount_out,
                        "profit": amount_out - amount,
                        "route": data[0].get("route")
                    }
                logger.info(
                    f"{chain_in.name} {token_in['ticker']} -> {chain_out.name} {token_out['ticker']} | {amount} : {amount_out}")
                return None
            else:
                if amount_out - amount > -max_swap_loss:
                    return {
                        "from_token": token_in["ticker"],
                        "from_chain": chain_in.name,
                        "to_token": token_out["ticker"],
                        "to_chain": chain_out.name,
                        "amount_in": amount,
                        "amount_out": amount_out,
                        "profit": amount_out - amount,
                        "route": data[0].get("route")
                    }
                logger.info(
                    f"{chain_in.name} {token_in['ticker']} -> {chain_out.name} {token_out['ticker']} | {amount} : {amount_out}")
                return None
        logger.warning("response data is empty")
        return None
    logger.warning(f"response status != 200")
    return None


def get_all_routes(tokens: list, swap_only_in_plus: bool, swap_plus_size: float, max_swap_loss: float, slippage: float,
                   amount: float) -> list:
    all_routes = []
    for token_in in tokens:
        chain_in = chains[token_in["chain"].lower()]  # Получаем объект Chain для входного токена
        for token_out in tokens:
            chain_out = chains[token_out["chain"].lower()]  # Получаем объект Chain для выходного токена
            if token_in != token_out or chain_in != chain_out:  # Проверка чтобы не делать обмен одного токена на него же
                result = check_swap_route(token_in, chain_in, token_out, chain_out, swap_only_in_plus, swap_plus_size,
                                          max_swap_loss, slippage, amount)
                if result:
                    # Проверяем, содержит ли результат ключи 'from_token' и 'from_chain'
                    if isinstance(result, dict) and 'from_token' in result and 'from_chain' in result:
                        all_routes.append(result)
                        logger.info(
                            f"Swap {result['from_token']} on {result['from_chain']} to {result['to_token']} on {result['to_chain']}: "
                            f"Amount In = {result['amount_in']}, Amount Out = {result['amount_out']:.6f}")
    return all_routes


def get_profitable_route(routes: list[dict]):
    max_profit_route = routes[0]  # Начальная инициализация
    for i in range(1, len(routes)):  # Начинаем с первого (второго) элемента
        if routes[i].get("profit") > max_profit_route.get("profit"):
            max_profit_route = routes[i]
    return max_profit_route
