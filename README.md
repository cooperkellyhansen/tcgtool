# Pokemon TCG Price Analysis Tool

A comprehensive Python-based tool for analyzing Pokemon Trading Card Game prices with Power BI integration.

## Features

✨ **Price Lookup** - Search for cards and get current market prices from multiple sources
📊 **Price Tracking** - Monitor and store historical price data
💼 **Collection Management** - Track your card collection and its total value
🔍 **Multi-Marketplace Comparison** - Compare prices across TCGPlayer, CardMarket, and more
📁 **Data Export** - Export to CSV, JSON, and SQLite for Power BI integration
🔔 **Price Alerts** - Set alerts for price thresholds
📈 **Market Analysis** - Identify trending cards and analyze price volatility

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a FREE Pokemon TCG API Key (REQUIRED)

⚠️ **The tool requires a Pokemon TCG API key to function!**

1. Visit **https://dev.pokemontcg.io/**
2. Sign up for a free account (takes 30 seconds)
3. Copy your API key

### 3. Configure Your API Key

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
POKEMON_TCG_API_KEY=your_api_key_here
```

**Without an API key, you cannot fetch card data or prices!**

## Quick Start

```bash
# Search for a card
python -m tcgtool search "Charizard VSTAR"

# Add to collection
python -m tcgtool collection add "Charizard VSTAR" --quantity 1

# View collection value
python -m tcgtool collection value

# Export data for Power BI
python -m tcgtool export --format powerbi

# Set price alert
python -m tcgtool alert set "Charizard VSTAR" --threshold 50.00
```

## Power BI Integration

This tool exports data in multiple formats compatible with Power BI:

1. **SQLite Database** - Direct connection to `data/tcgtool.db`
2. **CSV Export** - Structured CSV files in `exports/`
3. **JSON Export** - JSON format for custom integrations

See [POWERBI_GUIDE.md](POWERBI_GUIDE.md) for detailed integration instructions.

## Project Structure

```
tcgtool/
├── tcgtool/                 # Main package
│   ├── __init__.py
│   ├── __main__.py         # CLI entry point
│   ├── api/                # API integrations
│   ├── database/           # Database models and operations
│   ├── collection/         # Collection management
│   ├── alerts/             # Price alert system
│   ├── analysis/           # Market analysis
│   └── export/             # Data export functionality
├── data/                   # SQLite database and cache
├── exports/                # Exported data files
├── config.yaml             # Configuration file
├── requirements.txt        # Python dependencies
└── README.md
```

## Configuration

### Required Setup

**Pokemon TCG API Key** (Required): Add your key to `.env`:
```bash
POKEMON_TCG_API_KEY=your_key_here
```
Get your free key at: https://dev.pokemontcg.io/

### Optional Configuration

Edit `config.yaml` to customize:
- Alert notification settings
- Export preferences
- Database location
- Price tracking intervals

## Data Sources

- TCGPlayer API (primary)
- Pokemon TCG API (card details)
- Historical price tracking (internal database)

## License

MIT License
