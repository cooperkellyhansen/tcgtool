"""Price alert management."""

from datetime import datetime
from typing import List, Dict, Any

from ..database import get_database, Alert
from ..api import PriceFetcher


class AlertManager:
    """Manage price alerts."""

    def __init__(self):
        """Initialize the alert manager."""
        self.db = get_database()
        self.price_fetcher = PriceFetcher()

    def add_alert(
        self,
        card_id: str,
        threshold_price: float,
        condition: str = 'below'
    ) -> Alert:
        """Add a price alert.

        Args:
            card_id: Card ID
            threshold_price: Price threshold
            condition: 'above' or 'below'

        Returns:
            Alert object
        """
        alert_data = {
            'threshold_price': threshold_price,
            'condition': condition,
            'enabled': True,
        }

        return self.db.add_alert(card_id, alert_data)

    def remove_alert(self, alert_id: int) -> bool:
        """Remove an alert.

        Args:
            alert_id: Alert ID

        Returns:
            True if successful
        """
        return self.db.remove_alert(alert_id)

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get all alerts with card details.

        Returns:
            List of alert dictionaries
        """
        alerts = self.db.get_alerts(enabled_only=False)

        result = []
        for alert in alerts:
            card = self.db.get_card(alert.card_id)
            latest_price = self.db.get_latest_price(alert.card_id)

            result.append({
                'id': alert.id,
                'card_id': alert.card_id,
                'card_name': card.name if card else 'Unknown',
                'set_name': card.set_name if card else None,
                'threshold_price': alert.threshold_price,
                'condition': alert.condition,
                'current_price': latest_price.market_price if latest_price else None,
                'enabled': alert.enabled,
                'last_triggered': alert.last_triggered,
                'triggered_count': alert.triggered_count,
                'created_at': alert.created_at,
            })

        return result

    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all alerts and return triggered ones.

        Returns:
            List of triggered alerts
        """
        alerts = self.db.get_alerts(enabled_only=True)
        triggered = []

        for alert in alerts:
            # Fetch latest price
            price = self.price_fetcher.fetch_and_store_price(alert.card_id)
            if not price or not price.market_price:
                continue

            # Check condition
            is_triggered = False
            if alert.condition == 'below' and price.market_price <= alert.threshold_price:
                is_triggered = True
            elif alert.condition == 'above' and price.market_price >= alert.threshold_price:
                is_triggered = True

            if is_triggered:
                # Update alert
                with self.db.get_session() as session:
                    db_alert = session.query(Alert).filter_by(id=alert.id).first()
                    if db_alert:
                        db_alert.last_triggered = datetime.utcnow()
                        db_alert.triggered_count += 1
                        session.commit()

                # Get card details
                card = self.db.get_card(alert.card_id)

                triggered.append({
                    'alert_id': alert.id,
                    'card_id': alert.card_id,
                    'card_name': card.name if card else 'Unknown',
                    'threshold_price': alert.threshold_price,
                    'current_price': price.market_price,
                    'condition': alert.condition,
                })

        return triggered

    def notify(self, triggered_alerts: List[Dict[str, Any]]):
        """Send notifications for triggered alerts.

        Args:
            triggered_alerts: List of triggered alert dictionaries
        """
        if not triggered_alerts:
            return

        print("\n🔔 PRICE ALERTS TRIGGERED:")
        print("=" * 60)

        for alert in triggered_alerts:
            print(f"\n{alert['card_name']}")
            print(f"  Threshold: ${alert['threshold_price']:.2f} ({alert['condition']})")
            print(f"  Current Price: ${alert['current_price']:.2f}")

        print("\n" + "=" * 60)

    def run_alert_check(self):
        """Run alert check and send notifications."""
        triggered = self.check_alerts()
        self.notify(triggered)
        return triggered
