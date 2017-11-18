Fortran-gdb-pp
==============

A gdb pretty printer for Fortran dynamic types

This is currently only "proof of concept", and is by no means
guaranteed to work. It works for *me* with `gfortran 7.2` and `gdb
8.0.1`, and the very small number of programs I've tried.

How to use
----------

Start gdb, then:

```
python exec(open("fortran_printer.py").read())
```

What's the problem?
-------------------

Polymorphic objects don't get printed nicely in gdb. Take the program
[gdb_mvce.f90](./gdb_mvce.f90) with a breakpoint on line 46. Printing
`alloc_ext` gives:

```
(gdb) p alloc_ext1
$1 = ( _data = 0x606260, _vptr = 0x400da0
     <__foo_module_MOD___vtab_foo_module_My_extended_type> )
```

which is not very helpful. In order to see the actual value of
`alloc_ext`, we need to do

```
(gdb) p *(my_extended_type*)(alloc_ext1%_data)
$2 = ( my_base_type = ( base_char = 'base' ), extended_char = 'ext ' )
```

because gdb thinks `alloc_ext1%_data` is a pointer to a `my_base_type`
and not a `my_extended_type`. This quickly becomes frustrating if your
type has polymorphic components.

With Fortran-gdb-pp, we instead get:

```
(gdb) p alloc_ext1
$3 = ( my_base_type = ( base_char = 'base' ), extended_char = 'ext ' )
```

How does it work?
-----------------

Unfortunately, we have to work around several limitations of the gdb
python API. Firstly, gdb reports the `dynamic_type` of a polymorphic
variable as being its base type, and not its actual dynamic type! This
means we need some other way of getting its dynamic type. Luckily, the
symbol for the `_vptr` component (at least with gfortran 7.2) contains
the dynamic type, so we can use this. Briefly, we do the following:

1. Look up symbol for the value's `_vptr`
2. Parse the symbol to get the dynamic type
3. Cast the `_data` component to a pointer to the dynamic type and
   dereference

For 1., we need to get the `_vptr` symbol. We can do this
in gdb with `info symbol foo%_vptr`. The python API lacks such a
function, so instead we do:

```
gdb.execute("info symbol {:#x}".format(int(val['_vptr'])))
```

`int(val['_vptr'])` gets the address of `_vptr`

Next, we need to parse the symbol. With gfortran 7.2, `_vptr` symbols
look like either:

- `__<module name>_MOD___vtab_<module name>_<Dynamic type>` for types
  defined in modules, or
- `__vab_<program name>_<Dynamic type>.nnnn` for types defined in
  programs

Module and program names can contain underscores, but luckily the type
starts with a capital letter while everything else is in lower case.

Lastly, we need to actually print the `_data` component as the dynamic
type. While the python API does provide a `Value.cast(type)` method,
the `type` argument must be a `gdb.Type` object. No matter, we can use
the `gdb.lookup_type(name)` function... except that this doesn't work
with Fortran types. This time, we fallback to using
`gdb.parse_and_eval`:

```
cast_string = "*({type}*)({address:#x})".format(
    type=real_type, address=int(val['_data']))
real_val = gdb.parse_and_eval(cast_string)
```

where `real_type` is a string containing the dynamic type. This
basically executes `*(<dynamic type>)(value%_data)` and then we can
pass the resulting value to a pretty printer that just returns
`str(val)`, i.e. like the default printer.


Known issues
------------

- printing allocatable variables before they've been allocated will
  crash gdb
- accessing components of dynamic types is still annoying, as you
  still need to go through the intermediate `_data` component, which
  gdb thinks is a pointer to a base type object

