class MVCEPrinter:
    def __init__(self, val):
        self.val = val

    def to_string(self):
        message = "my_*_type(type: " + str(self.val.type)

        fields = self.val.type.fields()
        real_type = None
        if fields is not None:
            field_names = [field.name for field in fields]
            if "_vptr" in field_names:
                sym = gdb.execute("info symbol {:#x}".format(long(self.val['_vptr'])),
                                  True, True)
                if "my_extended_type" in sym.split()[0].lower():
                    print("This is actually a 'my_extended_type'!")
                    real_type = "extended"

        return message + ")"
        
def my_lookup_type(val):
    if "my" in str(val.type).lower():
        return MVCEPrinter(val)
    return None

gdb.pretty_printers.append(my_lookup_type)
