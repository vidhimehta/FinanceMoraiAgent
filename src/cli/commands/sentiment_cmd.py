"""
CLI commands for sentiment analysis functionality.
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, Confirm, IntPrompt
from datetime import datetime
from loguru import logger
from typing import Dict

from ...sentiment.analyzer import SentimentAnalyzer


class SentimentCommand:
    """
    Handles sentiment analysis CLI commands.
    """

    def __init__(self, console: Console):
        """
        Initialize sentiment command handler.

        Args:
            console: Rich console for output
        """
        self.console = console
        self.analyzer = SentimentAnalyzer(use_finbert=False)  # Use VADER by default
        logger.info("SentimentCommand initialized")

    def run_sentiment_menu(self):
        """Display sentiment analysis menu."""
        self.console.print(Panel("[bold cyan]Sentiment Analysis[/bold cyan]", box=box.ROUNDED))

        # Get ticker
        ticker = Prompt.ask("\nEnter stock ticker (e.g., AAPL, TCS.NS)")

        # Get company name (optional, helps with news search)
        company_name = Prompt.ask(
            "Enter company name (optional, press Enter to skip)",
            default=""
        )
        if not company_name:
            company_name = None

        # Get time period
        self.console.print("\n[bold]Analysis Period:[/bold]")
        self.console.print("  1. Last 3 days")
        self.console.print("  2. Last 7 days (1 week)")
        self.console.print("  3. Last 14 days (2 weeks)")
        self.console.print("  4. Last 30 days (1 month)")
        self.console.print("  5. Custom")

        period_choice = Prompt.ask("Select period", choices=["1", "2", "3", "4", "5"], default="2")

        if period_choice == "1":
            days_back = 3
        elif period_choice == "2":
            days_back = 7
        elif period_choice == "3":
            days_back = 14
        elif period_choice == "4":
            days_back = 30
        else:
            days_back = IntPrompt.ask("Enter number of days", default=7)

        # What to include
        include_news = Confirm.ask("\nInclude news articles?", default=True)
        include_filings = Confirm.ask("Include SEC/SEBI filings?", default=True)

        # Analyze sentiment
        try:
            self.console.print(f"\n[bold green]Analyzing sentiment for {ticker}...[/bold green]")
            self.console.print("[dim]This may take a few moments...[/dim]")

            with self.console.status("[bold green]Collecting and analyzing data..."):
                result = self.analyzer.analyze_stock_sentiment(
                    ticker=ticker,
                    company_name=company_name,
                    days_back=days_back,
                    include_news=include_news,
                    include_filings=include_filings,
                )

            # Display results
            self.display_sentiment_results(result)

        except Exception as e:
            self.console.print(f"\n[bold red]Error:[/bold red] {e}")
            logger.error(f"Sentiment analysis failed: {e}")

    def display_sentiment_results(self, result: Dict):
        """
        Display sentiment analysis results.

        Args:
            result: Sentiment analysis result dictionary
        """
        self.console.print(f"\n[bold green]✓[/bold green] Sentiment analysis complete!")

        # Overall sentiment summary
        overall = result["overall"]
        score = overall["score"]
        label = overall["label"]
        confidence = overall.get("confidence", 0.0)

        # Create summary table
        table = Table(title=f"Sentiment Summary: {result['ticker']}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")

        # Sentiment indicator
        if label == "positive":
            sentiment_display = f"[green]●[/green] {label.upper()} ({score:+.2f})"
        elif label == "negative":
            sentiment_display = f"[red]●[/red] {label.upper()} ({score:+.2f})"
        else:
            sentiment_display = f"[yellow]●[/yellow] {label.upper()} ({score:+.2f})"

        table.add_row("Overall Sentiment", sentiment_display)
        table.add_row("Confidence Level", f"{confidence * 100:.0f}%")
        table.add_row("Analysis Period", f"{result['days_analyzed']} days")
        table.add_row("Analyzed At", result["analyzed_at"][:19])

        self.console.print(table)

        # Source breakdown
        self.console.print("\n[bold]Sentiment by Source:[/bold]")
        source_table = Table(box=box.SIMPLE)
        source_table.add_column("Source", style="cyan")
        source_table.add_column("Sentiment", style="yellow")
        source_table.add_column("Items Analyzed", style="blue")
        source_table.add_column("Confidence", style="green")

        sources = result.get("sources", {})
        
        if "news" in sources:
            news = sources["news"]
            sentiment = news.get("sentiment", {})
            label_display = self._format_sentiment_label(sentiment.get("label", "neutral"))
            source_table.add_row(
                "News Articles",
                label_display,
                str(news.get("article_count", 0)),
                f"{news.get('confidence', 0) * 100:.0f}%"
            )

        if "sec" in sources:
            sec = sources["sec"]
            sentiment = sec.get("sentiment", {})
            label_display = self._format_sentiment_label(sentiment.get("label", "neutral"))
            source_table.add_row(
                "SEC Filings",
                label_display,
                str(sec.get("filing_count", 0)),
                f"{sec.get('confidence', 0) * 100:.0f}%"
            )

        if "sebi" in sources:
            sebi = sources["sebi"]
            sentiment = sebi.get("sentiment", {})
            label_display = self._format_sentiment_label(sentiment.get("label", "neutral"))
            source_table.add_row(
                "SEBI Announcements",
                label_display,
                str(sebi.get("announcement_count", 0)),
                f"{sebi.get('confidence', 0) * 100:.0f}%"
            )

        self.console.print(source_table)

        # Interpretation
        self._display_interpretation(overall)

    def _format_sentiment_label(self, label: str) -> str:
        """Format sentiment label with color."""
        if label == "positive":
            return "[green]Positive[/green]"
        elif label == "negative":
            return "[red]Negative[/red]"
        else:
            return "[yellow]Neutral[/yellow]"

    def _display_interpretation(self, overall: Dict):
        """Display interpretation of sentiment."""
        score = overall["score"]
        label = overall["label"]

        self.console.print("\n[bold]What This Means:[/bold]")

        if label == "positive":
            if score > 0.5:
                self.console.print("  📈 [green]Strongly positive sentiment detected![/green]")
                self.console.print("     Market sentiment is very bullish")
                self.console.print("     Consider: Stock may see buying pressure")
            elif score > 0.2:
                self.console.print("  📊 [green]Moderately positive sentiment[/green]")
                self.console.print("     Market sentiment is somewhat bullish")
                self.console.print("     Consider: Cautiously optimistic outlook")
            else:
                self.console.print("  ➡️  [green]Slightly positive sentiment[/green]")
                self.console.print("     Market sentiment is mildly bullish")
                self.console.print("     Consider: Watch for confirmation")

        elif label == "negative":
            if score < -0.5:
                self.console.print("  📉 [red]Strongly negative sentiment detected![/red]")
                self.console.print("     Market sentiment is very bearish")
                self.console.print("     Consider: Stock may face selling pressure")
            elif score < -0.2:
                self.console.print("  📊 [red]Moderately negative sentiment[/red]")
                self.console.print("     Market sentiment is somewhat bearish")
                self.console.print("     Consider: Proceed with caution")
            else:
                self.console.print("  ➡️  [red]Slightly negative sentiment[/red]")
                self.console.print("     Market sentiment is mildly bearish")
                self.console.print("     Consider: Monitor closely")

        else:
            self.console.print("  ➡️  [yellow]Neutral sentiment[/yellow]")
            self.console.print("     Market sentiment is balanced")
            self.console.print("     Consider: Wait for clearer signals")

        # Confidence warning
        confidence = overall.get("confidence", 0.0)
        if confidence < 0.3:
            self.console.print("\n  ⚠️  [yellow]Low confidence - limited data available[/yellow]")
        elif confidence < 0.6:
            self.console.print("\n  ⚠️  [yellow]Moderate confidence - interpret carefully[/yellow]")
        else:
            self.console.print("\n  ✓ [green]High confidence - sufficient data analyzed[/green]")
