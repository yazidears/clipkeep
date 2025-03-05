import argparse
import json
import os
import sys
import time
import requests
import pyperclip
import socketio

CONFIG_FILE = os.path.expanduser("~/.clipkeep_config.json")
SERVER_URL = "http://clipkeep.yzde.es"  # Update to your deployed server URL

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f)

def setkey(passkey):
    cfg = load_config()
    cfg["passkey"] = passkey
    cfg.setdefault("device", os.uname().nodename if hasattr(os, "uname") else "unknown")
    save_config(cfg)
    print("Passkey set.")

def add_clip(text, expire_in):
    cfg = load_config()
    passkey = cfg.get("passkey")
    if not passkey:
        print("Set passkey first using 'clipkeep setkey <YOUR_PASSKEY>'")
        sys.exit(1)
    data = {"passkey": passkey, "text": text, "device": cfg.get("device", "unknown")}
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
        print("Set passkey first using 'clipkeep setkey <YOUR_PASSKEY>'")
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
        print("Set passkey first using 'clipkeep setkey <YOUR_PASSKEY>'")
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
        print("Set passkey first using 'clipkeep setkey <YOUR_PASSKEY>'")
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
        print("Set passkey first using 'clipkeep setkey <YOUR_PASSKEY>'")
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
        print("Set passkey first using 'clipkeep setkey <YOUR_PASSKEY>'")
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
    subparsers = parser.add_subparsers(dest="command")
    p_setkey = subparsers.add_parser("setkey")
    p_setkey.add_argument("passkey")
    p_add = subparsers.add_parser("add")
    p_add.add_argument("text", nargs="?", default=None)
    p_add.add_argument("--expire", type=float, default=None)
    p_list = subparsers.add_parser("list")
    p_list.add_argument("--limit", type=int, default=10)
    p_get = subparsers.add_parser("get")
    p_get.add_argument("id", type=int)
    subparsers.add_parser("clear")
    subparsers.add_parser("paste")
    subparsers.add_parser("watch")
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
