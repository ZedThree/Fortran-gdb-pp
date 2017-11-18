module foo_module
  implicit none

  type my_base_type
     character(len=4) :: base_char = "base"
  end type my_base_type

  type, extends(my_base_type) :: my_extended_type
     character(len=4) :: extended_char = "ext "
  end type my_extended_type

contains

  subroutine bar(arg)
    class(my_base_type), intent(in) :: arg

    print*, "breakpoint here"
    select type(arg)
    type is (my_base_type)
       print*, "my_base_type ", arg%base_char
    type is (my_extended_type)
       print*, "my_extended_type ", arg%base_char, " ", arg%extended_char
    end select
  end subroutine bar
end module foo_module

program mvce
  use foo_module
  implicit none

  type(my_base_type) :: base1
  type(my_extended_type) :: ext1
  class(my_base_type), allocatable :: alloc_base1
  class(my_base_type), allocatable :: alloc_ext1

  allocate(alloc_base1, source=base1)
  allocate(alloc_ext1, source=ext1)

  call bar(alloc_base1)
  call bar(alloc_ext1)
end program mvce
