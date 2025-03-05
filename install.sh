#!/usr/bin/env bash
set -e

# Check for required commands: python3, pip3, curl
for cmd in python3 pip3 curl; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "Error: $cmd is not installed. Please install $cmd and try again."
    exit 1
  fi
done

# Define variables
CLIENT_URL="https://raw.githubusercontent.com/yazidears/clipkeep/refs/heads/main/clipkeep.py"
INSTALL_DIR="$HOME/.local/bin"
INSTALL_FILE="$INSTALL_DIR/clipkeep"

# Create the installation directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Download the client code to a temporary file
TEMP_FILE=$(mktemp)
echo "Downloading clipkeep client..."
curl -sSL "$CLIENT_URL" -o "$TEMP_FILE"

# Ensure the file has a proper shebang; if not, prepend it
if ! head -n 1 "$TEMP_FILE" | grep -q "^#!"; then
  echo "Adding shebang to the client code..."
  sed -i '1s;^;#!/usr/bin/env python3\n;' "$TEMP_FILE"
fi

# Move the file to the installation directory and make it executable
mv "$TEMP_FILE" "$INSTALL_FILE"
chmod +x "$INSTALL_FILE"
echo "Client installed to $INSTALL_FILE"

# Install required Python dependencies locally
echo "Installing required Python packages..."
pip3 install --upgrade --user requests pyperclip python-socketio

# Ensure that INSTALL_DIR is in the user's PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
  echo "Warning: $INSTALL_DIR is not in your PATH."
  SHELL_RC=""
  if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
  elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
  fi
  if [ -n "$SHELL_RC" ]; then
    echo "Adding $INSTALL_DIR to PATH in $SHELL_RC"
    echo "export PATH=\$PATH:$INSTALL_DIR" >> "$SHELL_RC"
    echo "Please run 'source $SHELL_RC' or restart your terminal."
  else
    echo "Please add $INSTALL_DIR to your PATH manually."
  fi
fi

# Test the server connection by calling the /ping endpoint
echo "Testing connection to the server..."
PING_OUTPUT=$(curl -sSL http://clipkeep.yzde.es/ping)
if echo "$PING_OUTPUT" | grep -q '"status": "ok"'; then
  echo "Server connection successful: $PING_OUTPUT"
else
  echo "Warning: Unable to connect to the server. Please check your network or server status."
fi

echo "clipkeep installed successfully! You can now run 'clipkeep' from your terminal."
