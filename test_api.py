#!/usr/bin/env python
"""Test script to verify Pokemon TCG API configuration."""

import os
from dotenv import load_dotenv
from pokemontcgsdk import Card, RestClient

print("=" * 60)
print("Pokemon TCG API Configuration Test")
print("=" * 60)

# Load environment
load_dotenv()

# Check for API key
api_key = os.getenv('POKEMON_TCG_API_KEY', '')

print(f"\n1. API Key Status:")
if api_key:
    print(f"   ✓ API key found (length: {len(api_key)})")
    print(f"   Key preview: {api_key[:8]}..." if len(api_key) > 8 else f"   Key: {api_key}")
else:
    print(f"   ✗ No API key found!")
    print(f"   Please add your key to .env file:")
    print(f"   POKEMON_TCG_API_KEY=your_key_here")

# Configure SDK
if api_key:
    print(f"\n2. Configuring Pokemon TCG SDK...")
    RestClient.configure(api_key)
    print(f"   ✓ SDK configured")
else:
    print(f"\n2. Skipping SDK configuration (no API key)")

# Test API call
print(f"\n3. Testing API Search...")
try:
    results = Card.where(q='name:"Pikachu"', pageSize=3)

    cards = list(results)
    print(f"   ✓ Search successful!")
    print(f"   Found {len(cards)} cards:")

    for i, card in enumerate(cards[:3], 1):
        print(f"   {i}. {card.name} ({card.set.name})")

        # Check for price data
        if hasattr(card, 'tcgplayer') and card.tcgplayer:
            if hasattr(card.tcgplayer, 'prices') and card.tcgplayer.prices:
                print(f"      Has price data: Yes")
            else:
                print(f"      Has price data: No")
        else:
            print(f"      Has price data: No")

except Exception as e:
    print(f"   ✗ Search failed!")
    print(f"   Error type: {type(e).__name__}")

    # Check for 403 error
    if hasattr(e, '__context__') and hasattr(e.__context__, 'code'):
        if e.__context__.code == 403:
            print(f"   Error: 403 Forbidden - Invalid or missing API key")
            print(f"\n   Get a free API key at: https://dev.pokemontcg.io/")
        else:
            print(f"   HTTP Error {e.__context__.code}: {e.__context__.reason}")
    else:
        print(f"   Error details: {e}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
