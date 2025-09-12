#!/usr/bin/env python3
from dotenv import load_dotenv
from pathlib import Path

def load_environment():
    if load_dotenv():
        return

    script_dir = Path(__file__).parent
    parent_dir = script_dir.parent
    env_path = parent_dir / '.env'

    if env_path.exists():
        load_dotenv(env_path)

if __name__ == '__main__':
    from app.main import start_server
    load_environment()
    start_server()
