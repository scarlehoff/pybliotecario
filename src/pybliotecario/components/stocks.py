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
from dataclasses import dataclass
from yahoo_fin import stock_info

from pybliotecario.components.component_core import Component

logger = logging.getLogger(__name__)


### All checks to be applied, take ticket name, current price and conditions dictionary
def below(price, ticket, conditions):
    """ Check whether the price is below the threshold """
    thrs = conditions["below"]
    if price < thrs:
        return f"{ticket} price is below the threshold: {price:.3f} < {thrs}"
    return None


def above(price, ticket, conditions):
    """ Check whether the price is below the threshold """
    thrs = conditions["above"]
    if price > thrs:
        return f"{ticket} price is above the threshold: {price:.3f} > {thrs}"
    return None


CHECKS = [below, above]


def checking_conditions(price, ticket, conditions):
    """
    Check the price against the given conditions to decide on the msg to send (if any)
    """
    for check in CHECKS:
        if check.__name__ in conditions:
            ret = check(price, ticket, conditions)
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
    for ticket, conditions in information.items():
        try:
            current_price = stock_info.get_live_price(ticket)
            ret = checking_conditions(current_price, ticket, conditions)
            if ret is not None:
                results.append(ret)
        except AssertionError:
            logger.warning(f"Ticket {ticket} not found")
        except:  # yahoo-fin is not the most stable piece of software
            logger.warning(f"There was a non-expected error with {ticket}")
    return results


class Stocks(Component):

    key_name = "STOCKS"
    help_text = """ > Stocks module
    /stocks_value ticket: get the most recent information about the given ticket """

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

if __name__ == "__main__":
    import tempfile
    json_example = {
    "AAPL" : {
        "below" : 140,
        "above" : 110
    },
    "TSLA" : {
        "below" : 1000,
        "above" : 200,
    }}
    tmp = tempfile.mktemp()
    with open(tmp, 'w') as f:
        json.dump(json_example, f)
    msgs = check_stock(tmp)
    for i, msg in enumerate(msgs):
        print(f"Message #{i+1}: {msg}")
