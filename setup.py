#!/usr/bin/env python3
"""
Quick setup script for Pokemon TCG Price Tool.

This script will help you get your FREE API key and configure the tool.
"""

import os
import sys
import webbrowser
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("  🎴 Pokemon TCG Price Tool - Quick Setup")
    print("="*70)

    # Check if .env exists and has key
    env_path = Path('.env')
    has_key = False

    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
            if 'POKEMON_TCG_API_KEY=' in content:
                for line in content.split('\n'):
                    if line.startswith('POKEMON_TCG_API_KEY='):
                        key = line.split('=', 1)[1].strip()
                        if key and key != 'your_api_key_here':
                            has_key = True
                            print(f"\n✓ API key already configured!")
                            break

    if has_key:
        print("\nYour API key is set up. Testing connection...")
        os.system('python test_api.py')
        return

    print("\n📋 Setup Steps:")
    print("\n1. Get your FREE API key from Pokemon TCG API")
    print("   This takes about 30 seconds...")

    response = input("\n   Ready to open the website? (y/n): ")

    if response.lower() == 'y':
        print("\n   Opening https://dev.pokemontcg.io/ in your browser...")
        webbrowser.open('https://dev.pokemontcg.io/')
        print("\n   Follow these steps on the website:")
        print("   • Click 'Get API Key' or 'Sign Up'")
        print("   • Create a free account")
        print("   • Copy your API key")

    print("\n" + "-"*70)
    api_key = input("\n2. Paste your API key here: ").strip()

    if not api_key:
        print("\n❌ No API key entered. Run this script again when you have your key.")
        sys.exit(1)

    # Create/update .env file
    env_content = f"""# Pokemon TCG API Configuration
# Get your free key at: https://dev.pokemontcg.io/

POKEMON_TCG_API_KEY={api_key}
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("\n✓ API key saved to .env file!")

    # Test the API
    print("\n3. Testing your API key...")
    print("-"*70)

    os.system('python test_api.py')

    print("\n" + "="*70)
    print("  Setup Complete! 🎉")
    print("="*70)
    print("\nYou can now use the tool:")
    print('  python -m tcgtool search "Charizard"')
    print('  python -m tcgtool search "Pikachu VMAX"')
    print("\nFor more commands, run:")
    print('  python -m tcgtool --help')
    print("\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled.")
        sys.exit(1)
