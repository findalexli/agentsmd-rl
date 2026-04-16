#!/bin/bash
# Gold solution - adds get_interface_ip function with a docstring to gradio/utils.py
# This implementation actually returns a valid IP address using socket

cd /workspace/gradio

# Create the function with a proper implementation that returns an IP address
cat > /tmp/new_function.py << 'FUNCODE'
import socket


def get_interface_ip():
    """Get the IP address of the interface.

    Returns the IP address as a string.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a public address to determine the interface IP
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


FUNCODE

# Find the line number of the first def or class
FIRST_DEF=$(grep -n "^def \|^class " gradio/utils.py | head -1 | cut -d: -f1)

# Insert the new function before the first def/class
head -n $((FIRST_DEF - 1)) gradio/utils.py > /tmp/utils_new.py
cat /tmp/new_function.py >> /tmp/utils_new.py
tail -n +$FIRST_DEF gradio/utils.py >> /tmp/utils_new.py
mv /tmp/utils_new.py gradio/utils.py

# Format the file to pass ruff check
python -m ruff format gradio/utils.py

echo "Added get_interface_ip function with docstring to gradio/utils.py"
