"""Main CLI entry point for the TCG tool."""

import click
from datetime import datetime
from tabulate import tabulate
from colorama import init, Fore, Style

from .api import PokemonTCGAPI, PriceFetcher
from .collection import CollectionManager
from .alerts import AlertManager
from .analysis import MarketAnalyzer
from .export import DataExporter

# Initialize colorama for cross-platform color support
init()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Pokemon TCG Price Analysis Tool

    A comprehensive tool for tracking and analyzing Pokemon Trading Card Game prices
    with Power BI integration.
    """
    pass


# ============================================================================
# SEARCH COMMANDS
# ============================================================================

@cli.command()
@click.argument('query')
@click.option('--limit', default=10, help='Maximum number of results')
def search(query, limit):
    """Search for Pokemon cards by name."""
    api = PokemonTCGAPI()
    price_fetcher = PriceFetcher()

    print(f"\n🔍 Searching for: {query}\n")

    cards = api.search_cards(query, page_size=limit)

    if not cards:
        print(f"{Fore.YELLOW}No cards found.{Style.RESET_ALL}")
        return

    # Display results
    data = []
    for card in cards:
        # Fetch price
        price = price_fetcher.fetch_and_store_price(card.id)
        price_str = f"${price.market_price:.2f}" if price and price.market_price else "N/A"

        data.append([
            card.id,
            card.name,
            card.set_name or 'N/A',
            card.number or 'N/A',
            card.rarity or 'N/A',
            price_str
        ])

    headers = ['ID', 'Name', 'Set', 'Number', 'Rarity', 'Price']
    print(tabulate(data, headers=headers, tablefmt='grid'))


@cli.command()
@click.argument('card_id')
def price(card_id):
    """Get detailed price information for a card."""
    price_fetcher = PriceFetcher()

    print(f"\n💰 Fetching price data...\n")

    summary = price_fetcher.get_price_summary(card_id)

    if 'error' in summary:
        print(f"{Fore.RED}Error: {summary['error']}{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}Card:{Style.RESET_ALL} {summary['card_name']}")
    print(f"{Fore.CYAN}Set:{Style.RESET_ALL} {summary['card_set']}")
    print()
    print(f"{Fore.GREEN}Current Price:{Style.RESET_ALL} ${summary['current_price']:.2f}")
    print(f"  Low: ${summary['low_price']:.2f}")
    print(f"  High: ${summary['high_price']:.2f}")

    if summary['avg_price_30d']:
        print()
        print(f"{Fore.YELLOW}30-Day Statistics:{Style.RESET_ALL}")
        print(f"  Average: ${summary['avg_price_30d']:.2f}")
        print(f"  Min: ${summary['min_price_30d']:.2f}")
        print(f"  Max: ${summary['max_price_30d']:.2f}")

        if summary['price_change']:
            change_color = Fore.GREEN if summary['price_change'] > 0 else Fore.RED
            print(f"  Change: {change_color}{summary['price_change']:+.2f} ({summary['price_change_pct']:+.1f}%){Style.RESET_ALL}")

    print(f"\nData points: {summary['data_points']}")
    if summary['last_updated']:
        print(f"Last updated: {summary['last_updated']}")


# ============================================================================
# COLLECTION COMMANDS
# ============================================================================

@cli.group()
def collection():
    """Manage your card collection."""
    pass


@collection.command(name='add')
@click.argument('card_id')
@click.option('--quantity', '-q', default=1, help='Number of cards')
@click.option('--condition', '-c', default='Near Mint', help='Card condition')
@click.option('--price', '-p', type=float, help='Purchase price')
def collection_add(card_id, quantity, condition, price):
    """Add a card to your collection."""
    manager = CollectionManager()
    api = PokemonTCGAPI()

    # Fetch card details
    card = api.get_card(card_id)
    if not card:
        print(f"{Fore.RED}Card not found.{Style.RESET_ALL}")
        return

    # Add to collection
    manager.add_card(
        card_id=card_id,
        quantity=quantity,
        condition=condition,
        purchase_price=price,
        purchase_date=datetime.now() if price else None
    )

    print(f"{Fore.GREEN}✓{Style.RESET_ALL} Added {quantity}x {card.name} to collection")


@collection.command(name='list')
def collection_list():
    """List all cards in your collection."""
    manager = CollectionManager()

    collection = manager.get_collection()

    if not collection:
        print(f"{Fore.YELLOW}Your collection is empty.{Style.RESET_ALL}")
        return

    print(f"\n📦 Your Collection ({len(collection)} unique cards)\n")

    data = []
    for item in collection:
        current = f"${item['current_price']:.2f}" if item['current_price'] else "N/A"
        total = f"${item['total_value']:.2f}" if item['total_value'] else "N/A"

        profit = ""
        if item['profit_loss']:
            color = Fore.GREEN if item['profit_loss'] > 0 else Fore.RED
            profit = f"{color}{item['profit_loss']:+.2f} ({item['profit_loss_pct']:+.1f}%){Style.RESET_ALL}"

        data.append([
            item['id'],
            item['card_name'],
            item['set_name'] or 'N/A',
            item['quantity'],
            item['condition'],
            current,
            total,
            profit
        ])

    headers = ['ID', 'Name', 'Set', 'Qty', 'Condition', 'Price', 'Total', 'P/L']
    print(tabulate(data, headers=headers, tablefmt='grid'))


@collection.command(name='value')
def collection_value():
    """Show total collection value and statistics."""
    manager = CollectionManager()

    stats = manager.get_collection_value()

    print(f"\n💼 Collection Value\n")
    print(f"Total Cards: {stats['total_cards']}")
    print(f"Unique Cards: {stats['unique_cards']}")
    print()
    print(f"{Fore.CYAN}Current Value:{Style.RESET_ALL} ${stats['total_value']:.2f}")

    if stats['total_invested']:
        print(f"Total Invested: ${stats['total_invested']:.2f}")

        if stats['profit_loss']:
            color = Fore.GREEN if stats['profit_loss'] > 0 else Fore.RED
            print(f"Profit/Loss: {color}${stats['profit_loss']:+.2f} ({stats['profit_loss_pct']:+.1f}%){Style.RESET_ALL}")

    # Show top cards
    if stats['top_cards']:
        print(f"\n{Fore.YELLOW}Top 5 Most Valuable Cards:{Style.RESET_ALL}")
        for i, card in enumerate(stats['top_cards'][:5], 1):
            print(f"  {i}. {card['card_name']} - ${card['total_value']:.2f}")


@collection.command(name='remove')
@click.argument('collection_id', type=int)
def collection_remove(collection_id):
    """Remove a card from your collection."""
    manager = CollectionManager()

    if manager.remove_card(collection_id):
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} Card removed from collection")
    else:
        print(f"{Fore.RED}Card not found in collection.{Style.RESET_ALL}")


@collection.command(name='update')
def collection_update():
    """Update prices for all cards in collection."""
    manager = CollectionManager()

    print("🔄 Updating collection prices...")

    updated = manager.update_collection_prices()

    print(f"{Fore.GREEN}✓{Style.RESET_ALL} Updated prices for {updated} cards")


# ============================================================================
# ALERT COMMANDS
# ============================================================================

@cli.group()
def alert():
    """Manage price alerts."""
    pass


@alert.command(name='add')
@click.argument('card_id')
@click.option('--threshold', '-t', required=True, type=float, help='Price threshold')
@click.option('--condition', '-c', type=click.Choice(['above', 'below']), default='below', help='Alert condition')
def alert_add(card_id, threshold, condition):
    """Add a price alert for a card."""
    manager = AlertManager()
    api = PokemonTCGAPI()

    # Fetch card details
    card = api.get_card(card_id)
    if not card:
        print(f"{Fore.RED}Card not found.{Style.RESET_ALL}")
        return

    manager.add_alert(card_id, threshold, condition)

    print(f"{Fore.GREEN}✓{Style.RESET_ALL} Alert added for {card.name}")
    print(f"  Will notify when price goes {condition} ${threshold:.2f}")


@alert.command(name='list')
def alert_list():
    """List all price alerts."""
    manager = AlertManager()

    alerts = manager.get_alerts()

    if not alerts:
        print(f"{Fore.YELLOW}No alerts configured.{Style.RESET_ALL}")
        return

    print(f"\n🔔 Price Alerts\n")

    data = []
    for alert in alerts:
        current = f"${alert['current_price']:.2f}" if alert['current_price'] else "N/A"
        status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if alert['enabled'] else f"{Fore.RED}✗{Style.RESET_ALL}"

        data.append([
            alert['id'],
            status,
            alert['card_name'],
            alert['condition'],
            f"${alert['threshold_price']:.2f}",
            current,
            alert['triggered_count']
        ])

    headers = ['ID', 'Active', 'Card', 'Condition', 'Threshold', 'Current', 'Triggered']
    print(tabulate(data, headers=headers, tablefmt='grid'))


@alert.command(name='check')
def alert_check():
    """Check all alerts and display triggered ones."""
    manager = AlertManager()

    print("🔍 Checking alerts...\n")

    triggered = manager.run_alert_check()

    if not triggered:
        print(f"{Fore.GREEN}No alerts triggered.{Style.RESET_ALL}")


@alert.command(name='remove')
@click.argument('alert_id', type=int)
def alert_remove(alert_id):
    """Remove a price alert."""
    manager = AlertManager()

    if manager.remove_alert(alert_id):
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} Alert removed")
    else:
        print(f"{Fore.RED}Alert not found.{Style.RESET_ALL}")


# ============================================================================
# ANALYSIS COMMANDS
# ============================================================================

@cli.group()
def analyze():
    """Market analysis tools."""
    pass


@analyze.command(name='trending')
@click.option('--days', '-d', default=30, help='Number of days to analyze')
@click.option('--limit', '-l', default=20, help='Number of results')
def analyze_trending(days, limit):
    """Show trending cards with significant price changes."""
    analyzer = MarketAnalyzer()

    print(f"\n📈 Trending Cards (Last {days} days)\n")

    trending = analyzer.get_trending_cards(days=days)

    if not trending:
        print(f"{Fore.YELLOW}No trending data available.{Style.RESET_ALL}")
        return

    data = []
    for card in trending[:limit]:
        change_color = Fore.GREEN if card['price_change'] > 0 else Fore.RED
        change_str = f"{change_color}{card['price_change']:+.2f} ({card['price_change_pct']:+.1f}%){Style.RESET_ALL}"

        data.append([
            card['card_name'],
            card['set_name'] or 'N/A',
            f"${card['oldest_price']:.2f}",
            f"${card['newest_price']:.2f}",
            change_str,
            f"{card['volatility_pct']:.1f}%"
        ])

    headers = ['Card', 'Set', 'Old Price', 'New Price', 'Change', 'Volatility']
    print(tabulate(data, headers=headers, tablefmt='grid'))


@analyze.command(name='volatility')
@click.argument('card_id')
@click.option('--days', '-d', default=30, help='Number of days to analyze')
def analyze_volatility(card_id, days):
    """Analyze price volatility for a specific card."""
    analyzer = MarketAnalyzer()
    api = PokemonTCGAPI()

    card = api.get_card(card_id)
    if not card:
        print(f"{Fore.RED}Card not found.{Style.RESET_ALL}")
        return

    print(f"\n📊 Volatility Analysis: {card.name}\n")

    result = analyzer.get_card_volatility(card_id, days=days)

    if 'error' in result:
        print(f"{Fore.RED}Error: {result['error']}{Style.RESET_ALL}")
        return

    print(f"Period: {days} days")
    print(f"Data Points: {result['data_points']}")
    print()
    print(f"Mean Price: ${result['mean_price']:.2f}")
    print(f"Std Dev: ${result['std_dev']:.2f}")
    print(f"Price Range: ${result['min_price']:.2f} - ${result['max_price']:.2f}")
    print()
    print(f"Coefficient of Variation: {result['coefficient_of_variation']:.1f}%")
    print(f"Volatility Rating: {Fore.YELLOW}{result['volatility_rating']}{Style.RESET_ALL}")


# ============================================================================
# EXPORT COMMANDS
# ============================================================================

@cli.group()
def export():
    """Export data for Power BI and other tools."""
    pass


@export.command(name='powerbi')
def export_powerbi():
    """Export complete dataset for Power BI."""
    exporter = DataExporter()

    files = exporter.export_powerbi_dataset()

    print(f"\n{Fore.GREEN}✓ Power BI dataset ready!{Style.RESET_ALL}")
    print("\nNext steps:")
    print("1. Open Power BI Desktop")
    print("2. Click 'Get Data' > 'Text/CSV'")
    print(f"3. Import the CSV files from: {exporter.output_dir}")
    print("4. Create relationships between tables")
    print("\nSee POWERBI_GUIDE.md for detailed instructions.")


@export.command(name='collection')
@click.option('--format', '-f', type=click.Choice(['csv', 'json']), default='csv')
def export_collection(format):
    """Export collection data."""
    exporter = DataExporter()

    if format == 'csv':
        path = exporter.export_collection_csv()
    else:
        collection = exporter.collection_manager.get_collection()
        path = exporter.export_to_json(collection, 'collection.json')

    print(f"{Fore.GREEN}✓{Style.RESET_ALL} Collection exported to {path}")


@export.command(name='excel')
def export_excel():
    """Export all data to Excel workbook."""
    exporter = DataExporter()

    path = exporter.export_to_excel()

    if path:
        print(f"{Fore.GREEN}✓{Style.RESET_ALL} Data exported to {path}")


if __name__ == '__main__':
    cli()
