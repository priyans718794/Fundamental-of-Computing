#!/usr/bin/env python3

from utils import (Map, commit, exit_prompt, parse_date_str, print_table,
                   prompt_num, prompt_yn, read, timedelta, today, unit_days)

db = Map({"stocks": read(), "rents": read("rents"), "earnings": read("earnings")})


def handle_returns():
    global db
    _t = "rents"
    tdb = db[_t]
    edb = db.earnings
    _db = db.stocks
    char = prompt_num("Please select an ID of the returened rental: ", len(tdb), 1)
    item_id = char - 1
    entry = tdb[item_id]
    _entry = _db[entry["IID"] - 1]
    print(end="\n" * 2)
    total_price = _entry["Price"] * entry["Rental unit days"] * entry["Rental qty"]
    return_date = parse_date_str(entry["Date of rental"]) + unit_days(
        entry["Rental unit days"]
    )
    invoice_table = [
        {
            "Customer's Name": entry["Username"],
            "Item's Name": _entry["Name"],
            "Brand": _entry["Brand"],
            "Price": f'$ {_entry["Price"]}',
            "Rented Qty": entry["Rental qty"],
            "Contact": entry["Contact"],
            "Rental date": entry["Date of rental"],
            "Return date": return_date,
            "Total Price": f"$ {total_price}",
        }
    ]
    print_table(invoice_table)
    if return_date == today():
        _id = 1
        if len(edb):
            _id = edb[-1]["ID"]
        earning_entry = {
            "ID": _id,
            "username": entry["Username"],
            "contact": entry["Contact"],
            "price_per_unit": _entry["Price"],
            "total_price": total_price,
            "date_of_rental": entry["Date of rental"],
            "date_of_return": return_date,
            "rental_qty": entry["Rental qty"],
            "rental_unit_days": entry["Rental unit days"],
        }
        if len(edb):
            edb.append(earning_entry)
            db.earnings = edb
            commit(edb, "earnings")
        else:
            commit([earning_entry], "earnings")
            db.earnings = [Map(earning_entry)]
        for _index, _entry in enumerate(_db):
            if entry["IID"] == _entry["ID"]:
                _entry["Qty"] += entry["Rental qty"]
                _db[_index] = _entry
                commit(_db, "stocks")
                db.stocks = _db
        for index, _entry in enumerate(tdb):
            if _entry["ID"] == entry["ID"]:
                del tdb[index]
                commit(tdb, "rents")
                db.rents = tdb
    elif (return_date - today()).days > 0:
        handle_early_return(entry["ID"])
    else:
        handle_late_return(entry["ID"])


def handle_late_return(_id):
    global db
    _t = "rents"
    tdb = db[_t]
    edb = db.earnings
    _db = db.stocks
    entry = tdb[_id - 1]
    _entry = _db[entry["IID"] - 1]
    item_qty = entry["Rental qty"]
    total_price = _entry["Price"] * entry["Rental unit days"] * item_qty
    return_date = parse_date_str(entry["Date of rental"]) + unit_days(
        entry["Rental unit days"]
    )
    days_late = (today() - return_date).days
    return_date += timedelta(days=days_late)
    choice = prompt_yn(
        f"Looks like you've submitted the item {days_late} days late, would you like to charge costumer fine for it?"
    )
    print(end="\n" * 2)
    if choice == "y":
        price_per_day_per_item = _entry["Price"] / 5
        fine_price = price_per_day_per_item * item_qty * days_late
        total_price += fine_price
    invoice_table = [
        {
            "Customer's Name": entry["Username"],
            "Item's Name": _entry["Name"],
            "Brand": _entry["Brand"],
            "Price": f'$ {_entry["Price"]}',
            "Rented Qty": entry["Rental qty"],
            "Contact": entry["Contact"],
            "Rental date": entry["Date of rental"],
            "Return date": return_date,
            "Total Price": f"$ {total_price}",
        }
    ]
    print_table(invoice_table)
    _id = 1
    if len(edb):
        _id = edb[-1]["ID"]
    earning_entry = {
        "ID": _id,
        "username": entry["Username"],
        "contact": entry["Contact"],
        "price_per_unit": _entry["Price"],
        "total_price": total_price,
        "date_of_rental": entry["Date of rental"],
        "date_of_return": return_date,
        "rental_qty": entry["Rental qty"],
        "rental_unit_days": entry["Rental unit days"],
    }
    if len(edb):
        edb.append(earning_entry)
        db.earnings = edb
        commit(edb, "earnings")
    else:
        commit([earning_entry], "earnings")
        db.earnings = [Map(earning_entry)]
    for _index, _entry in enumerate(_db):
        if entry["IID"] == _entry["ID"]:
            _entry["Qty"] += entry["Rental qty"]
            _db[_index] = _entry
            commit(_db, "stocks")
            db.stocks = _db
    for index, _entry in enumerate(tdb):
        if _entry["ID"] == entry["ID"]:
            del tdb[index]
            commit(tdb, "rents")
            db.rents = tdb


