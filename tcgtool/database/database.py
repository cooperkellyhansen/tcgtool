"""Database connection and operations."""

from pathlib import Path
from typing import Optional, List
from datetime import datetime

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .models import Base, Card, PriceHistory, Collection, Alert
from ..config import config


class Database:
    """Database manager for the TCG tool."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = config.database_path

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create engine
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False
        )

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine)

        # Create tables
        self.create_tables()

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    # Card operations
    def add_card(self, card_data: dict) -> Card:
        """Add or update a card in the database.

        Args:
            card_data: Dictionary containing card data

        Returns:
            Card object
        """
        with self.get_session() as session:
            card = session.query(Card).filter_by(id=card_data['id']).first()

            if card:
                # Update existing card
                for key, value in card_data.items():
                    setattr(card, key, value)
                card.updated_at = datetime.utcnow()
            else:
                # Create new card
                card = Card(**card_data)
                session.add(card)

            session.commit()
            session.refresh(card)
            return card

    def get_card(self, card_id: str) -> Optional[Card]:
        """Get a card by ID.

        Args:
            card_id: Card ID

        Returns:
            Card object or None
        """
        with self.get_session() as session:
            return session.query(Card).filter_by(id=card_id).first()

    def search_cards(self, query: str, limit: int = 20) -> List[Card]:
        """Search for cards by name.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of Card objects
        """
        with self.get_session() as session:
            return session.query(Card).filter(
                Card.name.ilike(f'%{query}%')
            ).limit(limit).all()

    # Price history operations
    def add_price(self, card_id: str, price_data: dict) -> PriceHistory:
        """Add a price record.

        Args:
            card_id: Card ID
            price_data: Dictionary containing price data

        Returns:
            PriceHistory object
        """
        with self.get_session() as session:
            price = PriceHistory(card_id=card_id, **price_data)
            session.add(price)
            session.commit()
            session.refresh(price)
            return price

    def get_price_history(self, card_id: str, limit: int = 100) -> List[PriceHistory]:
        """Get price history for a card.

        Args:
            card_id: Card ID
            limit: Maximum number of records

        Returns:
            List of PriceHistory objects
        """
        with self.get_session() as session:
            return session.query(PriceHistory).filter_by(
                card_id=card_id
            ).order_by(desc(PriceHistory.recorded_at)).limit(limit).all()

    def get_latest_price(self, card_id: str) -> Optional[PriceHistory]:
        """Get the latest price for a card.

        Args:
            card_id: Card ID

        Returns:
            PriceHistory object or None
        """
        with self.get_session() as session:
            return session.query(PriceHistory).filter_by(
                card_id=card_id
            ).order_by(desc(PriceHistory.recorded_at)).first()

    # Collection operations
    def add_to_collection(self, card_id: str, collection_data: dict) -> Collection:
        """Add a card to the collection.

        Args:
            card_id: Card ID
            collection_data: Dictionary containing collection data

        Returns:
            Collection object
        """
        with self.get_session() as session:
            item = Collection(card_id=card_id, **collection_data)
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def get_collection(self) -> List[Collection]:
        """Get all items in the collection.

        Returns:
            List of Collection objects
        """
        with self.get_session() as session:
            return session.query(Collection).all()

    def remove_from_collection(self, collection_id: int) -> bool:
        """Remove an item from the collection.

        Args:
            collection_id: Collection item ID

        Returns:
            True if successful, False otherwise
        """
        with self.get_session() as session:
            item = session.query(Collection).filter_by(id=collection_id).first()
            if item:
                session.delete(item)
                session.commit()
                return True
            return False

    # Alert operations
    def add_alert(self, card_id: str, alert_data: dict) -> Alert:
        """Add a price alert.

        Args:
            card_id: Card ID
            alert_data: Dictionary containing alert data

        Returns:
            Alert object
        """
        with self.get_session() as session:
            alert = Alert(card_id=card_id, **alert_data)
            session.add(alert)
            session.commit()
            session.refresh(alert)
            return alert

    def get_alerts(self, enabled_only: bool = True) -> List[Alert]:
        """Get all alerts.

        Args:
            enabled_only: Only return enabled alerts

        Returns:
            List of Alert objects
        """
        with self.get_session() as session:
            query = session.query(Alert)
            if enabled_only:
                query = query.filter_by(enabled=True)
            return query.all()

    def remove_alert(self, alert_id: int) -> bool:
        """Remove an alert.

        Args:
            alert_id: Alert ID

        Returns:
            True if successful, False otherwise
        """
        with self.get_session() as session:
            alert = session.query(Alert).filter_by(id=alert_id).first()
            if alert:
                session.delete(alert)
                session.commit()
                return True
            return False


# Global database instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get the global database instance.

    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
