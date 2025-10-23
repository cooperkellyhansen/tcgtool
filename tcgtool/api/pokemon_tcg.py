"""Pokemon TCG API integration."""

import json
from typing import List, Optional, Dict, Any
from pokemontcgsdk import Card as SDKCard, Set
from pokemontcgsdk import RestClient

from ..config import config
from ..database import get_database, Card


class PokemonTCGAPI:
    """Pokemon TCG API client."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Pokemon TCG API client.

        Args:
            api_key: Pokemon TCG API key (optional but recommended)
        """
        self.api_key = api_key or config.pokemon_tcg_api_key

        if self.api_key:
            RestClient.configure(self.api_key)

        self.db = get_database()

    def search_cards(self, query: str, page_size: int = 20) -> List[Card]:
        """Search for cards by name.

        Args:
            query: Search query (card name)
            page_size: Number of results per page

        Returns:
            List of Card objects
        """
        try:
            # Search using Pokemon TCG SDK
            results = SDKCard.where(q=f'name:"{query}*"', pageSize=page_size)

            cards = []
            for sdk_card in results:
                card_data = self._convert_sdk_card(sdk_card)
                card = self.db.add_card(card_data)
                cards.append(card)

            return cards

        except Exception as e:
            print(f"Error searching cards: {e}")
            # Fallback to local database search
            return self.db.search_cards(query, limit=page_size)

    def get_card(self, card_id: str) -> Optional[Card]:
        """Get a card by ID.

        Args:
            card_id: Pokemon TCG API card ID

        Returns:
            Card object or None
        """
        try:
            # Try to get from database first
            card = self.db.get_card(card_id)
            if card:
                return card

            # Fetch from API if not in database
            sdk_card = SDKCard.find(card_id)
            if sdk_card:
                card_data = self._convert_sdk_card(sdk_card)
                return self.db.add_card(card_data)

        except Exception as e:
            print(f"Error fetching card: {e}")

        return None

    def get_card_with_price(self, card_id: str) -> Dict[str, Any]:
        """Get a card with its latest price.

        Args:
            card_id: Card ID

        Returns:
            Dictionary with card and price information
        """
        card = self.get_card(card_id)
        if not card:
            return {}

        price = self.db.get_latest_price(card_id)

        return {
            'card': card,
            'price': price,
            'market_price': price.market_price if price else None,
            'low_price': price.low_price if price else None,
            'high_price': price.high_price if price else None,
        }

    def get_sets(self) -> List[Set]:
        """Get all Pokemon TCG sets.

        Returns:
            List of Set objects
        """
        try:
            return Set.all()
        except Exception as e:
            print(f"Error fetching sets: {e}")
            return []

    def _convert_sdk_card(self, sdk_card: SDKCard) -> Dict[str, Any]:
        """Convert SDK card to database format.

        Args:
            sdk_card: Pokemon TCG SDK card object

        Returns:
            Dictionary of card data
        """
        # Get image URL
        image_url = None
        if hasattr(sdk_card, 'images') and sdk_card.images:
            image_url = sdk_card.images.get('large') or sdk_card.images.get('small')

        # Convert subtypes to JSON string
        subtypes = json.dumps(sdk_card.subtypes) if hasattr(sdk_card, 'subtypes') else None

        card_data = {
            'id': sdk_card.id,
            'name': sdk_card.name,
            'set_name': sdk_card.set.name if hasattr(sdk_card, 'set') else None,
            'set_id': sdk_card.set.id if hasattr(sdk_card, 'set') else None,
            'number': sdk_card.number if hasattr(sdk_card, 'number') else None,
            'rarity': sdk_card.rarity if hasattr(sdk_card, 'rarity') else None,
            'artist': sdk_card.artist if hasattr(sdk_card, 'artist') else None,
            'image_url': image_url,
            'card_type': sdk_card.supertype if hasattr(sdk_card, 'supertype') else None,
            'subtypes': subtypes,
            'supertype': sdk_card.supertype if hasattr(sdk_card, 'supertype') else None,
            'hp': int(sdk_card.hp) if hasattr(sdk_card, 'hp') and sdk_card.hp else None,
            'release_date': sdk_card.set.releaseDate if hasattr(sdk_card, 'set') and hasattr(sdk_card.set, 'releaseDate') else None,
        }

        return card_data

    def get_card_prices_from_api(self, sdk_card: SDKCard) -> Optional[Dict[str, float]]:
        """Extract price data from SDK card object.

        Args:
            sdk_card: Pokemon TCG SDK card object

        Returns:
            Dictionary with price data or None
        """
        if not hasattr(sdk_card, 'tcgplayer') or not sdk_card.tcgplayer:
            return None

        tcgplayer = sdk_card.tcgplayer
        if not hasattr(tcgplayer, 'prices') or not tcgplayer.prices:
            return None

        # Try to get normal/holofoil/reverseHolofoil prices
        prices = tcgplayer.prices

        # Get the first available price variant
        price_variant = None
        for variant in ['normal', 'holofoil', 'reverseHolofoil', 'unlimited', '1stEdition']:
            if hasattr(prices, variant):
                price_variant = getattr(prices, variant)
                break

        if not price_variant:
            return None

        return {
            'market_price': getattr(price_variant, 'market', None),
            'low_price': getattr(price_variant, 'low', None),
            'mid_price': getattr(price_variant, 'mid', None),
            'high_price': getattr(price_variant, 'high', None),
        }
