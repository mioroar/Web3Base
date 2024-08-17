from utils.mnemonic_convert import memo_txt_to_pk_txt, read_file
from utils.other import get_logo
from utils.w3 import get_balance_in_one_network, get_balance_in_all_network


def account_menu() -> list:
    choice = None
    while not choice:
        print(
            """
            1. Импротировать аккаунты из mnemonic.txt
            2. Импортировать аккаунты из pk.txt
            """)
        choice = input("-> ")

        if choice == '1':
            memo_txt_to_pk_txt()
            print("Сид фразы конвертированы в приватные ключи и добавлены в pk.txt")
            acc_list = read_file("settings/pk.txt")
            print(f"Обнаружено {len(acc_list)} аккаунтов")
            return acc_list
        elif choice == '2':
            acc_list = read_file("settings/pk.txt")
            print(f"Обнаружено {len(acc_list)} аккаунтов")
            return acc_list
        else:
            print("Неправильный ввод!")
            choice = None


def action_menu(accs: list):
    while True:
        choice = None
        while not choice:
            print(
                """
                1. Получить нативные балансы аккаунтов в определенной сети
                2. Получить нативные балансы в всех сетях
                """)
            choice = input("-> ")
            if choice == '1':
                get_balance_in_one_network(accs)
            elif choice == '2':
                get_balance_in_all_network(accs)
            else:
                print("Неправильный ввод!")
                choice = None


def main():
    get_logo()
    accs = account_menu()
    action_menu(accs)


if __name__ == '__main__':
    main()
