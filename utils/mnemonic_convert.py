import os
from eth_account import Account


def read_file(path: str) -> list:
    """
    Читает содержимое файла и возвращает его в виде списка строк.

    :param path: Путь к файлу, который нужно прочитать.
    :return: Список строк из файла.
    :raises FileNotFoundError: Если файл не найден.
    """
    if os.path.exists(path):
        with open(path, "r") as file:
            return file.read().splitlines()
    else:
        raise FileNotFoundError(f"The file '{path}' does not exist.")


def mnemonic_to_private_key(mnemonics: list) -> list:
    """
    Преобразует список мнемонических фраз в список приватных ключей.

    :param mnemonics: Список мнемонических фраз.
    :return: Список приватных ключей, соответствующих каждой мнемонической фразе.
    """
    Account.enable_unaudited_hdwallet_features()  # Включаем поддержку неаудированных функций
    private_key_list = []
    for memo in mnemonics:
        account = Account.from_mnemonic(memo)  # Создаем аккаунт на основе мнемонической фразы
        private_key_list.append(account._private_key.hex())  # Получаем приватный ключ и добавляем в список
    return private_key_list


def ensure_newline_at_end_of_file(path: str) -> None:
    """
    Проверяет, есть ли новая строка в конце файла. Если нет, добавляет её.

    :param path: Путь к файлу, который нужно проверить.
    """
    with open(path, "rb+") as file:
        file.seek(-1, os.SEEK_END)  # Перемещаем указатель в конец файла
        last_char = file.read(1)
        if last_char != b"\n":  # Проверяем, является ли последний символ новой строкой
            file.write(b"\n")  # Если нет, добавляем новую строку


def memo_txt_to_pk_txt() -> None:
    """
    Преобразует все мнемонические фразы из файла в приватные ключи и добавляет их в файл pk.txt,
    избегая повторений ключей и следя за корректностью окончания файла.

    :raises FileNotFoundError: Если файл с мнемоническими фразами или файл для записи ключей не найден.
    """
    memo = read_file("settings/mnemonic.txt")
    pk_list = mnemonic_to_private_key(memo)
    path = "settings/pk.txt"
    existing_pks = set()
    if os.path.exists(path):
        existing_pks = set(read_file(path))
        ensure_newline_at_end_of_file(path)
    with open(path, "a") as file: # Добавление новых приватников
        for pk in pk_list:
            if pk not in existing_pks:  # Проверяем на повторение
                file.write(pk + "\n")
                existing_pks.add(pk)
