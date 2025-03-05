#!/usr/bin/env bash
set -e

# Check for python3
if ! command -v python3 &> /dev/null; then
  echo "Error: python3 is not installed. Please install python3 and try again."
  exit 1
fi

# Check for pip3
if ! command -v pip3 &> /dev/null; then
  echo "Error: pip3 is not installed. Please install pip3 and try again."
  exit 1
fi

# Define installation directory and file location
INSTALL_DIR="$HOME/.local/bin"
INSTALL_FILE="$INSTALL_DIR/clipkeep"

# Create the installation directory if it doesn't exist
mkdir -p "$INSTALL_DIR"

# Download the client code from GitHub
echo "Downloading clipkeep client from GitHub..."
curl -sSL https://raw.githubusercontent.com/yazidears/clipkeep/refs/heads/main/clipkeep.py -o "$INSTALL_FILE"

# Make the file executable
chmod +x "$INSTALL_FILE"

# Install required Python dependencies
echo "Installing required Python packages..."
pip3 install --upgrade --user requests pyperclip python-socketio

# Check if the installation directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
  echo "Warning: $INSTALL_DIR is not in your PATH."
  if [ -f "$HOME/.bashrc" ]; then
    echo "Adding $INSTALL_DIR to PATH in ~/.bashrc"
    echo "export PATH=\$PATH:$INSTALL_DIR" >> "$HOME/.bashrc"
    echo "Please run 'source ~/.bashrc' or restart your terminal."
  elif [ -f "$HOME/.zshrc" ]; then
    echo "Adding $INSTALL_DIR to PATH in ~/.zshrc"
    echo "export PATH=\$PATH:$INSTALL_DIR" >> "$HOME/.zshrc"
    echo "Please run 'source ~/.zshrc' or restart your terminal."
  else
    echo "Please add $INSTALL_DIR to your PATH manually."
  fi
fi

# Test connection to the server
echo "Testing connection to the server..."
PING_OUTPUT=$(curl -sSL http://clipkeep.yzde.es/ping)
if echo "$PING_OUTPUT" | grep -q '"status": "ok"'; then
  echo "Server connection successful: $PING_OUTPUT"
else
  echo "Warning: Unable to connect to the server. Please check your network or server status."
fi

echo "clipkeep installed successfully! You can now run 'clipkeep' to use the tool."
