from hexbytes import HexBytes
from web3 import Web3

from settings.chains import Chain


class Client:
    def __init__(self, chain: Chain, private_key: str):
        """
        Инициализирует клиента с подключением к RPC и настройкой аккаунта на основе приватного ключа.

        :param chain: обьект класса Chain
        :param private_key: Приватный ключ в шестнадцатеричном формате (с или без префикса '0x').
        :raises ConnectionError: Если не удается подключиться к RPC.
        """
        self.chain = chain
        self.rpc = self.chain.rpc
        self.connection = Web3(Web3.HTTPProvider(self.rpc))

        if not self.connection.is_connected():
            raise ConnectionError(f"Failed to connect to the RPC at {self.rpc}")

        self.private_key = bytes.fromhex(private_key[2:] if private_key.startswith('0x') else private_key)
        self.account = self.connection.eth.account.from_key(self.private_key)
        self.public_key = self.account.address

    def __str__(self) -> str:
        """
        Возвращает строковое представление клиента, включая публичный и приватный ключи.

        :return: Строка с публичным и приватным ключами.
        """
        return f"Client(public_key={self.public_key}, private_key={'0x' + self.private_key.hex()})"

    def __del__(self) -> str:
        """
        Возвращает сообщение о том, что клиент был удален.

        :return: Сообщение о том, что клиент был удален.
        """
        return f"Client(public_key={self.public_key}, private_key={'0x' + self.private_key.hex()}) WAS DELETED"

    def switch_network(self, chain: Chain):
        """
        Переключает клиента на другую сеть.

        :param chain: новый объект сети
        :raises ConnectionError: Если не удается подключиться к новому RPC.
        """
        self.chain = chain
        self.rpc = self.chain.rpc
        self.connection = Web3(Web3.HTTPProvider(self.rpc))

        # Проверка подключения к новой сети
        if not self.connection.is_connected():
            raise ConnectionError(f"Failed to connect to the RPC at {self.rpc}")

        # Перезагрузка данных учетной записи с новым RPC
        self.account = self.connection.eth.account.from_key(self.private_key)
        self.public_key = self.account.address
        return f"Switched to network {chain.name}"

    def get_transaction_receipt(self, transaction_hash: HexBytes) -> dict:
        """
        Получает информацию о транзакции на основе её хеша.

        :param transaction_hash: Хеш транзакции.
        :return: Словарь с информацией о транзакции.
        """
        return self.connection.eth.get_transaction_receipt(transaction_hash)

    def send_transaction(self, transaction: dict) -> HexBytes:
        """
        Подписывает и отправляет транзакцию в сеть, возвращая её хеш.

        :param transaction: Словарь с данными транзакции.
        :return: Хеш отправленной транзакции.
        """
        signed_transaction = self.account.sign_transaction(transaction)
        return self.connection.eth.send_raw_transaction(signed_transaction.rawTransaction)

    def get_balance(self, address: str = None) -> float:
        """
        Получает баланс аккаунта в ETH.

        :param address: Адрес для проверки баланса. Если не указан, используется публичный ключ клиента.
        :return: Баланс аккаунта в ETH.
        """
        if address is None:
            address = self.public_key
        balance_wei = self.connection.eth.get_balance(address)
        return self.connection.from_wei(balance_wei, 'ether')

    def get_nonce(self, address: str = None) -> int:
        """
        Получает текущий nonce для учетной записи.

        :param address: Адрес учетной записи. Если не указан, используется публичный ключ клиента.
        :return: Nonce для учетной записи.
        """
        if address is None:
            address = self.public_key
        return self.connection.eth.get_transaction_count(address)

    def approve(self, token_address: str, spender: str, amount: float) -> HexBytes:
        """
        Выполняет approve транзакцию, позволяя spender расходовать до amount токенов от имени владельца.

        :param token_address: Адрес смарт-контракта токена (ERC-20).
        :param spender: Адрес, которому разрешено тратить токены.
        :param amount: Количество токенов для одобрения (в формате float).
        :return: Хеш транзакции.
        """
        # ABI для метода approve и метода decimals
        abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

        # Создание объекта контракта
        contract = self.connection.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)

        # Получение количества знаков после запятой (decimals)
        decimals = contract.functions.decimals().call()

        # Приведение amount к минимальным единицам токена
        scaled_amount = int(amount * (10 ** decimals))

        # Nonce для транзакции
        nonce = self.get_nonce()

        # Оценка газа для транзакции
        estimated_gas = contract.functions.approve(Web3.to_checksum_address(spender), scaled_amount).estimate_gas({
            'from': self.public_key
        })

        # Получение текущей цены газа
        gas_price = self.connection.eth.gas_price

        # Создание транзакции для вызова метода approve
        transaction = contract.functions.approve(Web3.to_checksum_address(spender), scaled_amount).build_transaction({
            'from': self.public_key,
            'nonce': nonce,
            'gas': estimated_gas,
            'gasPrice': gas_price,
            'chainId': self.chain.id
        })

        # Подписывание и отправка транзакции
        signed_transaction = self.account.sign_transaction(transaction)
        return self.connection.eth.send_raw_transaction(signed_transaction.rawTransaction)

    def get_allowance(self, token_address: str, spender: str = None) -> float:
        """
        Получает текущий лимит токенов, одобренный для конкретного spender(для клиента если не указывать).

        :param token_address: Адрес смарт-контракта токена (ERC-20).
        :param spender: Адрес, которому разрешено тратить токены.
        :return: Лимит токенов в формате float с учетом decimals.
        """
        if not spender:
            spender = self.public_key
        abi = [
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "remaining", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

        # Создание объекта контракта
        contract = self.connection.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)

        # Получение количества знаков после запятой (decimals)
        decimals = contract.functions.decimals().call()

        # Получение текущего лимита
        allowance = contract.functions.allowance(self.public_key, Web3.to_checksum_address(spender)).call()

        # Приведение лимита к формату float
        return allowance / (10 ** decimals)

    def get_token_balance(self, token_address: str, spender: str = None) -> float:
        """
        Получает баланс токенов для текущего пользователя.

        :param spender: адрес, баланс которого проверяем, если не указывать, то текущего клиента
        :param token_address: Адрес смарт-контракта токена (ERC-20).
        :return: Баланс токенов в виде float с учетом decimals.
        """
        if not spender:
            spender = self.public_key
        abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

        # Создание объекта контракта
        contract = self.connection.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)

        # Получение количества знаков после запятой (decimals)
        decimals = contract.functions.decimals().call()

        # Получение баланса
        balance = contract.functions.balanceOf(spender).call()

        # Приведение баланса к формату float
        return balance / (10 ** decimals)

    def send_eth(self, to_address: str, amount: float) -> HexBytes:
        """
        Отправляет ETH на указанный адрес.

        :param to_address: Адрес получателя.
        :param amount: Сумма для отправки в ETH.
        :return: Хеш транзакции.
        """
        # Приведение amount к минимальным единицам (wei)
        value = self.connection.to_wei(amount, 'ether')

        # Nonce для транзакции
        nonce = self.get_nonce()

        # Создание транзакции
        transaction = {
            'to': Web3.to_checksum_address(to_address),
            'value': value,
            'gas': 21000,  # фиксированное значение для обычных ETH транзакций
            'gasPrice': self.connection.eth.gas_price,
            'nonce': nonce,
            'chainId': self.chain.id
        }

        # Подписывание и отправка транзакции
        signed_transaction = self.account.sign_transaction(transaction)
        return self.connection.eth.send_raw_transaction(signed_transaction.rawTransaction)

    def transfer_token(self, token_address: str, to_address: str, amount: float) -> HexBytes:
        """
        Отправляет ERC-20 токены на указанный адрес.

        :param token_address: Адрес смарт-контракта токена (ERC-20).
        :param to_address: Адрес получателя.
        :param amount: Сумма для отправки в формате float.
        :return: Хеш транзакции.
        """
        abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]

        # Создание объекта контракта
        contract = self.connection.eth.contract(address=Web3.to_checksum_address(token_address), abi=abi)

        # Получение количества знаков после запятой (decimals)
        decimals = contract.functions.decimals().call()

        # Приведение amount к минимальным единицам токена
        scaled_amount = int(amount * (10 ** decimals))

        # Nonce для транзакции
        nonce = self.get_nonce()

        # Оценка газа для транзакции
        estimated_gas = contract.functions.transfer(Web3.to_checksum_address(to_address), scaled_amount).estimate_gas({
            'from': self.public_key
        })

        # Получение текущей цены газа
        gas_price = self.connection.eth.gas_price

        # Создание транзакции
        transaction = contract.functions.transfer(Web3.to_checksum_address(to_address),
                                                  scaled_amount).build_transaction({
            'from': self.public_key,
            'nonce': nonce,
            'gas': estimated_gas,
            'gasPrice': gas_price,
            'chainId': self.chain.id
        })

        # Подписывание и отправка транзакции
        signed_transaction = self.account.sign_transaction(transaction)
        return self.connection.eth.send_raw_transaction(signed_transaction.rawTransaction)

