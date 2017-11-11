class MVCEPrinter:
    def __init__(self, val):
        self.val = val

    def to_string(self):
        message = "my_*_type(type: " + str(self.val.type)

        if self.val.address is not None:
            message += ",\n address: <"
            for line in str(self.val.address).split("\n"):
                message += "\t" + line
            message += ">"
        message += ",\n dynamic_type: " + str(self.val.dynamic_type)
        message += ",\n type: " + str(self.val.type)
        message += ",\n type.code: " + str(self.val.type.code)
        message += ",\n type.tag: " + str(self.val.type.tag)
        for index, field in enumerate(self.val.type.fields()):
            message += ",\n type.fields[{}]: {} <{}>".format(
                index, field.name, field.type)
        
        return message + ")"
        
def my_lookup_type(val):
    if "my" in str(val.type).lower():
        return MVCEPrinter(val)
    return None

gdb.pretty_printers.append(my_lookup_type)
