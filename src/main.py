import yaml
from logging.logger import setup_logger
from posting.poster import Poster


def load_config(path="config/forums.yaml"):
    """
    Loads YAML configuration for all forums.
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    logger = setup_logger()

    logger.info("=== Backlink Agent Started ===")

    # Load forum configuration
    config = load_config()

    # Initialize posting engine
    poster = Poster(config, logger)

    # Run all forums
    poster.run_all()

    logger.info("=== Backlink Agent Finished ===")


if __name__ == "__main__":
    main()
