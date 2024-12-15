from utils import *
import os


def main():
    ev = BotApi()
    running = True

    while running:

        os.system(('cls' if os.name == 'nt' else 'clear'))

        print("Press Enter to update...\n")
        positions = ev.view()
        acc_info = ev.view(gen_info=True)
        acc_info = acc_info['account']
        print(f"Bal {acc_info['balance']}")
        print(f"PL {acc_info['pl']}\n")

        for i in positions['positions']:
            instrument = i['instrument']
            pos_type = ('long' if i['long']['units'] != '0' else 'short')
            unrealizedPL = i['unrealizedPL']


            print(f"{instrument}  {i[pos_type]['units']}  {unrealizedPL}")


        input("\nPair Units Profit-Loss\n")

main()
