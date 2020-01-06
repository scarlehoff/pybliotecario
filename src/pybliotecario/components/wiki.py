"""
    Module to read and send content from wikipedia
"""

# TODO use one of the more advance API instead of the wikipedia module
# TODO ask for default language during initialization
# TODO ask for the size of the summary 
# TODO get full length of the page

import regex
import logging
import wikipedia
from pybliotecario.components.component_core import Component

log = logging.getLogger(__name__)
get_n = regex.compile("^\d+")


class WikiComponent(Component):
    """
    Read content from wikipedia and send it to instagram
    """

    help_text = """ > Wikipedia module
    /wiki term: search for term in wikipedia, return the summary
    /wiki_full N term: read the full article and return N times the defined summary_size
    """

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        self.summary_size = 1024

    def get_page(self, term):
        try:
            wiki_page = wikipedia.page(term)
            return wiki_page
        except wikipedia.exceptions.DisambiguationError:
            other_terms = wikipedia.search(term)
            response = "Found disambiguation page, please try with one of these other terms: "
            response += ", ".join(other_terms)
        except wikipedia.exceptions.PageError:
            response = "Sorry, no Wikipedia pages were found for this query: {0}".format(term)
        self.send_msg(response)
        return None

    def read_summary(self, term):
        wiki_page = self.get_page(term)
        if wiki_page is None:
            return None
        summary = wiki_page.summary[:self.summary_size]
        self.send_msg(summary)

    def read_whole_page(self, msg):
        # First break the msg and the number of msgs we want
        reg_n = get_n.search(msg)
        if reg_n is None:
            error = """For a whole page, write the query in the form /wiki_full N search_term
where N is the number of msgs of size {0} you want to receive""".format(self.summary_size)
            self.send_msg(error)
            return None
        n_str = reg_n[0]
        n = int(n_str)
        term = msg.replace(n_str, '').strip()
        wiki_page = self.get_page(term)
        if wiki_page is None:
            return None
        whole_page = wiki_page.content
        total_length = len(whole_page)
        final_length = min(total_length, n*self.summary_size)
        for char in range(0, final_length, self.summary_size):
            response = whole_page[char:char+self.summary_size]
            self.send_msg(response)

    def telegram_message(self, msg):
        command = msg.command
        if command == "wiki":
            self.read_summary(msg.text.strip())
        elif command == "wiki_full":
            self.read_whole_page(msg.text.strip())
