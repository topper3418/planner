import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Define the project root and logs directory
LOGS_DIR = Path("data/log")
# Ensure logs directory exists
LOGS_DIR.mkdir(exist_ok=True)

# Custom filter for logs from your modules (excluding 3rd-party)
class AppModuleFilter(logging.Filter):
    def filter(self, record):
        # Include logs from your src/ modules, exclude 3rd-party
        return record.name.startswith("src.") and not record.name.startswith("src.third_party")

# Custom filter for processing module logs
class ProcessingModuleFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith("src.processor") or \
                record.name.startswith("src.grok")

# Custom filter for all package logs (yours and 3rd-party)
class AllPackagesFilter(logging.Filter):
    def filter(self, record):
        # Include logs from all packages under src/
        return record.name.startswith("src.")

# Custom filter to exclude 3rd-party logs (used in testing)
class NoThirdPartyFilter(logging.Filter):
    def filter(self, record):
        # Exclude logs from known 3rd-party modules
        third_party_prefixes = [
            "requests", 
            "urllib3", 
            "botocore", 
            "asyncio", 
            "httpx",
            "httpcore",
            "openai",
        ]
        return not any(record.name.startswith(prefix) for prefix in third_party_prefixes)

def setup_normal_logging():
    # Clear any existing handlers to avoid duplicates
    logging.getLogger().handlers.clear()

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels, filter at handlers

    # Formatter for log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Handler 1: Logs from your modules (app_modules.log)
    app_handler = RotatingFileHandler(
        LOGS_DIR / "app_modules.log", maxBytes=50 * 1024 * 1024, backupCount=5
    )
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(formatter)
    app_handler.addFilter(AppModuleFilter())
    root_logger.addHandler(app_handler)

    # Handler 2: Logs from all packages (all_packages.log)
    all_packages_handler = RotatingFileHandler(
        LOGS_DIR / "all_packages.log", maxBytes=50 * 1024 * 1024, backupCount=5
    )
    all_packages_handler.setLevel(logging.DEBUG)
    all_packages_handler.setFormatter(formatter)
    all_packages_handler.addFilter(AllPackagesFilter())
    root_logger.addHandler(all_packages_handler)

    # Handler 3: Logs from processing module (processing_module.log)
    processing_handler = RotatingFileHandler(
        LOGS_DIR / "processing_module.log", maxBytes=50 * 1024 * 1024, backupCount=5
    )
    processing_handler.setLevel(logging.DEBUG)
    processing_handler.setFormatter(formatter)
    processing_handler.addFilter(ProcessingModuleFilter())
    root_logger.addHandler(processing_handler)

    # Suppress 3rd-party logs in general (set to WARNING)
    third_party_loggers = ["requests", "urllib3", "botocore", "asyncio"]
    for logger_name in third_party_loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Optional: Console handler for debugging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

def setup_test_logging():
    """Configure logging for tests, suppressing 3rd-party logs."""
    setup_normal_logging()  # Start with default setup
    root_logger = logging.getLogger()
    
    # Add NoThirdPartyFilter to all handlers
    for handler in root_logger.handlers:
        handler.addFilter(NoThirdPartyFilter())

if __name__ == "__main__":
    # Example usage
    setup_normal_logging()
    logger = logging.getLogger("src.processing_module.processor")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
