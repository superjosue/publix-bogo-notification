import logging

from publix_bogos.producer import BogoProducer


class LoggingBogoProducer(BogoProducer):
    """Console BOGO Producer."""

    def __init__(self, _config: dict | None = None) -> None:
        super().__init__()
        self.logger = logging.getLogger(__name__)


    def publish_bogo(self, bogo_items: list[str]) -> bool:
        """Publish BOGO item to Logs.

        Args:
            bogo_items (list[str]): BOGO items to publish.

        Returns:
            bool: true if BOGO items were published, otherwise false.
        """
        for bogo_text in bogo_items:
            self.logger.info(bogo_text)

        return True
