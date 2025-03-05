#!/usr/bin/env bash
set -e

if ! command -v python3 &> /dev/null; then
  echo "Error: python3 is not installed. Please install python3 and try again."
  exit 1
fi

if ! command -v pip3 &> /dev/null; then
  echo "Error: pip3 is not installed. Please install pip3 and try again."
  exit 1
fi

echo "Installing clipkeep..."

pip3 install --upgrade --user clipkeep || { echo "Installation failed!"; exit 1; }

USER_BASE=$(python3 -m site --user-base)
BIN_DIR="$USER_BASE/bin"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo "It seems $BIN_DIR is not in your PATH."
  SHELL_RC=""
  if [ -f ~/.bashrc ]; then
    SHELL_RC=~/.bashrc
  elif [ -f ~/.zshrc ]; then
    SHELL_RC=~/.zshrc
  fi
  if [ -n "$SHELL_RC" ]; then
    echo "Adding $BIN_DIR to PATH in $SHELL_RC"
    echo "export PATH=\$PATH:$BIN_DIR" >> "$SHELL_RC"
    echo "Please restart your terminal or run 'source $SHELL_RC' to update your PATH."
  else
    echo "Please add $BIN_DIR to your PATH."
  fi
fi

echo "clipkeep installed successfully!"
echo "You can now run 'clipkeep' to use the tool."
