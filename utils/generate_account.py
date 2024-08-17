import eth_account
import web3


def generate_account(w3: web3.Web3) -> eth_account.signers.local.LocalAccount:
    w3.eth.account.enable_unaudited_hdwallet_features()
    print("Сгенерируем новый кошелек...")
    account, mnemonic = w3.eth.account.create_with_mnemonic()
    print(f"Адрес вашего кошелька: {account.address}")
    print(f"Сид фраза вашего кошелька: {mnemonic}")
    print(f"Приватный ключ вашего кошелька: {account.key.hex()}")
    return account