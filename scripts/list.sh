#!/bin/bash

# ✅ Set the target directory (change as needed)
DIR="icons/blocks"

# ✅ Set the output file
OUT="output.txt"

# ✅ Whether to strip the .png extension (true/false)
STRIP=true

# Clear or create output file
> "$OUT"

# Loop through .png files in the directory
for file in "$DIR"/*.png; do
    if [ "$STRIP" = true ]; then
        basename "${file%.*}" >> "$OUT"
    else
        basename "$file" >> "$OUT"
    fi
done

echo "Wrote list of PNGs to $OUT"

