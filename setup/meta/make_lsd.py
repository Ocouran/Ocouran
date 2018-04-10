#!/usr/bin/env python3
import write_files,write_core,write_controllers,write_index_controller,write_jinjatemplates


if __name__ == '__main__':
    one = write_files.make()
    print(one)
    two = write_controllers.make()
    print(two)
    three = write_index_controller.make()
    print(three)
    four = write_jinjatemplates.make()
    print(four)
    five = write_core.make()
    print(five)
