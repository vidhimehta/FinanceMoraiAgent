"""
CLI commands for forecasting functionality.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, Confirm, IntPrompt
from datetime import datetime
from loguru import logger

from ...core.data_pipeline import DataPipeline
from ...utils.helpers import format_currency, format_percentage


class ForecastCommand:
    """
    Handles forecast-related CLI commands.
    """

    def __init__(self, console: Console):
        """
        Initialize forecast command handler.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.pipeline = DataPipeline()
        logger.info("ForecastCommand initialized")

    def run_forecast_menu(self):
        """Display forecast generation menu."""
        self.console.print(Panel("[bold cyan]Generate Forecast[/bold cyan]", box=box.ROUNDED))

        # Get ticker
        ticker = Prompt.ask("\nEnter stock ticker (e.g., AAPL, TCS.NS)")

        # Get forecast horizon
        self.console.print("\n[bold]Forecast Horizon:[/bold]")
        self.console.print("  1. Tomorrow (1 day) ⚡ Most accurate!")
        self.console.print("  2. This week (7 days)")
        self.console.print("  3. Two weeks (14 days)")
        self.console.print("  4. One month (30 days)")
        self.console.print("  5. Custom")

        horizon_choice = Prompt.ask("Select horizon", choices=["1", "2", "3", "4", "5"], default="2")

        if horizon_choice == "1":
            horizon = 1
            recommended_lookback = 30
        elif horizon_choice == "2":
            horizon = 7
            recommended_lookback = 60
        elif horizon_choice == "3":
            horizon = 14
            recommended_lookback = 90
        elif horizon_choice == "4":
            horizon = 30
            recommended_lookback = 120
        else:
            horizon = IntPrompt.ask("Enter number of days", default=7)
            recommended_lookback = 90

        # Get lookback period
        lookback = IntPrompt.ask(
            f"\nLookback period (days of historical data) [recommended: {recommended_lookback}]",
            default=recommended_lookback
        )

        # Ask about context
        use_context = Confirm.ask(
            "\nUse technical indicators as context?",
            default=True
        )

        # Generate forecast
        try:
            if horizon == 1:
                self.console.print(f"\n[bold green]Predicting tomorrow's price for {ticker}...[/bold green]")
            else:
                self.console.print(f"\n[bold green]Generating {horizon}-day forecast for {ticker}...[/bold green]")

            with self.console.status("[bold green]Generating forecast..."):
                result = self.pipeline.generate_forecast(
                    ticker=ticker,
                    horizon=horizon,
                    lookback_days=lookback,
                    use_context=use_context,
                )

            # Display results
            self.display_forecast_results(result)

            # Ask about visualization (skip for 1-day)
            if horizon > 1 and Confirm.ask("\nShow forecast plot?", default=True):
                self.display_forecast_plot(result)

            # Ask about export
            if Confirm.ask("\nExport forecast to CSV?", default=False):
                self.export_forecast(result)

        except Exception as e:
            self.console.print(f"\n[bold red]Error:[/bold red] {e}")
            logger.error(f"Forecast generation failed: {e}")

    def display_forecast_results(self, result: dict):
        """
        Display forecast results in a table.

        Args:
            result: Forecast result dictionary
        """
        self.console.print(f"\n[bold green]✓[/bold green] Forecast generated successfully!")

        # Summary table
        horizon = result['horizon']
        if horizon == 1:
            title = f"Tomorrow's Prediction: {result['ticker']}"
        else:
            title = f"Forecast Summary: {result['ticker']}"
            
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        stats = result["statistics"]
        table.add_row("Method", result["method"].replace("_", " ").title())
        
        if horizon == 1:
            table.add_row("Horizon", "Tomorrow")
        else:
            table.add_row("Horizon", f"{horizon} days")
            
        table.add_row("Confidence Level", f"{result['confidence_level']*100:.0f}%")
        table.add_row("", "")  # Spacer
        table.add_row("Current Price", format_currency(stats["last_price"], "USD"))
        
        if horizon == 1:
            table.add_row("Tomorrow's Price", format_currency(stats["forecast_final"], "USD"))
        else:
            table.add_row("Forecast (Final)", format_currency(stats["forecast_final"], "USD"))
            
        table.add_row("Expected Return", format_percentage(stats["expected_return"]))
        
        if horizon > 1:
            table.add_row("Min Forecast", format_currency(stats["min_forecast"], "USD"))
            table.add_row("Max Forecast", format_currency(stats["max_forecast"], "USD"))

        self.console.print(table)

        # Show forecast details
        if horizon == 1:
            self._display_tomorrow_detail(result)
        else:
            self._display_multi_day_preview(result)

    def _display_tomorrow_detail(self, result: dict):
        """Display detailed prediction for tomorrow."""
        self.console.print("\n[bold]Tomorrow's Prediction Detail:[/bold]")
        
        forecast = result["forecast"][0]
        lower = result["lower_bound"][0]
        upper = result["upper_bound"][0]
        date = result["dates"][0]
        
        detail_table = Table(box=box.SIMPLE)
        detail_table.add_column("Date", style="cyan")
        detail_table.add_column("Expected Price", style="yellow")
        detail_table.add_column("Best Case", style="green")
        detail_table.add_column("Worst Case", style="red")
        
        detail_table.add_row(
            str(date.date()),
            f"${forecast:.2f}",
            f"${upper:.2f}",
            f"${lower:.2f}",
        )
        
        self.console.print(detail_table)
        
        # Add interpretation
        current = result["statistics"]["last_price"]
        change = forecast - current
        change_pct = (change / current) * 100
        
        self.console.print("\n[bold]What This Means:[/bold]")
        if change > 0:
            self.console.print(f"  📈 [green]Expected to go UP by ${abs(change):.2f} ({abs(change_pct):.2f}%)[/green]")
        elif change < 0:
            self.console.print(f"  📉 [red]Expected to go DOWN by ${abs(change):.2f} ({abs(change_pct):.2f}%)[/red]")
        else:
            self.console.print(f"  ➡️  [yellow]Expected to stay relatively FLAT[/yellow]")
            
        range_width = upper - lower
        volatility_pct = (range_width / current) * 100
        
        self.console.print(f"\n[bold]Uncertainty Range:[/bold]")
        self.console.print(f"  Range: ${lower:.2f} to ${upper:.2f}")
        self.console.print(f"  Spread: ${range_width:.2f} ({volatility_pct:.1f}% volatility)")
        
        if volatility_pct < 2:
            self.console.print("  ✓ [green]Low volatility - fairly predictable[/green]")
        elif volatility_pct < 5:
            self.console.print("  ⚠️  [yellow]Moderate volatility - some uncertainty[/yellow]")
        else:
            self.console.print("  ⚠️  [red]High volatility - significant uncertainty[/red]")

    def _display_multi_day_preview(self, result: dict):
        """Display preview for multi-day forecasts."""
        self.console.print("\n[bold]Forecast Preview:[/bold]")
        forecast_table = Table(box=box.SIMPLE)
        forecast_table.add_column("Date", style="cyan")
        forecast_table.add_column("Forecast", style="yellow")
        forecast_table.add_column("Lower Bound", style="red")
        forecast_table.add_column("Upper Bound", style="green")

        dates = result["dates"]
        forecast = result["forecast"]
        lower = result["lower_bound"]
        upper = result["upper_bound"]

        # Show first 3 and last 3
        if len(forecast) <= 6:
            indices = list(range(len(forecast)))
        else:
            indices = list(range(3)) + list(range(len(forecast) - 3, len(forecast)))

        for i in indices:
            if i == 3 and len(forecast) > 6:
                forecast_table.add_row("...", "...", "...", "...")
            forecast_table.add_row(
                str(dates[i].date()),
                f"${forecast[i]:.2f}",
                f"${lower[i]:.2f}",
                f"${upper[i]:.2f}",
            )

        self.console.print(forecast_table)

    def display_forecast_plot(self, result: dict):
        """
        Display ASCII plot of forecast.

        Args:
            result: Forecast result dictionary
        """
        try:
            import plotext as plt

            self.console.print("\n[bold]Forecast Visualization:[/bold]\n")

            # Prepare data
            historical = result["historical_data"]["Close"].values[-30:]  # Last 30 days
            forecast = result["forecast"]
            lower = result["lower_bound"]
            upper = result["upper_bound"]

            # Create x-axis
            hist_x = list(range(-len(historical), 0))
            forecast_x = list(range(0, len(forecast)))

            # Plot
            plt.clear_figure()
            plt.plot(hist_x, historical, label="Historical", marker="dot")
            plt.plot(forecast_x, forecast, label="Forecast", marker="dot")
            plt.plot(forecast_x, lower, label="Lower Bound", marker="dot")
            plt.plot(forecast_x, upper, label="Upper Bound", marker="dot")

            plt.title(f"{result['ticker']} Price Forecast")
            plt.xlabel("Days")
            plt.ylabel("Price ($)")
            plt.plotsize(100, 25)

            plt.show()

        except ImportError:
            self.console.print("[yellow]plotext not available for visualization[/yellow]")
        except Exception as e:
            self.console.print(f"[yellow]Visualization error: {e}[/yellow]")

    def export_forecast(self, result: dict):
        """
        Export forecast to CSV file.

        Args:
            result: Forecast result dictionary
        """
        try:
            import pandas as pd
            from pathlib import Path

            # Create export directory
            export_dir = Path("storage/results")
            export_dir.mkdir(parents=True, exist_ok=True)

            # Prepare data
            export_data = pd.DataFrame({
                "Date": result["dates"],
                "Forecast": result["forecast"],
                "Lower_Bound": result["lower_bound"],
                "Upper_Bound": result["upper_bound"],
            })

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            horizon_label = "tomorrow" if result["horizon"] == 1 else f"{result['horizon']}day"
            filename = export_dir / f"{result['ticker']}_forecast_{horizon_label}_{timestamp}.csv"

            # Export
            export_data.to_csv(filename, index=False)

            self.console.print(f"\n[green]✓[/green] Forecast exported to: {filename}")

        except Exception as e:
            self.console.print(f"\n[red]Export failed:[/red] {e}")
