import re

def get_dynamic_type(val):

    real_type = None
    print("vptr at : {:#x}".format(int(val['_vptr'])))
    symbol = gdb.execute("info symbol {:#x}".format(int(val['_vptr'])),
                      True, True)
    vptr_symbol = symbol.split()[0]
    print("vptr symbol is ", vptr_symbol)
    module_vtab = re.compile(r"__(?P<module>[a-z].*)"
                             r"_MOD___vtab_(?P=module)_"
                             r"(?P<type>[A-Z].*)")
    program_vtab = re.compile(r"__vtab_[a-z0-9_]*_"
                              r"(P<type>[A-Z].*)\.[0-9]*")

    if vptr_symbol.startswith("__vtab_"):
        print("type defined in a program")
        vtab_regex = program_vtab
    else:
        print("type defined in a module")
        vtab_regex = module_vtab

    type_ = re.match(vtab_regex, vptr_symbol)
    print(type_)
    if type_:
        real_type = type_.group("type")
        print("dynamic type is ", real_type)

    return real_type

class FortranType:
    def __init__(self, val):
        self.val = val

    def to_string(self):
        return str(self.val)

def my_lookup_type(val):
    if "Type " not in str(val.type):
        return None
    fields = val.type.fields()
    if fields is not None:
        field_names = [field.name for field in fields]
        if "_vptr" in field_names:
            real_type = get_dynamic_type(val)
            print(field_names)
            data_address = val['_data']
            print(data_address)
            cast_string = "*({type}*)({address:#x})".format(
                type=real_type, address=int(val['_data']))
            print(cast_string)
            real_val = gdb.parse_and_eval(cast_string)
            return FortranType(real_val)
    else:
        return None

gdb.pretty_printers.append(my_lookup_type)
