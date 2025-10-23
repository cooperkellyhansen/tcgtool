# Power BI Integration Guide

This guide will help you integrate the Pokemon TCG Price Analysis Tool with Power BI to create interactive dashboards.

## Overview

The tool exports data in several formats compatible with Power BI:
- **CSV files** - Easy to import and refresh
- **SQLite database** - Direct connection for real-time data
- **JSON files** - For custom data integrations

## Quick Start

### Step 1: Export Data

Run the export command to generate all necessary files:

```bash
python -m tcgtool export powerbi
```

This creates the following files in the `exports/` directory:
- `powerbi_cards_[timestamp].csv` - Master card data
- `powerbi_prices_[timestamp].csv` - Price history
- `powerbi_collection_[timestamp].csv` - Your collection
- `powerbi_trending_[timestamp].csv` - Trending analysis

### Step 2: Import into Power BI

1. **Open Power BI Desktop**

2. **Import Card Data**
   - Click **Get Data** > **Text/CSV**
   - Select `powerbi_cards_[timestamp].csv`
   - Click **Load**

3. **Import Price History**
   - Click **Get Data** > **Text/CSV**
   - Select `powerbi_prices_[timestamp].csv`
   - Click **Load**

4. **Import Collection Data**
   - Click **Get Data** > **Text/CSV**
   - Select `powerbi_collection_[timestamp].csv`
   - Click **Load**

5. **Import Trending Data**
   - Click **Get Data** > **Text/CSV**
   - Select `powerbi_trending_[timestamp].csv`
   - Click **Load**

### Step 3: Create Relationships

Power BI may automatically detect relationships. If not:

1. Go to **Model view** (left sidebar)
2. Create the following relationships:

**Price History → Cards**
- Drag `card_id` from `price_history` to `id` in `cards`
- Cardinality: Many to One (*)
- Cross filter direction: Single

**Collection → Cards**
- Drag `card_id` from `collection` to `id` in `cards`
- Cardinality: Many to One (*)
- Cross filter direction: Both

## Data Tables

### Cards Table (Dimension)
Contains master card information:
- `id` - Unique card identifier
- `name` - Card name
- `set_name` - Pokemon TCG set
- `rarity` - Card rarity
- `artist` - Card artist
- `release_date` - Set release date

### Price History Table (Fact)
Contains historical price data:
- `card_id` - Foreign key to Cards
- `card_name` - Card name (denormalized)
- `market_price` - Current market price
- `low_price` - Lowest price
- `high_price` - Highest price
- `recorded_at` - Timestamp

### Collection Table (Fact)
Contains your collection:
- `card_id` - Foreign key to Cards
- `quantity` - Number of cards owned
- `condition` - Card condition
- `purchase_price` - Original purchase price
- `current_price` - Latest market price
- `total_value` - Current total value
- `profit_loss` - Profit or loss amount
- `profit_loss_pct` - Profit/loss percentage

### Trending Table (Fact)
Contains trend analysis:
- `card_id` - Card identifier
- `card_name` - Card name
- `price_change` - Price change amount
- `price_change_pct` - Price change percentage
- `volatility_pct` - Price volatility

## Sample Visualizations

### 1. Collection Value Over Time

**Visual Type:** Line Chart
- **X-axis:** `recorded_at` from Price History
- **Y-axis:** `market_price` (sum)
- **Legend:** `card_name` from Cards
- **Filter:** Cards in your collection

### 2. Portfolio Breakdown

**Visual Type:** Pie Chart
- **Values:** `total_value` from Collection
- **Legend:** `card_name`

### 3. Top Gainers/Losers

**Visual Type:** Bar Chart
- **X-axis:** `card_name`
- **Y-axis:** `profit_loss_pct` from Collection
- **Sort:** By `profit_loss_pct` descending

### 4. Price Trend Analysis

**Visual Type:** Line Chart with Forecast
- **X-axis:** `recorded_at`
- **Y-axis:** `market_price`
- **Legend:** `card_name`
- Enable **Analytics** > **Forecast** for predictions

### 5. Rarity Distribution

**Visual Type:** Donut Chart
- **Values:** Count of cards
- **Legend:** `rarity` from Cards
- **Filter:** Your collection

### 6. Market Volatility Heat Map

**Visual Type:** Matrix
- **Rows:** `card_name`
- **Columns:** `set_name`
- **Values:** `volatility_pct` from Trending
- **Color scale:** Low (green) to High (red)

## Key Metrics (DAX Measures)

Create these calculated measures for better insights:

### Total Collection Value
```dax
Total Collection Value =
SUM(Collection[total_value])
```

### Total Cards
```dax
Total Cards =
SUM(Collection[quantity])
```

### Average Card Price
```dax
Avg Card Price =
AVERAGE(Collection[current_price])
```

