with open('main.py', 'r') as f:
    lines = f.readlines()

# Find the problematic method
in_wrong_method = False
enhanced_start = None
enhanced_end = None
indent_level = None

for i, line in enumerate(lines):
    # Find 'async def enhanced_listen_for_command' that's indented too much
    if 'async def enhanced_listen_for_command' in line:
        # Check if it's indented more than it should be
        current_indent = len(line) - len(line.lstrip())
        if current_indent > 8:  # Should be 4 or 8 for class methods, not more
            print(f"Found incorrectly indented method at line {i+1}")
            enhanced_start = i
            indent_level = current_indent - 4  # Reduce by 4 spaces
            in_wrong_method = True
    
    if in_wrong_method:
        # Check if we've reached the end (next method at class level)
        if i > enhanced_start and line.strip() and not line.startswith(' ' * indent_level):
            if 'def ' in line or 'async def ' in line:
                enhanced_end = i
                break

if enhanced_start and not enhanced_end:
    enhanced_end = len(lines)

if enhanced_start:
    print(f"Fixing lines {enhanced_start+1} to {enhanced_end}")
    
    # Reduce indentation by 4 spaces for these lines
    for i in range(enhanced_start, enhanced_end):
        if lines[i].startswith(' ' * indent_level):
            lines[i] = lines[i][4:]  # Remove 4 spaces
    
    with open('main.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Fixed indentation!")
else:
    print("⚠️ Could not find the method. Let's check manually...")
