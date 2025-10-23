"""Database models for the TCG tool."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Card(Base):
    """Card model representing a Pokemon TCG card."""

    __tablename__ = 'cards'

    id = Column(String, primary_key=True)  # Pokemon TCG API ID
    name = Column(String, nullable=False, index=True)
    set_name = Column(String)
    set_id = Column(String)
    number = Column(String)
    rarity = Column(String)
    artist = Column(String)
    image_url = Column(String)
    card_type = Column(String)  # Pokemon, Trainer, Energy
    subtypes = Column(String)  # JSON string of subtypes
    supertype = Column(String)
    hp = Column(Integer)
    release_date = Column(String)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="card", cascade="all, delete-orphan")
    collection_items = relationship("Collection", back_populates="card", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="card", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Card(id='{self.id}', name='{self.name}', set='{self.set_name}')>"


class PriceHistory(Base):
    """Price history model for tracking card prices over time."""

    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey('cards.id'), nullable=False, index=True)

    # Prices from different markets
    market_price = Column(Float)  # TCGPlayer market price
    low_price = Column(Float)     # Lowest available
    mid_price = Column(Float)     # Mid price
    high_price = Column(Float)    # Highest recent sale

    # Market metadata
    marketplace = Column(String, default='tcgplayer')  # tcgplayer, cardmarket, etc.
    currency = Column(String, default='USD')

    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    card = relationship("Card", back_populates="price_history")

    def __repr__(self):
        return f"<PriceHistory(card_id='{self.card_id}', price={self.market_price}, date='{self.recorded_at}')>"


class Collection(Base):
    """Collection model for tracking user's card collection."""

    __tablename__ = 'collection'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey('cards.id'), nullable=False, index=True)

    quantity = Column(Integer, default=1)
    condition = Column(String, default='Near Mint')  # Mint, Near Mint, Lightly Played, etc.
    purchase_price = Column(Float)
    purchase_date = Column(DateTime)
    notes = Column(Text)

    # Tracking
    added_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    card = relationship("Card", back_populates="collection_items")

    def __repr__(self):
        return f"<Collection(card_id='{self.card_id}', quantity={self.quantity})>"


class Alert(Base):
    """Alert model for price alerts."""

    __tablename__ = 'alerts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey('cards.id'), nullable=False, index=True)

    # Alert settings
    threshold_price = Column(Float, nullable=False)
    condition = Column(String, default='below')  # 'above' or 'below'
    enabled = Column(Boolean, default=True)

    # Notification
    last_triggered = Column(DateTime)
    triggered_count = Column(Integer, default=0)

    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    card = relationship("Card", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(card_id='{self.card_id}', threshold={self.threshold_price}, condition='{self.condition}')>"
