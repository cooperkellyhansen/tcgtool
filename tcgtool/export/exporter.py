"""Data export functionality for Power BI integration."""

import csv
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

from ..database import get_database
from ..collection import CollectionManager
from ..analysis import MarketAnalyzer
from ..config import config


class DataExporter:
    """Export data in various formats for Power BI and other tools."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the data exporter.

        Args:
            output_dir: Output directory for exports
        """
        self.db = get_database()
        self.collection_manager = CollectionManager()
        self.analyzer = MarketAnalyzer()

        self.output_dir = Path(output_dir) if output_dir else config.export_directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_collection_csv(self, filename: Optional[str] = None) -> str:
        """Export collection to CSV for Power BI.

        Args:
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'collection_{timestamp}.csv'

        output_path = self.output_dir / filename

        collection = self.collection_manager.get_collection()

        if not collection:
            print("No collection data to export")
            return str(output_path)

        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=collection[0].keys())
            writer.writeheader()
            writer.writerows(collection)

        print(f"Collection exported to {output_path}")
        return str(output_path)

    def export_price_history_csv(self, filename: Optional[str] = None) -> str:
        """Export price history to CSV for Power BI.

        Args:
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'price_history_{timestamp}.csv'

        output_path = self.output_dir / filename

        # Get all price history
        with self.db.get_session() as session:
            from ..database.models import PriceHistory, Card

            query = session.query(
                PriceHistory.id,
                PriceHistory.card_id,
                Card.name.label('card_name'),
                Card.set_name,
                Card.rarity,
                PriceHistory.market_price,
                PriceHistory.low_price,
                PriceHistory.mid_price,
                PriceHistory.high_price,
                PriceHistory.marketplace,
                PriceHistory.currency,
                PriceHistory.recorded_at
            ).join(Card, PriceHistory.card_id == Card.id)

            results = query.all()

            if not results:
                print("No price history data to export")
                return str(output_path)

            # Convert to list of dictionaries
            data = [
                {
                    'id': r.id,
                    'card_id': r.card_id,
                    'card_name': r.card_name,
                    'set_name': r.set_name,
                    'rarity': r.rarity,
                    'market_price': r.market_price,
                    'low_price': r.low_price,
                    'mid_price': r.mid_price,
                    'high_price': r.high_price,
                    'marketplace': r.marketplace,
                    'currency': r.currency,
                    'recorded_at': r.recorded_at.isoformat() if r.recorded_at else None,
                }
                for r in results
            ]

            # Write to CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            print(f"Price history exported to {output_path}")
            return str(output_path)

    def export_cards_csv(self, filename: Optional[str] = None) -> str:
        """Export all cards to CSV.

        Args:
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'cards_{timestamp}.csv'

        output_path = self.output_dir / filename

        with self.db.get_session() as session:
            from ..database.models import Card

            cards = session.query(Card).all()

            if not cards:
                print("No card data to export")
                return str(output_path)

            # Convert to list of dictionaries
            data = [
                {
                    'id': c.id,
                    'name': c.name,
                    'set_name': c.set_name,
                    'set_id': c.set_id,
                    'number': c.number,
                    'rarity': c.rarity,
                    'artist': c.artist,
                    'card_type': c.card_type,
                    'supertype': c.supertype,
                    'hp': c.hp,
                    'release_date': c.release_date,
                    'image_url': c.image_url,
                }
                for c in cards
            ]

            # Write to CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            print(f"Cards exported to {output_path}")
            return str(output_path)

    def export_trending_csv(self, days: int = 30, filename: Optional[str] = None) -> str:
        """Export trending cards analysis to CSV.

        Args:
            days: Number of days to analyze
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'trending_{timestamp}.csv'

        output_path = self.output_dir / filename

        trending = self.analyzer.get_trending_cards(days=days)

        if not trending:
            print("No trending data to export")
            return str(output_path)

        # Write to CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=trending[0].keys())
            writer.writeheader()
            writer.writerows(trending)

        print(f"Trending cards exported to {output_path}")
        return str(output_path)

    def export_to_json(self, data: Any, filename: str) -> str:
        """Export data to JSON format.

        Args:
            data: Data to export
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"Data exported to {output_path}")
        return str(output_path)

    def export_powerbi_dataset(self) -> Dict[str, str]:
        """Export complete dataset for Power BI.

        This creates multiple CSV files optimized for Power BI:
        - Cards master table
        - Price history fact table
        - Collection items
        - Trending analysis

        Returns:
            Dictionary with paths to all exported files
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        print("Exporting Power BI dataset...")

        files = {
            'cards': self.export_cards_csv(f'powerbi_cards_{timestamp}.csv'),
            'price_history': self.export_price_history_csv(f'powerbi_prices_{timestamp}.csv'),
            'collection': self.export_collection_csv(f'powerbi_collection_{timestamp}.csv'),
            'trending': self.export_trending_csv(30, f'powerbi_trending_{timestamp}.csv'),
        }

        # Also export collection summary
        collection_value = self.collection_manager.get_collection_value()
        files['collection_summary'] = self.export_to_json(
            collection_value,
            f'powerbi_summary_{timestamp}.json'
        )

        print("\n✅ Power BI dataset exported successfully!")
        print(f"Files created in: {self.output_dir}")
        for name, path in files.items():
            print(f"  - {name}: {Path(path).name}")

        return files

    def export_to_excel(self, filename: Optional[str] = None) -> str:
        """Export all data to Excel workbook with multiple sheets.

        Args:
            filename: Output filename (optional)

        Returns:
            Path to exported file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'tcgtool_export_{timestamp}.xlsx'

        output_path = self.output_dir / filename

        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Collection sheet
                collection = self.collection_manager.get_collection()
                if collection:
                    df_collection = pd.DataFrame(collection)
                    df_collection.to_excel(writer, sheet_name='Collection', index=False)

                # Price history sheet
                with self.db.get_session() as session:
                    from ..database.models import PriceHistory, Card

                    query = session.query(
                        Card.name.label('card_name'),
                        Card.set_name,
                        PriceHistory.market_price,
                        PriceHistory.recorded_at
                    ).join(Card, PriceHistory.card_id == Card.id)

                    results = query.all()
                    if results:
                        df_prices = pd.DataFrame([
                            {
                                'card_name': r.card_name,
                                'set_name': r.set_name,
                                'price': r.market_price,
                                'date': r.recorded_at
                            }
                            for r in results
                        ])
                        df_prices.to_excel(writer, sheet_name='Price History', index=False)

                # Trending sheet
                trending = self.analyzer.get_trending_cards(days=30)
                if trending:
                    df_trending = pd.DataFrame(trending)
                    df_trending.to_excel(writer, sheet_name='Trending', index=False)

                # Collection summary sheet
                summary = self.collection_manager.get_collection_value()
                df_summary = pd.DataFrame([summary])
                df_summary.to_excel(writer, sheet_name='Summary', index=False)

            print(f"Excel workbook exported to {output_path}")
            return str(output_path)

        except ImportError:
            print("Error: openpyxl not installed. Install with: pip install openpyxl")
            return ""
