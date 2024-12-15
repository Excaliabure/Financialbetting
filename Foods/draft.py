import json
import os


def get_json():    
    f = open("prices.json")
    a = json.load(f)
    f.close()
    return a


def save_new(dictionary):

    save_file = open("prices.json", "w")  
    json.dump(dictionary, save_file, indent = 6)  
    save_file.close()          


def add_store(name):

    j = get_json()
    if name not in j.keys():
        j[name] = {}
        save_new(j)
        print(f"[ADDED] Store : {name}")
        return 0
    
    else:
        print(f"[EXISTS] Store : {name}")
        return 1
    
def remove_store(name):
    j = get_json()
    if name not in j.keys():
        j.pop(name, None)
        save_new(j)
        
        print(f"[REMOVED] Store : {name}")
        return 0
    else:
        print(f"[UNKNOWN] Store : {name}")
        return 1
    

def add_item(store, name,bought_at = -1, per_lb = -1, per_unit = -1, amt = -1, avg = -1):

    j = get_json()
    if name not in j[store].keys():
        j[store][name] = {"amt" : -1,
                          "bought at" : -1,
                          "per unit" : -1,
                          "per lb" : -1}

    if name in j[store].keys():
        
        if amt >= -1.0:
            j[store][name]["amt"] = amt 
        if bought_at >= -1.0:
            j[store][name]["bought at"] = bought_at
        if per_unit >= -1.0:
            j[store][name]["per unit"] = per_unit
        if per_lb >= -1.0:
            j[store][name]["per lb"] = per_lb
        
        save_new(j)
        print(f"[ADDED] {store} -> {name} \n\t -> bought at : {bought_at}\n\t -> per unit : {per_unit} \n\t -> per lb : {per_lb}")
        return 0
    else:
        print(f"[UNKNOWN] {store} -> {name}")
        return 1


def remove_item(store,name):
    j = get_json()
    if name in j[store].keys():
        j[store].pop(name, None)
        save_new(j)
        print(f"[REMOVED] {store} -> {name}")
        return 0
    
    else:
        print(f"[UNKNOWN] {store} -> {name}")
        return 1


def check_store(store_name):
    j = get_json()
    if store_name not in j.keys():
        print(f"{store_name} Not Found")
        add_store(store_name)
        return 0
    else:
        return 1

store_default = None
running = True
os.system("cls")
while running:


    # Options
    a = input(f"Current Store Default : {store_default}\n[1] Add item\n[2] Add store\n[3] Remove item\n[4] Remove Store\n[5] Set Store Default\n[6] Remove Store default\n")
    os.system("cls")



    print("[q] Exit")
    if a == "5":
        store_default = input("Set Store Default : ")
        os.system("cls")
    
    elif a == "6":
        store_default = None
        os.system("cls")
    
    elif a == "1":
        print(f"*Note -1 for no change*\nCurrent Store : {store_default}\n\n")
        
        j = get_json()
        if store_default in j.keys():
            print(f"Store : {store_default}")
            n = input("Name of item : ")
            ba = float(input("bought at : "))
            pl = float(input("per pound : "))
            pu = float(input("per unit : "))
            amt = float(input("amt : "))


            
            add_item(store_default,n,ba,pl,pu)
            input("")
            os.system('cls')
        else:
            store = input((f"Store : "))
            check_store(store)
            n = input("Name of item : ")
            ba = float(input("bought at : "))
            pl = float(input("per pound : "))
            pu = float(input("per unit : "))
            amt = float(input("amt : "))
            
            add_item(store,n,ba,pl,pu)
            input("")
            os.system('cls')
        

