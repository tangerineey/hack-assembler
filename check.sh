#!/bin/bash

set -e

input_dir="test/input"
expected_output_dir="test/output"

for asm_file in "$input_dir"/*.asm; do
    base_name=$(basename "$asm_file" .asm)

    python3 src/main.py "$asm_file"

    generated_hack="$base_name.hack"
    expected_hack="$expected_output_dir/$base_name.hack"

    if [ -f "$expected_hack" ]; then
        echo "Comparing $generated_hack with $expected_hack"
        diff -u "$generated_hack" "$expected_hack"
    else
        echo "Expected output file for $generated_hack not found in $expected_output_dir"
    fi

    rm "$generated_hack"
done

echo "All tests passed!"
