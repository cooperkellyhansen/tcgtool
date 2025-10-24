"""Price fetching and tracking functionality."""

from datetime import datetime
from typing import Optional, Dict, Any
from pokemontcgsdk import Card as SDKCard

from ..database import get_database, PriceHistory
from .pokemon_tcg import PokemonTCGAPI


class PriceFetcher:
    """Fetch and track card prices."""

    def __init__(self):
        """Initialize the price fetcher."""
        self.db = get_database()
        self.api = PokemonTCGAPI()

    def fetch_and_store_price(self, card_id: str) -> Optional[PriceHistory]:
        """Fetch current price and store in database.

        Args:
            card_id: Card ID

        Returns:
            PriceHistory object or None
        """
        try:
            # Fetch card from API
            sdk_card = SDKCard.find(card_id)
            if not sdk_card:
                print(f"Card {card_id} not found")
                return None

            # Extract price data
            price_data = self.api.get_card_prices_from_api(sdk_card)
            if not price_data:
                print(f"No price data available for card {card_id}")
                return None

            # Add marketplace and currency
            price_data['marketplace'] = 'tcgplayer'
            price_data['currency'] = 'USD'
            price_data['recorded_at'] = datetime.utcnow()

            # Store in database
            price = self.db.add_price(card_id, price_data)
            print(f"Stored price for {card_id}: ${price_data.get('market_price', 'N/A')}")

            return price

        except Exception as e:
            # Check if it's a 403 error (missing API key)
            try:
                error_msg = repr(e)
            except:
                error_msg = type(e).__name__

            if '403' in error_msg or 'Forbidden' in error_msg:
                print("\n⚠️  API Key Required!")
                print("Get a free key at: https://dev.pokemontcg.io/")
            else:
                print(f"Error fetching price for {card_id}")
            return None

    def get_price_summary(self, card_id: str) -> Dict[str, Any]:
        """Get price summary for a card.

        Args:
            card_id: Card ID

        Returns:
            Dictionary with price summary
        """
        # Get card
        card = self.db.get_card(card_id)
        if not card:
            return {'error': 'Card not found'}

        # Get latest price
        latest_price = self.db.get_latest_price(card_id)

        # Get price history
        history = self.db.get_price_history(card_id, limit=30)

        # Calculate statistics
        if history:
            prices = [p.market_price for p in history if p.market_price]
            avg_price = sum(prices) / len(prices) if prices else None
            min_price = min(prices) if prices else None
            max_price = max(prices) if prices else None

            # Calculate price change
            if len(prices) >= 2:
                price_change = prices[0] - prices[-1]
                price_change_pct = (price_change / prices[-1] * 100) if prices[-1] else 0
            else:
                price_change = None
                price_change_pct = None
        else:
            avg_price = None
            min_price = None
            max_price = None
            price_change = None
            price_change_pct = None

        return {
            'card_name': card.name,
            'card_set': card.set_name,
            'current_price': latest_price.market_price if latest_price else None,
            'low_price': latest_price.low_price if latest_price else None,
            'high_price': latest_price.high_price if latest_price else None,
            'avg_price_30d': avg_price,
            'min_price_30d': min_price,
            'max_price_30d': max_price,
            'price_change': price_change,
            'price_change_pct': price_change_pct,
            'last_updated': latest_price.recorded_at if latest_price else None,
            'data_points': len(history),
        }

    def update_all_tracked_cards(self) -> int:
        """Update prices for all cards in the database.

        Returns:
            Number of cards updated
        """
        # Get all collection items
        collection = self.db.get_collection()

        updated = 0
        for item in collection:
            if self.fetch_and_store_price(item.card_id):
                updated += 1

        # Get all alert cards
        alerts = self.db.get_alerts()
        alert_card_ids = {alert.card_id for alert in alerts}

        for card_id in alert_card_ids:
            # Skip if already updated
            if any(item.card_id == card_id for item in collection):
                continue

            if self.fetch_and_store_price(card_id):
                updated += 1

        return updated

    def compare_marketplaces(self, card_id: str) -> Dict[str, Any]:
        """Compare prices across different marketplaces.

        Args:
            card_id: Card ID

        Returns:
            Dictionary with marketplace comparison
        """
        # For now, we only have TCGPlayer
        # This can be extended to include CardMarket, eBay, etc.

        latest_price = self.db.get_latest_price(card_id)
        if not latest_price:
            return {'error': 'No price data available'}

        return {
            'tcgplayer': {
                'market_price': latest_price.market_price,
                'low_price': latest_price.low_price,
                'high_price': latest_price.high_price,
                'last_updated': latest_price.recorded_at,
            }
            # Add more marketplaces here
        }
