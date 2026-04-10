"""Fix ALL quote issues in generate-synapse-pptx.js - comprehensive approach"""
import re

path = "scripts/generate-synapse-pptx.js"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Step 1: Remove ALL inner quotation marks from Chinese text
# Chinese text shouldn't need quotation marks - they add emphasis in Chinese without them
# Remove patterns like: "text" inside already-quoted strings, or `text` inside backtick strings

lines = content.split("\n")
for i, line in enumerate(lines):
    # Only process lines with string literals containing Chinese
    if not re.search(r'[\u4e00-\u9fff]', line):
        continue

    # Remove nested backticks inside backtick strings
    # Pattern: `...`nested`...` -> `...nested...`
    if line.count('`') > 2:
        # Find the outermost backtick pair and remove inner ones
        parts = line.split('`')
        if len(parts) > 3:
            # Reconstruct: keep first ` and last `, remove inner `
            new_line = parts[0] + '`' + ''.join(parts[1:-1]) + '`' + parts[-1]
            lines[i] = new_line

    # Remove stray double quotes inside backtick strings
    if '`' in line:
        # Find backtick-delimited content and remove " inside it
        def clean_backtick_content(m):
            inner = m.group(1).replace('"', '')
            return '`' + inner + '`'
        lines[i] = re.sub(r'`([^`]+)`', clean_backtick_content, lines[i])

content = "\n".join(lines)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Comprehensive fix done")
