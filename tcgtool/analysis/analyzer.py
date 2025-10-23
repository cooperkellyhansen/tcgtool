"""Market analysis functionality."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics

from ..database import get_database, PriceHistory


class MarketAnalyzer:
    """Analyze Pokemon TCG market trends."""

    def __init__(self):
        """Initialize the market analyzer."""
        self.db = get_database()

    def get_trending_cards(self, days: int = 30, min_data_points: int = 7) -> List[Dict[str, Any]]:
        """Get cards with significant price changes.

        Args:
            days: Number of days to analyze
            min_data_points: Minimum number of price records required

        Returns:
            List of trending cards
        """
        # Get all cards with price history
        with self.db.get_session() as session:
            # Get all unique card IDs with recent price data
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            price_records = session.query(PriceHistory).filter(
                PriceHistory.recorded_at >= cutoff_date
            ).all()

            # Group by card
            card_prices = {}
            for record in price_records:
                if record.card_id not in card_prices:
                    card_prices[record.card_id] = []
                if record.market_price:
                    card_prices[record.card_id].append({
                        'price': record.market_price,
                        'date': record.recorded_at
                    })

            # Analyze trends
            trending = []
            for card_id, prices in card_prices.items():
                if len(prices) < min_data_points:
                    continue

                # Sort by date
                prices.sort(key=lambda x: x['date'])

                # Calculate price change
                oldest_price = prices[0]['price']
                newest_price = prices[-1]['price']
                price_change = newest_price - oldest_price
                price_change_pct = (price_change / oldest_price * 100) if oldest_price > 0 else 0

                # Calculate volatility (standard deviation)
                price_values = [p['price'] for p in prices]
                volatility = statistics.stdev(price_values) if len(price_values) > 1 else 0
                volatility_pct = (volatility / statistics.mean(price_values) * 100) if price_values else 0

                # Get card details
                card = self.db.get_card(card_id)
                if not card:
                    continue

                trending.append({
                    'card_id': card_id,
                    'card_name': card.name,
                    'set_name': card.set_name,
                    'rarity': card.rarity,
                    'oldest_price': oldest_price,
                    'newest_price': newest_price,
                    'price_change': price_change,
                    'price_change_pct': price_change_pct,
                    'volatility': volatility,
                    'volatility_pct': volatility_pct,
                    'data_points': len(prices),
                    'days_tracked': days,
                })

            # Sort by absolute price change percentage
            trending.sort(key=lambda x: abs(x['price_change_pct']), reverse=True)

            return trending

    def get_card_volatility(self, card_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze price volatility for a specific card.

        Args:
            card_id: Card ID
            days: Number of days to analyze

        Returns:
            Dictionary with volatility metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.db.get_session() as session:
            prices = session.query(PriceHistory).filter(
                PriceHistory.card_id == card_id,
                PriceHistory.recorded_at >= cutoff_date,
                PriceHistory.market_price.isnot(None)
            ).order_by(PriceHistory.recorded_at).all()

            if len(prices) < 2:
                return {'error': 'Insufficient data'}

            price_values = [p.market_price for p in prices]

            mean_price = statistics.mean(price_values)
            std_dev = statistics.stdev(price_values)
            min_price = min(price_values)
            max_price = max(price_values)
            price_range = max_price - min_price

            # Calculate coefficient of variation (CV)
            cv = (std_dev / mean_price * 100) if mean_price > 0 else 0

            return {
                'card_id': card_id,
                'days_analyzed': days,
                'data_points': len(prices),
                'mean_price': mean_price,
                'std_dev': std_dev,
                'min_price': min_price,
                'max_price': max_price,
                'price_range': price_range,
                'coefficient_of_variation': cv,
                'volatility_rating': self._get_volatility_rating(cv),
            }

    def _get_volatility_rating(self, cv: float) -> str:
        """Get volatility rating based on coefficient of variation.

        Args:
            cv: Coefficient of variation

        Returns:
            Volatility rating string
        """
        if cv < 5:
            return 'Very Stable'
        elif cv < 10:
            return 'Stable'
        elif cv < 20:
            return 'Moderate'
        elif cv < 30:
            return 'Volatile'
        else:
            return 'Highly Volatile'

    def get_market_summary(self) -> Dict[str, Any]:
        """Get overall market summary.

        Returns:
            Dictionary with market statistics
        """
        with self.db.get_session() as session:
            # Get recent price data (last 24 hours)
            cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_prices = session.query(PriceHistory).filter(
                PriceHistory.recorded_at >= cutoff
            ).all()

            if not recent_prices:
                return {'error': 'No recent price data'}

            # Calculate statistics
            all_prices = [p.market_price for p in recent_prices if p.market_price]

            if not all_prices:
                return {'error': 'No valid price data'}

            return {
                'total_cards_tracked': len(set(p.card_id for p in recent_prices)),
                'total_price_updates': len(recent_prices),
                'average_card_price': statistics.mean(all_prices),
                'median_card_price': statistics.median(all_prices),
                'price_range': {
                    'min': min(all_prices),
                    'max': max(all_prices),
                },
                'last_updated': max(p.recorded_at for p in recent_prices),
            }
