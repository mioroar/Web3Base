import os


def get_logo():
    print("""
████╗░██████╗░███████╗████╗ ░█████╗░███████╗░█████╗░███████╗██╗░░░░░░█████╗░
██╔═╝██╔════╝░╚════██║╚═██║ ██╔══██╗╚════██║██╔══██╗╚════██║██║░░░░░██╔══██╗
██║░░██║░░██╗░░░░░██╔╝░░██║ ███████║░░███╔═╝███████║░░███╔═╝██║░░░░░██║░░██║
██║░░██║░░╚██╗░░░██╔╝░░░██║ ██╔══██║██╔══╝░░██╔══██║██╔══╝░░██║░░░░░██║░░██║
████╗╚██████╔╝░░██╔╝░░████║ ██║░░██║███████╗██║░░██║███████╗███████╗╚█████╔╝
╚═══╝░╚═════╝░░░╚═╝░░░╚═══╝ ╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝╚══════╝░╚════╝░
Telegram community: https://t.me/g7monitor
""")


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

def filter_tokens(tokens):
    print("Список доступных токенов:")
    for i, token in enumerate(tokens):
        print(f"{i + 1}: {token['chain']} - {token['ticker']}")

    include_indexes = input("Введите номера токенов для включения, разделенные запятыми (или оставьте пустым для всех): ")
    exclude_indexes = input("Введите номера токенов для исключения, разделенные запятыми (или оставьте пустым, чтобы ничего не исключать): ")

    if include_indexes:
        include_indexes = list(map(int, include_indexes.split(',')))
        tokens = [tokens[i - 1] for i in include_indexes if i <= len(tokens)]

    if exclude_indexes:
        exclude_indexes = list(map(int, exclude_indexes.split(',')))
        tokens = [token for i, token in enumerate(tokens) if (i + 1) not in exclude_indexes]

    return tokens
