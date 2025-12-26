with open('main.py', 'r') as f:
    lines = f.readlines()

# We need to fix the except block. Let's find it first
for i in range(len(lines)):
    if 'except ImportError as e:' in lines[i]:
        print(f"Found except at line {i+1}")
        # Fix this line and the next few lines
        # Line with 'except' should have 8 spaces if 'try' has 4
        lines[i] = '    except ImportError as e:\n'
        
        # Next line (comment) should have 12 spaces
        if i+1 < len(lines):
            lines[i+1] = '        # Fallback to original database if import fails\n'
        
        # Next line (logger) should have 12 spaces
        if i+2 < len(lines) and 'logger.warning' in lines[i+2]:
            lines[i+2] = '        logger.warning(f"⚠️ Could not import Indian Service Manager: {e}")\n'
        
        # Empty line after that
        if i+3 < len(lines):
            lines[i+3] = '\n'
        
        # self.service_database line should have 12 spaces
        if i+4 < len(lines) and 'self.service_database = {' in lines[i+4]:
            lines[i+4] = '        self.service_database = {\n'
        
        # Dictionary items should have 16 spaces
        j = i+5
        while j < len(lines) and ('\'' in lines[j] or '"' in lines[j]):
            lines[j] = '            ' + lines[j].lstrip()
            j += 1
        
        break

with open('main.py', 'w') as f:
    f.writelines(lines)
print("Fixed!")
