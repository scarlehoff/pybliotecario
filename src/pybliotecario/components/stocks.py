"""
    Use yahoo_fin: http://theautomatic.net/yahoo_fin-documentation/
    to obtain information of stock prices

    The watch list is a json like:
    {
    "AAPL" : {
        "below" : 100,
        "above" : 170
    },

"""
import json
import logging
from yahoo_fin import stock_info

from pybliotecario.components.component_core import Component

logger = logging.getLogger(__name__)


### All checks to be applied, take ticker name, current price and conditions dictionary
def below(price, ticker, conditions):
    """ Check whether the price is below the threshold """
    thrs = conditions["below"]
    if price < thrs:
        return f"{ticker} price is below the threshold: {price:.3f} < {thrs}"
    return None


def above(price, ticker, conditions):
    """ Check whether the price is below the threshold """
    thrs = conditions["above"]
    if price > thrs:
        return f"{ticker} price is above the threshold: {price:.3f} > {thrs}"
    return None


CHECKS = [below, above]


def checking_conditions(price, ticker, conditions):
    """
    Check the price against the given conditions to decide on the msg to send (if any)
    """
    for check in CHECKS:
        if check.__name__ in conditions:
            ret = check(price, ticker, conditions)
            if ret is not None:
                # The first check that passes is sent
                return ret
    return None


def check_stock(json_file):
    """
    Reads up a json file given in the STOCKS::watch_json variable of the config file
    and sends a notification if any of the conditions occur
    """
    with open(json_file, "r") as f:
        information = json.load(f)
    results = []
    for ticker, conditions in information.items():
        try:
            current_price = stock_info.get_live_price(ticker)
            ret = checking_conditions(current_price, ticker, conditions)
            if ret is not None:
                results.append(ret)
        except AssertionError:
            logger.warning(f"ticker {ticker} not found")
        except:  # yahoo-fin is not the most stable piece of software
            logger.warning(f"There was a non-expected error with {ticker}")
    return results


class Stocks(Component):

    key_name = "STOCKS"
    help_text = """ > Stocks module
    /stock_value ticker: get the most recent information about the given ticker """

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        if self.key_name in configuration:
            self.stock_config = self.read_config_section("STOCKS")
        else:
            self.stock_config = None

    def cmdline_command(self, args):
        """`stock_watcher`: opens the given file and "follows the rules" """
        if args.stock_watcher is not None:
            if len(args.stock_watcher) == 0 and self.stock_config is not None:
                json_files = [self.stock_config.get("watch_json")]
            else:
                json_files = args.stock_watcher
            for ff in json_files:
                msgs = check_stock(ff)
                for msg in msgs:
                    self.send_msg(msg)

    def telegram_message(self, msg):
        command = msg.command
        ticker = msg.text.strip()
        if command == "stock_price":
            try:
                pp = stock_info.get_live_price(ticker)
                self.send_msg(f"{ticker} price: {pp:.3f}$")
            except:  # yahoo-fin not very stable :(
                self.send_msg(f"Unknown error trying to get information from {ticker}")


if __name__ == "__main__":
    import tempfile, os

    json_example = {
        "AAPL": {"below": 140, "above": 110},
        "TSLA": {
            "below": 1000,
            "above": 200,
        },
    }
    fd, tmp = tempfile.mkstemp(suffix=".json", text=True)
    with os.fdopen(fd, "w") as f:
        json.dump(json_example, f)
    msgs = check_stock(tmp)
    for i, msg in enumerate(msgs):
        print(f"Message #{i+1}: {msg}")
