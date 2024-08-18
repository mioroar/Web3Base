from modules.crosscurve_arbitrage import get_all_routes, get_profitable_route
from settings.crosscurve import tokens
from utils.mnemonic_convert import memo_txt_to_pk_txt
from utils.other import get_logo, read_file, filter_tokens
from utils.w3 import get_balance_in_one_network, get_balance_in_all_network


def crosscurve_arbitrage_settings_menu():
    swap_only_plus = bool(int(input("Искать только плюсовые роуты? 1-да 0-нет: ")))
    if swap_only_plus:
        swap_plus_size = float(input("Минимальный профит с роута (более чем N $): "))
        max_swap_loss = 0
    else:
        swap_plus_size = 0
        max_swap_loss = float(input("Максимальный размер потерь в роуте (менее чем N $): "))
    slippage = float(input("Максимальный диапазон проскальзывания (менее чем N %): "))
    amount = float(input("Сумма свапа (в $): "))
    filtered_tokens = filter_tokens(tokens)
    print("Окончательный список токенов для работы:")
    for token in filtered_tokens:
        print(f"{token['chain']} - {token['ticker']} ({token['address']})")
    print("Начался поиск роутов. Ожидайте")
    return {"filtered_tokens": filtered_tokens,
            "swap_only_plus": swap_only_plus,
            "swap_plus_size": swap_plus_size,
            "max_swap_loss": max_swap_loss,
            "slippage": slippage,
            "amount": amount}


def account_menu() -> list:
    choice = None
    while not choice:
        print(
            """
            1. Импротировать аккаунты из mnemonic.txt
            2. Импортировать аккаунты из pk.txt
            3. CrossCurve арбитраж
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
        elif choice == '3':
            print("Настройка арбитража")
            arbitrage_settings = crosscurve_arbitrage_settings_menu()
            all_routes = get_all_routes(arbitrage_settings.get("filtered_tokens"),
                                        arbitrage_settings.get("swap_only_plus"),
                                        arbitrage_settings.get("swap_plus_size"),
                                        arbitrage_settings.get("max_swap_loss"), arbitrage_settings.get("slippage"),
                                        arbitrage_settings.get("amount"))
            print("Все роуты, подходящие под запрос")
            for route in all_routes:
                print(
                    f"{route.get("from_chain")} {route.get("from_token")} -> {route.get("to_chain")} {route.get("to_token")} | {route.get("amount_in")} : {route.get("amount_out")}")
            print("---------------------------------------------------------------------")
            print("Самый выгодный роут")
            profitable = get_profitable_route(all_routes)
            print(
                f"{profitable.get("from_chain")} {profitable.get("from_token")} -> {profitable.get("to_chain")} {profitable.get("to_token")} | {profitable.get("amount_in")} : {profitable.get("amount_out")} | PROFIT = {profitable.get("profit")}")
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
    while True:
        get_logo()
        accs = account_menu()
        if accs is not None:
            action_menu(accs)


if __name__ == '__main__':
    main()
