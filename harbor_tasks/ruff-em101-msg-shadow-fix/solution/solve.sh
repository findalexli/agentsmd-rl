#!/bin/bash
# Gold solution - adds get_interface_ip function with a docstring to gradio/utils.py

cd /workspace/gradio

# Create the function at the beginning of utils.py after any imports
# Find a good place to add it - after the module docstring and imports

# Use sed to add the function after the module docstring line
cat > /tmp/new_function.py << 'EOF'
def get_interface_ip():
    """Get the IP address of the interface.

    Returns the IP address as a string.
    """
    pass


EOF

# Insert the function near the top of utils.py, after the module docstring
# First, find the line number of the first def or class
FIRST_DEF=$(grep -n "^def \|^class " gradio/utils.py | head -1 | cut -d: -f1)

# Insert the new function before the first def/class
head -n $((FIRST_DEF - 1)) gradio/utils.py > /tmp/utils_new.py
cat /tmp/new_function.py >> /tmp/utils_new.py
tail -n +$FIRST_DEF gradio/utils.py >> /tmp/utils_new.py
mv /tmp/utils_new.py gradio/utils.py

# Format the file to pass ruff check
python -m ruff format gradio/utils.py

echo "Added get_interface_ip function with docstring to gradio/utils.py"
