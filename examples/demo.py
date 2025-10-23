"""
Demo script showing how to use the Pokemon TCG Price Tool programmatically.

This script demonstrates the main features of the tool.
"""

import sys
from pathlib import Path

# Add parent directory to path to import tcgtool
sys.path.insert(0, str(Path(__file__).parent.parent))

from tcgtool.api import PokemonTCGAPI, PriceFetcher
from tcgtool.collection import CollectionManager
from tcgtool.alerts import AlertManager
from tcgtool.analysis import MarketAnalyzer
from tcgtool.export import DataExporter


def demo_search():
    """Demo: Search for cards."""
    print("\n" + "="*60)
    print("DEMO: Searching for Cards")
    print("="*60)

    api = PokemonTCGAPI()

    # Search for Charizard cards
    print("\nSearching for 'Charizard' cards...")
    cards = api.search_cards("Charizard", page_size=5)

    for card in cards:
        print(f"  - {card.name} ({card.set_name}) - ID: {card.id}")


def demo_prices():
    """Demo: Fetch and display prices."""
    print("\n" + "="*60)
    print("DEMO: Price Lookup")
    print("="*60)

    price_fetcher = PriceFetcher()

    # Example card ID (Charizard VSTAR)
    card_id = "swsh9-18"

    print(f"\nFetching price for card: {card_id}")
    price_fetcher.fetch_and_store_price(card_id)

    # Get price summary
    summary = price_fetcher.get_price_summary(card_id)

    if 'error' not in summary:
        print(f"\nCard: {summary['card_name']}")
        print(f"Set: {summary['card_set']}")
        print(f"Current Price: ${summary['current_price']:.2f}")
        print(f"Low: ${summary['low_price']:.2f}")
        print(f"High: ${summary['high_price']:.2f}")


def demo_collection():
    """Demo: Collection management."""
    print("\n" + "="*60)
    print("DEMO: Collection Management")
    print("="*60)

    manager = CollectionManager()

    # Add a card to collection
    card_id = "swsh9-18"
    print(f"\nAdding card to collection: {card_id}")

    manager.add_card(
        card_id=card_id,
        quantity=1,
        condition="Near Mint",
        purchase_price=35.00
    )

    # View collection
    print("\nCurrent Collection:")
    collection = manager.get_collection()

    for item in collection:
        print(f"  - {item['card_name']}")
        print(f"    Quantity: {item['quantity']}")
        print(f"    Purchase Price: ${item['purchase_price']:.2f}")
        print(f"    Current Price: ${item['current_price']:.2f}" if item['current_price'] else "    Current Price: N/A")

    # Get collection value
    stats = manager.get_collection_value()
    print(f"\nTotal Collection Value: ${stats['total_value']:.2f}")
    print(f"Total Cards: {stats['total_cards']}")


def demo_alerts():
    """Demo: Price alerts."""
    print("\n" + "="*60)
    print("DEMO: Price Alerts")
    print("="*60)

    manager = AlertManager()

    # Add an alert
    card_id = "swsh9-18"
    threshold = 30.00

    print(f"\nSetting up alert for card: {card_id}")
    print(f"Alert when price goes below: ${threshold}")

    manager.add_alert(card_id, threshold, condition='below')

    # View alerts
    print("\nActive Alerts:")
    alerts = manager.get_alerts()

    for alert in alerts:
        print(f"  - {alert['card_name']}")
        print(f"    Threshold: ${alert['threshold_price']:.2f} ({alert['condition']})")
        print(f"    Current: ${alert['current_price']:.2f}" if alert['current_price'] else "    Current: N/A")


def demo_analysis():
    """Demo: Market analysis."""
    print("\n" + "="*60)
    print("DEMO: Market Analysis")
    print("="*60)

    analyzer = MarketAnalyzer()

    # Get trending cards
    print("\nFetching trending cards (last 30 days)...")
    trending = analyzer.get_trending_cards(days=30)

    if trending:
        print("\nTop 5 Trending Cards:")
        for i, card in enumerate(trending[:5], 1):
            change = card['price_change_pct']
            direction = "↑" if change > 0 else "↓"
            print(f"  {i}. {card['card_name']}")
            print(f"     Change: {direction} {abs(change):.1f}%")
    else:
        print("  No trending data available yet. Add cards to collection and update prices.")


def demo_export():
    """Demo: Data export."""
    print("\n" + "="*60)
    print("DEMO: Data Export")
    print("="*60)

    exporter = DataExporter()

    print("\nExporting collection to CSV...")
    csv_path = exporter.export_collection_csv()
    print(f"  ✓ Exported to: {csv_path}")

    print("\nExporting complete Power BI dataset...")
    files = exporter.export_powerbi_dataset()
    print(f"  ✓ Exported {len(files)} files")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("Pokemon TCG Price Analysis Tool - Demo")
    print("="*60)
    print("\nThis demo will showcase the main features of the tool.")
    print("Note: Some features require an internet connection and API access.")

    demos = [
        ("Search", demo_search),
        ("Prices", demo_prices),
        ("Collection", demo_collection),
        ("Alerts", demo_alerts),
        ("Analysis", demo_analysis),
        ("Export", demo_export),
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n⚠ Error in {name} demo: {e}")

    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nFor more information, see:")
    print("  - README.md - Overview and quick start")
    print("  - USAGE.md - Detailed usage examples")
    print("  - POWERBI_GUIDE.md - Power BI integration guide")
    print("\nTo use the CLI:")
    print("  python -m tcgtool --help")


if __name__ == "__main__":
    main()
