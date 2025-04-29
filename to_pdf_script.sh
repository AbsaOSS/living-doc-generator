#!/bin/bash

# Check if the input directory is provided as a parameter
if [ -z "$1" ]; then
    echo "❌ Error: Input directory not provided."
    echo "Usage: ./to_pdf_script.sh <input_directory> [output_pdf_file]"
    exit 1
fi

# Set the input directory from the first argument
INPUT_DIR="$1"

# Set the output PDF file (optional, defaults to "text.pdf" if not provided)
OUTPUT_FILE="${2:-text.pdf}"

# Temporary files
TMP_SORTED_FILES=$(mktemp)
TMP_PROCESSED_DIR=$(mktemp -d)

# Step 1: Find all md files, extract weight, and sort
for file in "$INPUT_DIR"/*.md; do
    # Extract weight from YAML front matter
    weight=$(awk '/^weight:/ {print $2; exit}' "$file")
    # In case weight is missing, default to a large number (9999)
    weight=${weight:-9999}

    # Process file to fix HTML links → Markdown
    processed_file="$TMP_PROCESSED_DIR/$(basename "$file")"
    sed -E "s|<a href='([^']+)'[^>]*>([^<]+)</a>|[\2](\1)|g" "$file" > "$processed_file"

    echo "$weight|$processed_file"
done | sort -n | cut -d'|' -f2 > "$TMP_SORTED_FILES"

# Step 2: Build the list of files to pass to pandoc
MD_FILES=$(cat "$TMP_SORTED_FILES")

# Step 3: Generate PDF using xelatex
pandoc --pdf-engine=xelatex --include-in-header=preamble.tex -V title="Living Documentation" $MD_FILES -o "$OUTPUT_FILE"

# Step 4: Cleanup
rm "$TMP_SORTED_FILES"
rm -r "$TMP_PROCESSED_DIR"

echo "✅ PDF generated: $OUTPUT_FILE"
