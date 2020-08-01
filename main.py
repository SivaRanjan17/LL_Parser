import sys
import os
import LLParser

if __name__ == '__main__':

    length = len(sys.argv)
    table_format = 'fancy_grid'
    formats = ["plain", "simple", "grid", "fancy_grid", "html"]

    if length >= 2:
        argument = sys.argv[1]

        if argument in ("--help", "-h"):
            print("Input Valid Grammar")
            exit()

        elif os.path.isfile(argument):
            with open(argument, "r") as file:
                grammar, keys = LLParser.grammar_definition(file.read())
                if len(grammar) == 0:
                    print("Invalid grammar in file.")
                    exit(-1)
        else:
            print("No grammar was found.")
            exit(-1)

        if length >= 3:
            if sys.argv[2] in formats:
                table_format = sys.argv[2]
            else:
                print("Invalid table style")
                exit(-1)
    else:
        print("""grammar not recognized!""")

    try:
        table = LLParser.create_table(grammar, keys, tablefmt=table_format)
        print(table)

    except RecursionError:
        print("Left recursive grammar!")


