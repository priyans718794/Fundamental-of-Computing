from datetime import date, datetime, timedelta


class State:
    StockStructure = {
        "ID": int,
        "name": str,
        "brand": str,
        "price": float,
        "qty": int,
    }
    RentalStructure = {
        "ID": int,
        "IID": int,
        "date_of_rental": str,
        "rental_unit_days": int,
        "rental_qty": int,
        "username": str,
        "contact": str,
    }
    EarningStructure = {
        "ID": int,
        "username": str,
        "contact": str,
        "price_per_unit": float,
        "total_price": float,
        "date_of_rental": str,
        "date_of_return": str,
        "rental_qty": int,
        "rental_unit_days": int,
    }
    DateFormat = "%Y-%m-%d"
    IN_NON_DELIMITED_CELL = 1
    IN_DELIMITED_CELL = 2


# This helps use use dot-notation. (Instead of using dict['key'], we'll also be able to use dict.key)
class Map(dict):
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


def get_cell_values(line, quotechar='"', delimiter=","):
    stack = []
    stack.append(State.IN_NON_DELIMITED_CELL)
    cell_values = [""]
    for character in line:
        current_state = stack[-1]
        if current_state == State.IN_NON_DELIMITED_CELL:
            if character == quotechar:
                stack.append(State.IN_DELIMITED_CELL)
            elif character == delimiter:
                cell_values.append("")
            else:
                cell_values[-1] += character

        if current_state == State.IN_DELIMITED_CELL:
            if character == quotechar:
                stack.pop()
            else:
                cell_values[-1] += character
    return cell_values


def parse_cell_values(cell_values, type="stocks"):
    parsed = {}
    if type.startswith("rent"):
        structure = State.RentalStructure
    elif type.startswith("stock"):
        structure = State.StockStructure
    elif type.startswith("earn"):
        structure = State.EarningStructure
    else:
        raise ValueError("Unknown type specified for structure of the cell_values.")
    for i in range(len(cell_values)):
        # print(i, cell_values, State.Structure.keys())
        key = tuple(structure.keys())[i]
        if not key.endswith("ID"):
            key = (" ".join(key.split("_"))).capitalize()
        value = tuple(structure.values())[i](cell_values[i])
        parsed[key] = value
    return Map(parsed)


def read(type="stocks"):
    if type.startswith("rent"):
        path = "./rentals.csv"
    elif type.startswith("stock"):
        path = "./stocks.csv"
    elif type.startswith("earn"):
        path = "./earnings.csv"
    else:
        raise ValueError("Unknown database collection specified in type argument.")
    db: list[dict] = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                cell_values = get_cell_values(line, '"', ",")
                db.append(parse_cell_values(cell_values, type))
    except Exception as e:
        print(f"Exception -> {e}")
    return db


def commit(db, type="stocks"):
    if type.startswith("rent"):
        path = "./rentals.csv"
    elif type.startswith("stock"):
        path = "./stocks.csv"
    elif type.startswith("earn"):
        path = "./earnings.csv"
    else:
        raise ValueError("Unknown database specified in type argument.")
    try:
        with open(path, "w") as f:
            for entry in db:
                values = tuple(entry.values())
                values_str = []
                for value in values:
                    values_str.append(str(value))
                # values_str[1:] => Making sure ID isn't there.
                # f.write(",".join(values_str[1:]) + "\n")
                f.write(",".join(values_str) + "\n")
    except Exception as e:
        print(f"Exception -> {e}")
    return True


def print_table(db):
    colList = list(db[0].keys() if db else [])
    _list = [colList]  # 1st row = header
    for entry in db:
        _list.append(
            [str(entry[col] if entry[col] is not None else "") for col in colList]
        )
    colSize = [max(map(len, col)) for col in zip(*_list)]
    formatStr = " | ".join(["{{:<{}}}".format(i) for i in colSize])
    _list.insert(1, ["-" * i for i in colSize])  # Separating line
    for item in _list:
        print(formatStr.format(*item))


def today():
    return date.today()


def parse_date_str(date_str):
    if type(date_str) != str:
        date_str = str(date_str)
    return datetime.strptime(date_str, State.DateFormat).date()


def unit_days(_unit_days):
    return timedelta(days=_unit_days * 5)


def prompt_num(prompt, less_than=9, greater_than=0, save_an_entity=False):
    print(end="\n" * 2)
    try:
        user_input = input(prompt)
        user_input = int(user_input)
    except KeyboardInterrupt:
        exit_prompt()
        return prompt_num(prompt, less_than, greater_than, save_an_entity)
    except Exception as e:
        print(e)
        return prompt_num(prompt, less_than, greater_than, save_an_entity)
    if save_an_entity:
        # Saving an entity through >=
        while user_input >= less_than or user_input < greater_than:  # pyright: ignore
            user_input = prompt_num(prompt, greater_than, less_than)
    else:
        while user_input > less_than or user_input < greater_than:  # pyright: ignore
            user_input = prompt_num(prompt, greater_than, less_than)
    return user_input


def prompt_yn(prompt):
    print(end="\n" * 2)
    try:
        char = input(f"{prompt} [y/n]: ").lower()
        while char not in ("y", "n"):
            char = prompt_yn(prompt)
    except KeyboardInterrupt:
        exit_prompt()
        return prompt_yn(prompt)
    except Exception as e:
        print(e)
        return prompt_yn(prompt)
    return char


def exit_prompt(prompt="Do you wish to quit?"):
    char = prompt_yn(prompt)
    if char == "y":
        exit(0)
