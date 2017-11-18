import re

class MVCEPrinter:
    def __init__(self, val):
        self.val = val

    def to_string(self):

        fields = self.val.type.fields()
        real_type = None
        if fields is not None:
            field_names = [field.name for field in fields]
            if "_vptr" in field_names:
                print("vptr at : {:#x}".format(int(self.val['_vptr'])))
                symbol = gdb.execute("info symbol {:#x}".format(int(self.val['_vptr'])),
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

        if real_type:
            message = real_type + "(..."
        else:
            message = str(self.val.type) + "(..."

        return message + ")"

def my_lookup_type(val):
    if "my" in str(val.type).lower():
        return MVCEPrinter(val)
    return None

gdb.pretty_printers.append(my_lookup_type)
