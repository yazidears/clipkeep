#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import requests
import pyperclip
import socketio

CONFIG_FILE = os.path.expanduser("~/.clipkeep_config.json")
SERVER_URL = "http://clipkeep.yzde.es"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Error reading config:", e)
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f)
    except Exception as e:
        print("Error saving config:", e)

def setkey(passkey):
    cfg = load_config()
    cfg["passkey"] = passkey
    # Set a default device name if not already set
    cfg.setdefault("device", os.uname().nodename if hasattr(os, "uname") else "unknown")
    save_config(cfg)
    print("Passkey set.")

def add_clip(text, expire_in):
    cfg = load_config()
    passkey = cfg.get("passkey")
    if not passkey:
        print("Error: Missing passkey. Run 'clipkeep setkey <YOUR_PASSKEY>' first.")
        sys.exit(1)
    data = {
        "passkey": passkey,
        "text": text,
        "device": cfg.get("device", "unknown")
    }
    if expire_in is not None:
        data["expire_in"] = expire_in
    r = requests.post(f"{SERVER_URL}/clipboard", json=data)
    if r.ok:
        print("Clipboard text added.")
    else:
        print("Error:", r.json())

def get_entries(limit):
    cfg = load_config()
    passkey = cfg.get("passkey")
    if not passkey:
        print("Error: Missing passkey. Run 'clipkeep setkey <YOUR_PASSKEY>' first.")
        sys.exit(1)
    r = requests.get(f"{SERVER_URL}/clipboard", params={"passkey": passkey, "limit": limit})
    if r.ok:
        entries = r.json().get("entries", [])
        for entry in entries:
            print(f"{entry['id']}: {entry['text']} (from {entry.get('device','unknown')})")
    else:
        print("Error:", r.json())

def get_entry(entry_id):
    cfg = load_config()
    passkey = cfg.get("passkey")
    if not passkey:
        print("Error: Missing passkey. Run 'clipkeep setkey <YOUR_PASSKEY>' first.")
        sys.exit(1)
    r = requests.get(f"{SERVER_URL}/clipboard/entry/{entry_id}", params={"passkey": passkey})
    if r.ok:
        entry = r.json().get("entry")
        print(f"{entry['id']}: {entry['text']} (from {entry.get('device','unknown')})")
    else:
        print("Error:", r.json())

def clear_entries():
    cfg = load_config()
    passkey = cfg.get("passkey")
    if not passkey:
        print("Error: Missing passkey. Run 'clipkeep setkey <YOUR_PASSKEY>' first.")
        sys.exit(1)
    r = requests.delete(f"{SERVER_URL}/clipboard", json={"passkey": passkey, "device": cfg.get("device", "unknown")})
    if r.ok:
        print("Clipboard cleared on server.")
    else:
        print("Error:", r.json())

def paste_latest():
    cfg = load_config()
    passkey = cfg.get("passkey")
    if not passkey:
        print("Error: Missing passkey. Run 'clipkeep setkey <YOUR_PASSKEY>' first.")
        sys.exit(1)
    r = requests.get(f"{SERVER_URL}/clipboard", params={"passkey": passkey, "limit": 1})
    if r.ok:
        entries = r.json().get("entries", [])
        if entries:
            latest = entries[-1]
            pyperclip.copy(latest["text"])
            print("Latest clipboard text copied to local clipboard.")
        else:
            print("No entries found.")
    else:
        print("Error:", r.json())

def watch_clipboard():
    cfg = load_config()
    passkey = cfg.get("passkey")
    if not passkey:
        print("Error: Missing passkey. Run 'clipkeep setkey <YOUR_PASSKEY>' first.")
        sys.exit(1)
    sio = socketio.Client()

    @sio.event
    def connect():
        sio.emit("join", {"passkey": passkey, "device": cfg.get("device", "unknown")})

    @sio.on("clipboard_update")
    def on_update(data):
        pyperclip.copy(data["text"])
        print("Clipboard updated from network:", data["text"])

    sio.connect(SERVER_URL)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        sio.disconnect()

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_setkey = subparsers.add_parser("setkey", help="Set your passkey for syncing")
    parser_setkey.add_argument("passkey", help="Your unique passkey")

    parser_add = subparsers.add_parser("add", help="Add a clipboard entry")
    parser_add.add_argument("text", nargs="?", help="Text to add. If not provided, uses clipboard content")
    parser_add.add_argument("--expire", type=float, default=None, help="Expiration time in seconds")

    parser_list = subparsers.add_parser("list", help="List recent clipboard entries")
    parser_list.add_argument("--limit", type=int, default=10, help="Number of entries to list")

    parser_get = subparsers.add_parser("get", help="Get a specific clipboard entry")
    parser_get.add_argument("id", type=int, help="Entry ID")

    subparsers.add_parser("clear", help="Clear clipboard entries on the server")
    subparsers.add_parser("paste", help="Paste the latest clipboard entry")
    subparsers.add_parser("watch", help="Watch for clipboard updates in real time")

    args = parser.parse_args()

    if args.command == "setkey":
        setkey(args.passkey)
    elif args.command == "add":
        text = args.text if args.text is not None else pyperclip.paste()
        add_clip(text, args.expire)
    elif args.command == "list":
        get_entries(args.limit)
    elif args.command == "get":
        get_entry(args.id)
    elif args.command == "clear":
        clear_entries()
    elif args.command == "paste":
        paste_latest()
    elif args.command == "watch":
        watch_clipboard()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