def handle_early_return(_id):
    global db
    _t = "rents"
    tdb = db[_t]
    edb = db.earnings
    _db = db.stocks
    entry = tdb[_id - 1]
    _entry = _db[entry["IID"] - 1]
    item_qty = entry["Rental qty"]
    total_price = _entry["Price"] * entry["Rental unit days"] * item_qty
    return_date = parse_date_str(entry["Date of rental"]) + unit_days(
        entry["Rental unit days"]
    )
    days_early = (return_date - today()).days
    return_date -= timedelta(days=days_early)
    choice = prompt_yn(
        f"Return date seemed to be {days_early} days ahead, would you like to charge for the rent till today instead of previously mentioned date?"
    )
    print(end="\n" * 2)
    if choice == "n":
        price_per_day_per_item = _entry["Price"] / 5
        deduction_price = price_per_day_per_item * item_qty * days_early
        total_price -= deduction_price
    invoice_table = [
        {
            "Customer's Name": entry["Username"],
            "Item's Name": _entry["Name"],
            "Brand": _entry["Brand"],
            "Price": f'$ {_entry["Price"]}',
            "Rented Qty": entry["Rental qty"],
            "Contact": entry["Contact"],
            "Rental date": entry["Date of rental"],
            "Return date": return_date,
            "Total Price": f"$ {total_price}",
        }
    ]
    print_table(invoice_table)
    _id = 1
    if len(edb):
        _id = edb[-1]["ID"]
    earning_entry = {
        "ID": _id,
        "username": entry["Username"],
        "contact": entry["Contact"],
        "price_per_unit": _entry["Price"],
        "total_price": total_price,
        "date_of_rental": entry["Date of rental"],
        "date_of_return": return_date,
        "rental_qty": entry["Rental qty"],
        "rental_unit_days": entry["Rental unit days"],
    }
    if len(edb):
        edb.append(earning_entry)
        db.earnings = edb
        commit(edb, "earnings")
    else:
        commit([earning_entry], "earnings")
        db.earnings = [Map(earning_entry)]
    for _index, _entry in enumerate(_db):
        if entry["IID"] == _entry["ID"]:
            _entry["Qty"] += entry["Rental qty"]
            _db[_index] = _entry
            commit(_db, "stocks")
            db.stocks = _db
    for index, _entry in enumerate(tdb):
        if _entry["ID"] == entry["ID"]:
            del tdb[index]
            commit(tdb, "rents")
            db.rents = tdb


def handle_new_rentals():
    global db
    _t = "stocks"
    tdb = db[_t]
    _db = db.rents
    char = prompt_num(
        "Please select an ID of available item you want to rent: ", len(tdb), 1
    )
    item_id = char - 1
    entry = tdb[item_id]
    char = prompt_num(
        "Enter quantity of the item you would like to rent: ",
        entry["Qty"],
        1,
        True,  # Saving an entity, since we need at least one quantity of an item.
    )
    rental_qty = char
    entry["Qty"] -= rental_qty
    char = prompt_num(
        "Enter unit day(s) you want to rent the item for (1 unit day = 5 days): ",
        367,
        1,
    )
    rental_unit_days = char
    total_price = entry["Price"] * rental_qty * rental_unit_days
    invoice_table = [
        {
            "Name": entry["Name"],
            "Brand": entry["Brand"],
            "Price": f'$ {entry["Price"]}',
            "Rented Qty": rental_qty,
            "Rental days": rental_unit_days * 5,
            "Total Price": f"$ {total_price}",
        }
    ]
    print("-" * 43)
    print("\n" * 3)
    print("YOUR INVOICE", end="\n\n")
    print_table(invoice_table)
    char = prompt_yn("Would you now like to rent the item?")
    if char == "y":
        tdb[item_id] = entry
        db[_t] = tdb
        _id = 1
        if len(_db):
            _id = _db[-1]["ID"] + 1
        username = input("Please enter your name sir: ")
        contact = input("And just your phone number: ")
        rental_entry = {
            "ID": _id,
            "IID": entry["ID"],
            "Date of rental": today(),
            "Rental unit days": rental_unit_days,
            "Rental qty": rental_qty,
            "Username": username,
            "Contact": contact,
        }
        if len(_db):
            _db.append(rental_entry)
            commit(_db, "rents")
            db.rents = _db
        else:
            commit([rental_entry], "rents")
            db.rents = [Map(rental_entry)]
        commit(tdb, _t)
        print_table(db.stocks)
        print("\n" * 3)
        print_table(db.rents)
        print(end="\n" * 2)
    else:
        entry = {}
        tdb = []


def handle_known_rentals():
    global db
    _t = "rents"
    _db = db.stocks
    tdb = db[_t]
    if not tdb:
        return
    print("-----Rentals-----")
    print_table(tdb)
    for entry in tdb:
        _entry = _db[entry["IID"] - 1]
        return_date = parse_date_str(entry["Date of rental"]) + unit_days(
            entry["Rental unit days"]
        )
        if today() > return_date:
            print(end="\n" * 2)
            more_days = (today() - return_date).days
            print(
                f'{entry["Username"]} was supposed to return {_entry["Name"]} on {return_date}, it has been {more_days} days since no return. You may want to call him on {entry["Contact"]}'
            )
            char = prompt_yn("Did he respond/you called?")
            if char == "y":
                handle_late_return(entry["ID"])
                return
    char = prompt_yn("Has any of above costume been returned?")
    if char == "y":
        handle_returns()
    else:
        handle_new_rentals()


def main():
    global db
    db = Map({"stocks": read(), "rents": read("rents"), "earnings": read("earnings")})
    print("Welcome to the Costume Rental Terminal", end="\n" * 2)
    print("-----Items-----")
    print_table(db.stocks)
    try:
        print(end="\n" * 2)
        if read("rent"):
            handle_known_rentals()
        else:
            handle_new_rentals()
        exit_prompt("Do you wish to exit now?")
        main()
    except Exception as e:
        print()
        print(f"Exception -> {e}")
        print(end="\n" * 2)
        print("Press enter to continue..", end="", flush=True)
        input()
    exit_prompt("Do you wish to exit now?")
    main()


if __name__ == "__main__":
    main()
