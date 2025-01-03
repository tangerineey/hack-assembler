# This program is able to convert a hack assembly file to its binary
# equivalent. However, it is very simple and lacks essential things like
# a proper lexer / parser. I will come back to it once I learn more about
# compilers and interpreters.

import os
import sys

DEST_BINS = {
    None: "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111",
}

COMP_BINS = {
    "0": "101010",
    "1": "111111",
    "-1": "111010",
    "D": "001100",
    "A": "110000",
    "!D": "001101",
    "!A": "110001",
    "-D": "001111",
    "-A": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "D+A": "000010",
    "D-A": "010011",
    "A-D": "000111",
    "D&A": "000000",
    "D|A": "010101",
    "M": "110000",
    "!M": "110001",
    "-M": "110011",
    "M+1": "110111",
    "M-1": "110010",
    "D+M": "000010",
    "D-M": "010011",
    "M-D": "000111",
    "D&M": "000000",
    "D|M": "010101",
}

JUMP_BINS = {
    None: "000",
    "JGT": "001",
    "JEG": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111",
}

SYMBOL_TABLE = {
    "R0": "0",
    "R1": "1",
    "R2": "2",
    "R3": "3",
    "R4": "4",
    "R5": "5",
    "R6": "6",
    "R7": "7",
    "R8": "8",
    "R9": "9",
    "R10": "10",
    "R11": "11",
    "R12": "12",
    "R13": "13",
    "R14": "14",
    "R15": "15",
    "SCREEN": "16384",
    "KBD": "24576",
    "SP": "0",
    "LCL": "1",
    "ARG": "2",
    "THIS": "3",
    "THAT": "4",
}


def read_file(input_filename: str):
    input = []

    with open(input_filename, "r") as file:
        for line in file:
            cleaned_line = skip_whitespace(line)
            if cleaned_line:
                input.append(cleaned_line)

    return input


def skip_whitespace(line: str) -> str | None:
    line = line.strip()
    comment_index = line.find("//")

    if comment_index != -1:
        line = line[:comment_index].strip()

    if not line:
        line = None

    return line


def process_inst(inst: str) -> str:
    A_Inst = inst.startswith("@")

    if A_Inst:
        value = SYMBOL_TABLE.get(inst[1:], None)

        if value is None:
            value = inst[1:]

        num = int(value)
        bin_str = format(num, "016b")

        return bin_str

    equal_pos = inst.find("=")
    colon_pos = inst.find(";")

    dest = comp = jump = None
    bin_str = None

    hasDest = equal_pos != -1
    hasJump = colon_pos != -1

    if hasDest:
        dest = inst[:equal_pos]
        comp = inst[equal_pos + 1 :]
    else:
        comp = inst

    if hasJump:
        if not hasDest:
            comp = inst[:colon_pos]
        jump = inst[colon_pos + 1 :]

    A_Bit = "1" if "M" in comp else "0"
    prefix = "111" + A_Bit

    dest_bin = DEST_BINS.get(dest, "000")
    comp_bin = COMP_BINS.get(comp, None)
    jump_bin = JUMP_BINS.get(jump, "000")

    if comp_bin is not None:
        bin_str = prefix + comp_bin + dest_bin + jump_bin
    else:
        raise Exception("Comp bin was not found!")

    return bin_str


def populate_table(instructions: list[str]):
    index = 0

    for inst in instructions:
        if inst.startswith("("):
            SYMBOL_TABLE[inst.strip("()")] = index
        else:
            index += 1


def populate_variables(instructions: list[str]):
    avail_register = 16

    for inst in instructions:
        if inst.startswith("@"):
            inst = inst[1:]
            inTable = inst in SYMBOL_TABLE.keys()
            isNotNum = not inst.isdigit()

            if isNotNum and not inTable:
                SYMBOL_TABLE[inst.strip("@")] = avail_register
                avail_register += 1


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 src/main.py <sourcefile.asm>")
        exit(1)

    file = sys.argv[1]
    filename, extension = os.path.splitext(os.path.basename(file))

    if extension != ".asm":
        print("Invalid filetype.")
        exit(1)

    instructions = read_file(file)
    binary = []

    populate_table(instructions)
    populate_variables(instructions)

    index = 0

    for inst in instructions:
        if inst.startswith("("):
            continue
        else:
            bin_inst = process_inst(inst)
            binary.append(bin_inst)
            index += 1

    with open(f"{filename}.hack", "w") as file:
        for bin in binary:
            file.write(bin + "\n")


if __name__ == "__main__":
    main()
