class BogoProducer:
    """Interface for BOGO producers.
    """
    def publish_bogo(self, bogo_items: list[str]) -> bool:
        raise NotImplementedError("publish_bogo is not implemented")
