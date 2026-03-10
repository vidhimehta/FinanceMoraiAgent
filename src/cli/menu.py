"""
CLI menu system for FinanceMoraiAgent.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional

from ..data.sources.yahoo_finance import YahooFinanceSource
from .commands.forecast_cmd import ForecastCommand
from .commands.sentiment_cmd import SentimentCommand
from ..data.preprocessor import DataPreprocessor
from ..data.feature_engineering import FeatureEngineer
from ..core.cache_manager import get_cache_manager
from ..utils.helpers import format_currency, format_percentage, normalize_ticker


class CLIMenu:
    """
    Main CLI menu interface.
    """

    def __init__(self):
        """Initialize CLI menu."""
        self.console = Console()
        self.yahoo = YahooFinanceSource()
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        self.cache_manager = get_cache_manager()
        self.forecast_cmd = ForecastCommand(self.console)
        self.sentiment_cmd = SentimentCommand(self.console)

        logger.info("CLI Menu initialized")

    def show_banner(self):
        """Display welcome banner."""
        banner = Text()
        banner.append("╔═══════════════════════════════════════════════════════╗\n", style="bold cyan")
        banner.append("║                                                       ║\n", style="bold cyan")
        banner.append("║        ", style="bold cyan")
        banner.append("FinanceMoraiAgent", style="bold yellow")
        banner.append("                       ║\n", style="bold cyan")
        banner.append("║   Quantitative Finance with Moirai Time-Series AI   ║\n", style="bold cyan")
        banner.append("║                                                       ║\n", style="bold cyan")
        banner.append("╚═══════════════════════════════════════════════════════╝", style="bold cyan")

        self.console.print(banner)
        self.console.print()

    def show_main_menu(self) -> str:
        """
        Display main menu and get user choice.

        Returns:
            User's menu choice
        """
        self.console.print("\n[bold cyan]Main Menu[/bold cyan]", style="bold")
        self.console.print("─" * 50)

        menu_options = [
            ("1", "Fetch Market Data", "Download and cache stock data"),
            ("2", "Sentiment Analysis", "Analyze news, filings, and social sentiment"),
            ("3", "Regime Detection", "[dim](Coming in Phase 4)[/dim]"),
            ("4", "Generate Forecast", "AI-powered price forecasting"),
            ("5", "Run Backtest", "[dim](Coming in Phase 5)[/dim]"),
            ("6", "View Cache Stats", "Check cache status and statistics"),
            ("7", "Settings", "Configure application settings"),
            ("0", "Exit", "Quit the application"),
        ]

        for key, title, desc in menu_options:
            self.console.print(f"  [{key}] {title:.<30} {desc}")

        self.console.print("─" * 50)
        choice = Prompt.ask("\nEnter your choice", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
        return choice

    def fetch_market_data_menu(self):
        """Fetch market data menu."""
        self.console.print(Panel("[bold cyan]Fetch Market Data[/bold cyan]", box=box.ROUNDED))

        # Get ticker
        ticker = Prompt.ask("\nEnter stock ticker (e.g., AAPL, TCS.NS, RELIANCE.BO)")

        # Normalize ticker
        normalized_ticker, market = normalize_ticker(ticker)
        self.console.print(f"Market: [bold]{market}[/bold]")

        # Get date range
        self.console.print("\n[bold]Date Range[/bold]")
        date_choice = Prompt.ask(
            "Select date range",
            choices=["1", "2", "3", "4"],
            default="1",
        )

        end_date = datetime.now()

        if date_choice == "1":
            # Last 30 days
            start_date = end_date - timedelta(days=30)
        elif date_choice == "2":
            # Last 90 days
            start_date = end_date - timedelta(days=90)
        elif date_choice == "3":
            # Last year
            start_date = end_date - timedelta(days=365)
        else:
            # Custom
            start_str = Prompt.ask("Enter start date (YYYY-MM-DD)")
            end_str = Prompt.ask("Enter end date (YYYY-MM-DD)", default=end_date.strftime("%Y-%m-%d"))
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")

        self.console.print(f"\nFetching data for [bold]{normalized_ticker}[/bold] "
                          f"from [bold]{start_date.date()}[/bold] to [bold]{end_date.date()}[/bold]")

        try:
            with self.console.status("[bold green]Fetching data..."):
                # Fetch OHLCV data
                df = self.yahoo.fetch_ohlcv(normalized_ticker, start_date, end_date)

                # Clean data
                df_clean = self.preprocessor.clean_ohlcv(df)

                # Add features
                df_features = self.feature_engineer.add_all_features(df_clean)

            # Display results
            self.display_data_summary(df_features, normalized_ticker)

            # Ask if user wants to see detailed data
            if Confirm.ask("\nShow detailed data?"):
                self.display_detailed_data(df_features)

            # Save option
            if Confirm.ask("\nSave data to cache?"):
                self.cache_manager.save_parquet(df_features, normalized_ticker, "ohlcv")
                self.console.print("[green]✓[/green] Data saved to parquet file")

        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")
            logger.error(f"Failed to fetch market data: {e}")

    def display_data_summary(self, df, ticker: str):
        """Display data summary table."""
        self.console.print(f"\n[bold green]✓[/bold green] Successfully fetched {len(df)} rows")

        # Detect currency based on ticker
        _, market = normalize_ticker(ticker)
        currency = "INR" if market in ["NSE", "BSE"] else "USD"

        # Create summary table
        table = Table(title=f"Data Summary: {ticker}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        # Basic stats
        table.add_row("Date Range", f"{df.index.min().date()} to {df.index.max().date()}")
        table.add_row("Total Days", str(len(df)))
        table.add_row("Missing Values", str(df.isna().sum().sum()))

        # Price stats
        if "Close" in df.columns:
            latest_price = df["Close"].iloc[-1]
            price_change = df["Close"].iloc[-1] - df["Close"].iloc[0]
            price_change_pct = (price_change / df["Close"].iloc[0]) * 100

            table.add_row("Latest Price", format_currency(latest_price, currency))
            table.add_row("Price Change", f"{format_currency(price_change, currency)} ({price_change_pct:+.2f}%)")
            table.add_row("Highest Price", format_currency(df["Close"].max(), currency))
            table.add_row("Lowest Price", format_currency(df["Close"].min(), currency))

        # Volume stats
        if "Volume" in df.columns:
            table.add_row("Avg Volume", f"{df['Volume'].mean():,.0f}")

        self.console.print(table)

    def display_detailed_data(self, df, max_rows: int = 10):
        """Display detailed data table."""
        self.console.print(f"\n[bold]Latest {max_rows} Rows:[/bold]")

        # Create data table
        table = Table(box=box.SIMPLE)
        table.add_column("Date", style="cyan")
        table.add_column("Open", style="yellow")
        table.add_column("High", style="green")
        table.add_column("Low", style="red")
        table.add_column("Close", style="yellow")
        table.add_column("Volume", style="blue")

        # Show last N rows
        for idx, row in df.tail(max_rows).iterrows():
            table.add_row(
                str(idx.date()),
                f"{row['Open']:.2f}",
                f"{row['High']:.2f}",
                f"{row['Low']:.2f}",
                f"{row['Close']:.2f}",
                f"{row['Volume']:,.0f}",
            )

        self.console.print(table)

    def show_cache_stats_menu(self):
        """Display cache statistics."""
        self.console.print(Panel("[bold cyan]Cache Statistics[/bold cyan]", box=box.ROUNDED))

        stats = self.cache_manager.get_cache_stats()

        table = Table(title="Cache Status", box=box.ROUNDED)
        table.add_column("Cache Tier", style="cyan")
        table.add_column("Items", style="yellow")
        table.add_column("Size", style="green")

        table.add_row("Memory Cache", str(stats["memory_items"]), "N/A")
        table.add_row("Disk Cache", str(stats["disk_items"]), f"{stats['disk_size_mb']:.2f} MB")

        # Count parquet files
        parquet_files = list(self.cache_manager.parquet_dir.glob("*.parquet"))
        total_size = sum(f.stat().st_size for f in parquet_files) / (1024**2)
        table.add_row("Parquet Files", str(len(parquet_files)), f"{total_size:.2f} MB")

        self.console.print(table)

        # Option to clear cache
        if Confirm.ask("\nClear cache?", default=False):
            self.cache_manager.clear()
            self.console.print("[green]✓[/green] Cache cleared")

    def show_settings_menu(self):
        """Display settings menu."""
        self.console.print(Panel("[bold cyan]Settings[/bold cyan]", box=box.ROUNDED))

        self.console.print("\n[bold]Configuration:[/bold]")
        self.console.print("  • Config file: config/settings.yaml")
        self.console.print("  • Environment: .env")
        self.console.print("  • Cache directory: storage/cache")
        self.console.print("  • Data directory: storage/historical")

        self.console.print("\n[dim]Edit configuration files to change settings[/dim]")

    def run(self):
        """Run the CLI menu loop."""
        self.show_banner()

        while True:
            try:
                choice = self.show_main_menu()

                if choice == "0":
                    self.console.print("\n[bold cyan]Thank you for using FinanceMoraiAgent![/bold cyan]")
                    break
                elif choice == "1":
                    self.fetch_market_data_menu()
                elif choice == "2":
                    self.sentiment_cmd.run_sentiment_menu()
                elif choice == "3":
                    self.console.print("\n[yellow]Regime Detection coming in Phase 4[/yellow]")
                elif choice == "4":
                    self.forecast_cmd.run_forecast_menu()
                elif choice == "5":
                    self.console.print("\n[yellow]Backtesting coming in Phase 5[/yellow]")
                elif choice == "6":
                    self.show_cache_stats_menu()
                elif choice == "7":
                    self.show_settings_menu()

                # Pause before showing menu again
                if choice != "0":
                    self.console.print()
                    Prompt.ask("\nPress Enter to continue", default="")

            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Interrupted by user[/yellow]")
                if Confirm.ask("Do you want to exit?", default=True):
                    break
            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {e}")
                logger.error(f"Menu error: {e}")
                Prompt.ask("\nPress Enter to continue", default="")
