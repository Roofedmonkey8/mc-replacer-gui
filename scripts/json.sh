#!/bin/bash

INPUT="output.txt"
OUTPUT="blocks.json"

echo "{" > "$OUTPUT"

while read -r name; do
    if [[ "$name" == *_slab ]]; then
        type="Slab"
    elif [[ "$name" == *_stairs ]]; then
        type="Stair"
    elif [[ "$name" == *_wall ]]; then
        type="Wall"
    else
        type="Normal"
    fi
    echo "  \"$name\": \"$type\"," >> "$OUTPUT"
done < "$INPUT"

# Remove last comma and close JSON
sed -i '$ s/,$//' "$OUTPUT"
echo "}" >> "$OUTPUT"

echo "Generated $OUTPUT with inferred block classes."