### Portfolio ROI
```dax
Portfolio ROI =
DIVIDE(
    SUM(Collection[profit_loss]),
    SUM(Collection[purchase_price]) * SUM(Collection[quantity]),
    0
)
```

### Price Trend (30 Days)
```dax
Price Trend 30D =
VAR CurrentPrice = SUM(PriceHistory[market_price])
VAR PriceThirtyDaysAgo =
    CALCULATE(
        SUM(PriceHistory[market_price]),
        DATEADD(PriceHistory[recorded_at], -30, DAY)
    )
RETURN
    DIVIDE(CurrentPrice - PriceThirtyDaysAgo, PriceThirtyDaysAgo, 0)
```

### Top Card by Value
```dax
Top Card =
TOPN(
    1,
    SUMMARIZE(
        Collection,
        Cards[name],
        "Value", SUM(Collection[total_value])
    ),
    [Value],
    DESC
)
```

## Auto-Refresh Setup

### Method 1: Manual Refresh
1. Re-export data: `python -m tcgtool export powerbi`
2. In Power BI: Click **Refresh**

### Method 2: Scheduled Export (Advanced)

Create a scheduled task to auto-export data:

**Windows (Task Scheduler):**
```batch
python -m tcgtool export powerbi
```

**Linux/Mac (cron):**
```bash
0 */6 * * * cd /path/to/tcgtool && python -m tcgtool export powerbi
```

### Method 3: Direct Database Connection

For real-time data, connect directly to the SQLite database:

1. In Power BI: **Get Data** > **More** > **Database** > **SQLite**
2. Browse to `data/tcgtool.db`
3. Select tables: `cards`, `price_history`, `collection`
4. Click **Load**

**Note:** You may need to install [SQLite ODBC driver](http://www.ch-werner.de/sqliteodbc/)

## Dashboard Layout Suggestions

### Dashboard 1: Portfolio Overview
- **KPI Cards:** Total Value, Total Cards, ROI, Change (30d)
- **Line Chart:** Collection value over time
- **Pie Chart:** Portfolio breakdown by card
- **Bar Chart:** Top 10 cards by value

### Dashboard 2: Market Analysis
- **Line Chart:** Price trends for tracked cards
- **Table:** Trending cards with % change
- **Heat Map:** Volatility by set and rarity
- **Scatter Plot:** Price vs. volatility

### Dashboard 3: Collection Details
- **Table:** Full collection with filters
- **Bar Chart:** Cards by condition
- **Line Chart:** Purchase price vs. current price
- **Slicer:** Filter by set, rarity, condition

## Tips and Best Practices

1. **Use Bookmarks** - Create bookmarks for different views (Portfolio, Market, Collection)

2. **Enable Drill-Through** - Allow drilling from summary to card details

3. **Add Slicers** - Filter by:
   - Date range
   - Card set
   - Rarity
   - Price range

4. **Use Conditional Formatting** - Highlight:
   - Gains in green
   - Losses in red
   - High volatility in orange

5. **Create Mobile Layout** - Design a mobile-friendly version in Power BI

6. **Publish to Power BI Service** - Share dashboards with others

7. **Set Up Alerts** - Use Power BI alerts for significant changes

## Troubleshooting

### Issue: "Could not find file"
**Solution:** Make sure you're using the full path to the CSV files

### Issue: "Data type errors"
**Solution:** Power BI should auto-detect types, but you can manually set:
- Prices: Decimal Number
- Dates: Date/Time
- IDs: Text

### Issue: "Relationships not working"
**Solution:** Ensure card_id in both tables match exactly (same data type)

### Issue: "Slow performance"
**Solution:**
- Import only recent data (filter by date)
- Use DirectQuery for large datasets
- Aggregate data before importing

## Advanced: Custom Visuals

Consider installing these Power BI custom visuals:

1. **Chiclet Slicer** - Better filtering experience
2. **Timeline Slicer** - Interactive date filtering
3. **Drill Down Combo** - Combined chart types
4. **Card with States** - Better KPI cards
5. **Power KPI** - Advanced KPI visualizations

## Sample Dashboard Template

A complete sample `.pbix` file would include:

1. **Home Page**
   - Total collection value
   - Total cards
   - Overall ROI
   - Quick navigation buttons

2. **My Collection**
   - Detailed card list
   - Value by set
   - Condition breakdown
   - Recent additions

3. **Market Insights**
   - Trending cards
   - Price movements
   - Volatility analysis
   - Best/worst performers

4. **Card Detail**
   - Individual card focus
   - Price history chart
   - Similar cards comparison
   - Market statistics

## Resources

- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)
- [DAX Function Reference](https://dax.guide/)
- [Power BI Community](https://community.powerbi.com/)

## Need Help?

If you encounter issues:
1. Check that data exports are complete
2. Verify file paths are correct
3. Ensure relationships are properly configured
4. Review the error messages in Power Query

Happy analyzing! 📊
