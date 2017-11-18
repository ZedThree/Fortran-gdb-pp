import re

def get_dynamic_type(val):

    symbol = gdb.execute("info symbol {:#x}".format(int(val['_vptr'])),
                      True, True)
    vptr_symbol = symbol.split()[0]
    module_vtab = re.compile(r"__(?P<module>[a-z].*)"
                             r"_MOD___vtab_(?P=module)_"
                             r"(?P<type>[A-Z].*)")
    program_vtab = re.compile(r"__vtab_(?P<prog>[a-z0-9_]*)_"
                              r"(?P<type>[A-Z].*)\.[0-9]*")

    if vptr_symbol.startswith("__vtab_"):
        vtab_regex = program_vtab
    else:
        vtab_regex = module_vtab

    type_ = re.match(vtab_regex, vptr_symbol)
    if type_:
        return type_.group("type")
    else:
        return None

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
            cast_string = "*({type}*)({address:#x})".format(
                type=real_type, address=int(val['_data']))
            real_val = gdb.parse_and_eval(cast_string)
            return FortranType(real_val)
    else:
        return None

gdb.pretty_printers.append(my_lookup_type)
