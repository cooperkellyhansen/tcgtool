# Usage Guide

Complete usage examples for the Pokemon TCG Price Analysis Tool.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd tcgtool

# Install dependencies
pip install -r requirements.txt

# Set up your API key (optional but recommended)
cp .env.example .env
# Edit .env and add your Pokemon TCG API key
```

## Getting Started

### 1. Search for Cards

```bash
# Search for a card
python -m tcgtool search "Charizard"

# Limit results
python -m tcgtool search "Pikachu" --limit 5
```

### 2. Get Price Information

```bash
# Get detailed price for a specific card
python -m tcgtool price "xy1-2"

# The card ID comes from the search results
```

## Managing Your Collection

### Add Cards

```bash
# Add a card to your collection
python -m tcgtool collection add "xy1-2" --quantity 2 --condition "Near Mint"

# Add with purchase price
python -m tcgtool collection add "xy1-2" --quantity 1 --price 45.00 --condition "Mint"
```

### View Collection

```bash
# List all cards in your collection
python -m tcgtool collection list

# See total collection value
python -m tcgtool collection value
```

### Update Prices

```bash
# Update prices for all cards in your collection
python -m tcgtool collection update
```

### Remove Cards

```bash
# Remove a card from collection (use the ID from collection list)
python -m tcgtool collection remove 1
```

## Price Alerts

### Set Up Alerts

```bash
# Alert when price goes below $50
python -m tcgtool alert add "xy1-2" --threshold 50.00 --condition below

# Alert when price goes above $100
python -m tcgtool alert add "xy1-2" --threshold 100.00 --condition above
```

### Manage Alerts

```bash
# List all alerts
python -m tcgtool alert list

# Check alerts (runs alert check)
python -m tcgtool alert check

# Remove an alert
python -m tcgtool alert remove 1
```

## Market Analysis

### View Trending Cards

```bash
# See trending cards (last 30 days)
python -m tcgtool analyze trending

# Custom time period
python -m tcgtool analyze trending --days 7 --limit 10
```

### Analyze Volatility

```bash
# Check price volatility for a specific card
python -m tcgtool analyze volatility "xy1-2"

# Custom time period
python -m tcgtool analyze volatility "xy1-2" --days 60
```

## Exporting Data

### Power BI Export

```bash
# Export complete dataset for Power BI
python -m tcgtool export powerbi
```

This creates multiple CSV files in the `exports/` directory:
- Cards master data
- Price history
- Collection data
- Trending analysis

### Export Collection

```bash
# Export to CSV
python -m tcgtool export collection --format csv

# Export to JSON
python -m tcgtool export collection --format json
```

### Export to Excel

```bash
# Export everything to Excel workbook
python -m tcgtool export excel
```

## Example Workflows

### Workflow 1: Start Tracking a Card

```bash
# 1. Search for the card
python -m tcgtool search "Charizard VSTAR"

# 2. Get detailed price info (use ID from search)
python -m tcgtool price "swsh9-18"

# 3. Set up price alert
python -m tcgtool alert add "swsh9-18" --threshold 30.00 --condition below

# 4. Check back later
python -m tcgtool alert check
```

### Workflow 2: Manage Your Collection

```bash
# 1. Add cards you own
python -m tcgtool collection add "base1-4" --quantity 1 --price 250.00
python -m tcgtool collection add "xy1-2" --quantity 2 --price 45.00

# 2. View collection
python -m tcgtool collection list

# 3. Update prices
python -m tcgtool collection update

# 4. Check value
python -m tcgtool collection value

# 5. Export for analysis
python -m tcgtool export powerbi
```

### Workflow 3: Market Research

```bash
# 1. Check trending cards
python -m tcgtool analyze trending --days 30

# 2. Analyze specific card volatility
python -m tcgtool analyze volatility "swsh9-18"

# 3. Track price history
python -m tcgtool price "swsh9-18"

# 4. Export trending data
python -m tcgtool export powerbi
```

## Advanced Usage

### Automated Price Tracking

Set up a scheduled task to automatically update prices:

**Linux/Mac (crontab):**
```bash
# Update prices every 6 hours
0 */6 * * * cd /path/to/tcgtool && python -m tcgtool collection update

# Check alerts every hour
0 * * * * cd /path/to/tcgtool && python -m tcgtool alert check
```

**Windows (Task Scheduler):**
Create tasks that run:
- `python -m tcgtool collection update` every 6 hours
- `python -m tcgtool alert check` every hour

### Configuration

Edit `config.yaml` to customize:

```yaml
# API keys
api_keys:
  pokemon_tcg_api: "your-api-key-here"

# Price tracking frequency
price_tracking:
  enabled: true
  check_interval_hours: 24
  retention_days: 365

# Alerts
alerts:
  enabled: true
  check_interval_minutes: 60

# Export settings
export:
  default_format: "csv"
  output_directory: "exports"
```

### Database Location

By default, the database is stored in `data/tcgtool.db`. You can change this in `config.yaml`:

```yaml
database:
  path: "/custom/path/to/database.db"
```

## Tips and Tricks

### 1. Get a Free API Key

Visit https://dev.pokemontcg.io/ to get a free API key. This increases your rate limits and provides better performance.

### 2. Backup Your Data

The SQLite database is portable. Simply copy `data/tcgtool.db` to backup your data:

```bash
cp data/tcgtool.db ~/backups/tcgtool_$(date +%Y%m%d).db
```

### 3. Import/Export Collection

You can export your collection to CSV and share it or import it on another machine:

```bash
# Export
python -m tcgtool export collection --format csv

# To import, add cards using the card IDs from the CSV
```

### 4. Bulk Operations

For bulk operations, you can create a shell script:

```bash
#!/bin/bash
# bulk_add.sh - Add multiple cards

cards=(
  "base1-4"
  "xy1-2"
  "swsh9-18"
)

for card in "${cards[@]}"; do
  python -m tcgtool collection add "$card" --quantity 1
done
```

### 5. Power BI Auto-Refresh

Set up a scheduled export and configure Power BI to auto-refresh:

```bash
# Create a cron job
0 6 * * * cd /path/to/tcgtool && python -m tcgtool export powerbi
```

Then in Power BI, set up scheduled refresh to run after your export.

## Troubleshooting

### "No module named 'pokemontcgsdk'"

```bash
pip install -r requirements.txt
```

### "Database is locked"

Close any other instances of the tool or database browsers.

### "API rate limit exceeded"

Get a free API key from https://dev.pokemontcg.io/ and add it to your `.env` file.

### "No price data available"

Some cards may not have price data in the Pokemon TCG API. The tool will skip these cards.

## Getting Help

- Check the [README.md](README.md) for general information
- See [POWERBI_GUIDE.md](POWERBI_GUIDE.md) for Power BI integration
- Review [config.yaml](config.yaml) for configuration options
- Check the [Pokemon TCG API documentation](https://docs.pokemontcg.io/)

## Example Card IDs

Here are some popular cards to get started:

- Charizard VSTAR: `swsh9-18`
- Pikachu VMAX: `swsh4-44`
- Mewtwo & Mew GX: `sm11-71`
- Base Set Charizard: `base1-4`
- Shining Charizard: `neo4-107`

Use these in search or to add to your collection!
