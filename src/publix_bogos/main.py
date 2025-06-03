import configparser
import logging
from bs4 import BeautifulSoup

from publix_bogos.bogos import BogoItem, parse_webpage_bogos, retrieve_sales_webpage
from publix_bogos.console import LoggingBogoProducer
from publix_bogos.filter_prettify import filter_prettify_items
from publix_bogos.producer import BogoProducer
from publix_bogos.tweeter import TwitterBogoProducer

logger = logging.getLogger(__name__)


def main():
    # RawConfigParser is needed because things like Twitter API keys have characters like '%' in them
    config = configparser.RawConfigParser()
    config.read('config.ini')

    set_logging(config)

    logger.info('Config values:')

    if 'BOGO' not in config:
        logger.error('No BOGO config found. Exiting...')
        return

    bogo_config = config['BOGO']
    if not bogo_config.get('keywords') or not bogo_config.get('url'):
        logger.error('"keywords" or "url" was provided in the config. Exiting...')
        return

    keywords = bogo_config['keywords'].split(',')
    url = bogo_config['url']
    prefix_text = bogo_config.get('prefix_text', '')
    postfix_text = bogo_config.get('postfix_text', '')
    no_bogo_text = bogo_config.get('no_bogo_text', 'No BOGOs')

    logger.info('keywords: %s', keywords)
    logger.info('url: %s', url)
    if prefix_text:
        logger.info('prefix_text: %s', prefix_text)
    if postfix_text:
        logger.info('postfix_text: %s', postfix_text)
    logger.info('no_bogo_text: %s', no_bogo_text)

    bogo_items = retrieve_bogos(url)
    filtered_prettified_bogo_items = filter_prettify_items(bogo_items, keywords, prefix_text, postfix_text)

    publish_bogo_items(filtered_prettified_bogo_items or [no_bogo_text], config)


def set_logging(config: configparser.RawConfigParser):
    """Set the logging level based on the config otherwise default to INFO.

    Args:
        config (configparser.RawConfigParser): configuration object to look for the logging level.
    """
    log_level = logging.INFO
    if 'logging' in config and config['logging']['level']:
        log_level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARN': logging.WARNING,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            }
        log_level = log_level_mapping.get(config['logging']['level'], logging.INFO)

    logging.basicConfig(level=log_level)
    # Needed because AWS doesn't seem to understand the log level set via basicConfig
    logging.getLogger().setLevel(log_level)


def retrieve_bogos(bogo_url: str) -> list[BogoItem]:
    """Retrieve bogo items from the url provide.

    Args:
        bogo_url (str): url to retrieve the bogo items from

    Returns:
        list[(str, str)]: a tuple list of bogo items (<item name>, <bogo type>)
    """
    try:
        sales_content: BeautifulSoup = retrieve_sales_webpage(bogo_url)
        return parse_webpage_bogos(sales_content)
    except Exception as e:
        logger.error(e)

    return list()


def publish_bogo_items(bogo_items: list[str], config: configparser.RawConfigParser):
    """Publish bogo items to configured producers (config['BOGO']['producers']).

    Args:
        bogo_items (list[str]): BOGO items to publish.
        config (configparser.RawConfigParser): Configuration for where to publish BOGOs.
    """
    if 'producers' not in config['BOGO'] or not config['BOGO']['producers']:
        logger.warn('No producers are configured for publishing BOGOs.')
        return

    for producer_type in config['BOGO']['producers'].split(','):
        producer = build_producer(producer_type, config[producer_type])
        producer.publish_bogo(bogo_items)



def build_producer(producer_type, config: configparser.RawConfigParser) -> BogoProducer:
    """Build the appropriate producer.

    Args:
        producer_type (_type_): Producer type.
        config (configparser.RawConfigParser): Configuration to pass to the producer.

    Returns:
        BogoProducer: Built producer using the type and the config.
    """
    config_dict = dict(config)
    producers = {
        'twitter_producer': TwitterBogoProducer,
        'logging_producer': LoggingBogoProducer,
    }
    if producer_type not in producers:
        raise LookupError(f'No producer is found for type "{producer_type}"')
    return producers[producer_type](config_dict)


def lambda_handler(event, context):
    main()

if __name__ == '__main__':
    main()

