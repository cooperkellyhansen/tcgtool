"""Collection management functionality."""

from datetime import datetime
from typing import List, Dict, Any, Optional

from ..database import get_database, Collection, Card
from ..api import PriceFetcher


class CollectionManager:
    """Manage user's card collection."""

    def __init__(self):
        """Initialize the collection manager."""
        self.db = get_database()
        self.price_fetcher = PriceFetcher()

    def add_card(
        self,
        card_id: str,
        quantity: int = 1,
        condition: str = 'Near Mint',
        purchase_price: Optional[float] = None,
        purchase_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Collection:
        """Add a card to the collection.

        Args:
            card_id: Card ID
            quantity: Number of cards
            condition: Card condition
            purchase_price: Price paid for the card
            purchase_date: Date purchased
            notes: Additional notes

        Returns:
            Collection object
        """
        collection_data = {
            'quantity': quantity,
            'condition': condition,
            'purchase_price': purchase_price,
            'purchase_date': purchase_date,
            'notes': notes,
        }

        return self.db.add_to_collection(card_id, collection_data)

    def remove_card(self, collection_id: int) -> bool:
        """Remove a card from the collection.

        Args:
            collection_id: Collection item ID

        Returns:
            True if successful
        """
        return self.db.remove_from_collection(collection_id)

    def get_collection(self) -> List[Dict[str, Any]]:
        """Get all cards in the collection with current prices.

        Returns:
            List of dictionaries with collection items and prices
        """
        collection = self.db.get_collection()

        result = []
        for item in collection:
            # Get card details
            card = self.db.get_card(item.card_id)
            if not card:
                continue

            # Get latest price
            latest_price = self.db.get_latest_price(item.card_id)

            current_price = latest_price.market_price if latest_price else None
            total_value = current_price * item.quantity if current_price else None

            # Calculate profit/loss
            if item.purchase_price and current_price:
                profit_loss = (current_price - item.purchase_price) * item.quantity
                profit_loss_pct = ((current_price - item.purchase_price) / item.purchase_price * 100)
            else:
                profit_loss = None
                profit_loss_pct = None

            result.append({
                'id': item.id,
                'card_id': item.card_id,
                'card_name': card.name,
                'set_name': card.set_name,
                'number': card.number,
                'rarity': card.rarity,
                'quantity': item.quantity,
                'condition': item.condition,
                'purchase_price': item.purchase_price,
                'purchase_date': item.purchase_date,
                'current_price': current_price,
                'total_value': total_value,
                'profit_loss': profit_loss,
                'profit_loss_pct': profit_loss_pct,
                'notes': item.notes,
                'added_at': item.added_at,
            })

        return result

    def get_collection_value(self) -> Dict[str, Any]:
        """Get total collection value and statistics.

        Returns:
            Dictionary with collection statistics
        """
        collection = self.get_collection()

        total_cards = sum(item['quantity'] for item in collection)
        total_value = sum(item['total_value'] for item in collection if item['total_value'])
        total_invested = sum(
            item['purchase_price'] * item['quantity']
            for item in collection
            if item['purchase_price']
        )

        total_profit_loss = total_value - total_invested if total_invested else None
        total_profit_loss_pct = (
            (total_profit_loss / total_invested * 100) if total_invested and total_invested > 0 else None
        )

        # Top cards by value
        top_cards = sorted(
            [item for item in collection if item['total_value']],
            key=lambda x: x['total_value'],
            reverse=True
        )[:10]

        # Cards with biggest gains
        top_gains = sorted(
            [item for item in collection if item['profit_loss']],
            key=lambda x: x['profit_loss'],
            reverse=True
        )[:5]

        return {
            'total_cards': total_cards,
            'unique_cards': len(collection),
            'total_value': total_value,
            'total_invested': total_invested,
            'profit_loss': total_profit_loss,
            'profit_loss_pct': total_profit_loss_pct,
            'top_cards': top_cards,
            'top_gains': top_gains,
        }

    def update_collection_prices(self) -> int:
        """Update prices for all cards in collection.

        Returns:
            Number of cards updated
        """
        collection = self.db.get_collection()
        updated = 0

        for item in collection:
            if self.price_fetcher.fetch_and_store_price(item.card_id):
                updated += 1

        return updated

    def export_collection(self) -> List[Dict[str, Any]]:
        """Export collection data for external use.

        Returns:
            List of collection items with full details
        """
        return self.get_collection()
