def GetValue(attribute):
    entry_dict = ToDictionary(attribute)
    entry_list = ToList(attribute)
    entry_tuple = ToTuple(attribute)
    entry_float = ToFloat(attribute)
    entry_int = ToInt(attribute)

    if entry_dict:
        my_dict = dict()

        for key, value in entry_dict.items():
            my_dict[key] = GetValue(value)

        return my_dict

    elif entry_list:
        my_list = [GetValue(element) for element in entry_list]
        return my_list

    elif entry_tuple:
        return GetValue(entry_tuple[0]), GetValue(entry_tuple[1])

    elif entry_int:
        return entry_int

    elif entry_float:
        return entry_float

    else:
        return attribute


def ToList(string):
    if string[0] == "[":
        return string[1:-1].split(", ")
    else:
        return False

def ToTuple(string):
    if string[0] == "(":
        terms = string[1:-1].split(", ")
        return terms[0], terms[1]
    else:
        return False

def ToDictionary(string):
    if string[0] == "{":
        terms = string[1:-1].split(", ")
        if len(terms) == 4:
            new_terms = [(terms[0] + ', ' + terms[1]), (terms[2] + ', ' + terms[3])]
            terms = new_terms

        d = dict()
        for term in terms:
            key_value = term.split(": ")
            d[key_value[0]] = key_value[1]
        return d

    else:
        return False

def ToInt(string):
    if string.isdigit():
        return int(string)
    else:
        return False

def ToFloat(string):
    if "." in string:
        numbers = string.split(".")
        if (len(numbers) == 2) and (numbers[0].isdigit()) and (numbers[1].isdigit()):
            return float(string)
    return False