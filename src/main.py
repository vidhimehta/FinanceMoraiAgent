"""
Main entry point for FinanceMoraiAgent.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli.menu import CLIMenu
from src.utils.logger import setup_logger
from src.utils.helpers import load_config, get_project_root


def main():
    """Main entry point."""
    try:
        # Load environment variables
        env_file = get_project_root() / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            print(f"Loaded environment from {env_file}")

        # Load configuration
        config_file = get_project_root() / "config" / "settings.yaml"
        if not config_file.exists():
            print(f"Warning: Config file not found at {config_file}")
            config = {}
        else:
            config = load_config(str(config_file))

        # Setup logging
        log_config = config.get("logging", {})
        setup_logger(
            log_level=log_config.get("level", "INFO"),
            log_file=log_config.get("destinations", {}).get("file_path", "storage/app.log"),
            rotation=log_config.get("rotation", "100 MB"),
            retention=log_config.get("retention", "30 days"),
            console_output=log_config.get("destinations", {}).get("console", True),
        )

        logger.info("=" * 60)
        logger.info("FinanceMoraiAgent Starting")
        logger.info("=" * 60)

        # Initialize and run CLI menu
        menu = CLIMenu()
        menu.run()

        logger.info("FinanceMoraiAgent Exiting")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        logger.exception("Fatal error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
