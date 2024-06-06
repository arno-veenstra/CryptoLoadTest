'''
Copyright (C) 2018-2024  Bryant Moscon - bmoscon@gmail.com
Please see the LICENSE file for the terms and conditions
associated with this software.
'''

import os
import logging
from datetime import datetime

from cryptofeed import FeedHandler
from cryptofeed.raw_data_collection import AsyncFileCallback
from cryptofeed.exchanges import EXCHANGE_MAP
from cryptofeed.feed import Feed
from cryptofeed.defines import L2_BOOK, TICKER, TRADES, FUNDING, CANDLES, OPEN_INTEREST, LIQUIDATIONS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

async def log_trade(obj, receipt_ts):
    rts = datetime.utcfromtimestamp(receipt_ts).strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"{rts} - {obj}")

def load_config() -> Feed:
    exchange = os.environ.get('EXCHANGE')
    symbols = os.environ.get('SYMBOLS')

    if symbols is None:
        raise ValueError("Symbols must be specified")
    symbols = symbols.split(",")

    channels = os.environ.get('CHANNELS')
    if channels is None:
        raise ValueError("Channels must be specified")
    channels = channels.split(",")

    config = os.environ.get('CONFIG')
    snap_only = os.environ.get('SNAPSHOT_ONLY', False)
    if snap_only:
        if snap_only.lower().startswith('f'):
            snap_only = False
        elif snap_only.lower().startswith('t'):
            snap_only = True
        else:
            raise ValueError('Invalid value specified for SNAPSHOT_ONLY')
    snap_interval = os.environ.get('SNAPSHOT_INTERVAL', 1000)
    snap_interval = int(snap_interval)
    candle_interval = os.environ.get('CANDLE_INTERVAL', '1m')

    cbs = {
        L2_BOOK: log_trade,
        TRADES: log_trade,
        TICKER: log_trade,
        FUNDING: log_trade,
        CANDLES: log_trade,
        OPEN_INTEREST: log_trade,
        LIQUIDATIONS: log_trade
    }

    # Prune unused callbacks
    remove = [chan for chan in cbs if chan not in channels]
    for r in remove:
        del cbs[r]

    return EXCHANGE_MAP[exchange](candle_interval=candle_interval, symbols=symbols, channels=channels, config=config, callbacks=cbs)

def main():
    save_raw = os.environ.get('SAVE_RAW', False)
    if save_raw:
        if save_raw.lower().startswith('f'):
            save_raw = False
        elif save_raw.lower().startswith('t'):
            save_raw = True
        else:
            raise ValueError('Invalid value specified for SAVE_RAW')

    fh = FeedHandler(raw_data_collection=AsyncFileCallback("./raw_data") if save_raw else None)
    cfg = load_config()
    fh.add_feed(cfg)
    fh.run()

if __name__ == '__main__':
    main()
