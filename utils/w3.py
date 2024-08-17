from settings.chains import chains
from classes.client import Client


def get_balance_in_all_network(acc_list: list):
    obj_acc_list = []
    for acc in acc_list:
        account = Client(chains["ethereum"], acc)
        obj_acc_list.append(account)
    for acc in obj_acc_list:
        print("--------------------------------")
        print(f"Адрес: {acc.public_key}")
        for chain_name in chains:
            chain_obj = chains[chain_name]
            acc.switch_network(chain_obj)
            print(f"{chain_name}: {acc.get_balance()}")


async def get_balance_in_one_network(acc_list: list):
    print("Выберите сеть")
    counter = 1
    for i in chains:
        print(f"{counter}. {i}")
        counter += 1
    choice = int(input("-> "))
    chains_list = list(chains)
    selected_chain = chains_list[choice - 1]
    print("--------------------------------")
    for i in acc_list:
        account = Client(chains.get(selected_chain), i)
        print(account.public_key)
        print(account.get_balance())
        print("--------------------------------")
