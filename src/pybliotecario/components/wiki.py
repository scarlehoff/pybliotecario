"""
    Module to read and send content from wikipedia
"""

# TODO use the selected language

import re

import wikipedia

from pybliotecario.components.component_core import Component

# log = logging.getLogger(__name__)
GET_N = re.compile(r"^\d+")
MAX_SIZE = 4000
WIKI_NAME = "WIKIPEDIA"
DEFAULT_LANGUAGE = "EN"


class WikiComponent(Component):
    """
    Read content from wikipedia and send it to instagram
    """

    help_text = """ > Wikipedia module
    /wiki term: search for term in wikipedia, return the summary
    /wiki_full N term: read the full article and return N times the defined summary_size"""

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        wiki_config = self.read_config_section(WIKI_NAME)
        self.summary_size = int(wiki_config.get("msg_size", 1024))
        self.language = wiki_config.get("language", DEFAULT_LANGUAGE)
        wikipedia.set_lang(self.language)

    @classmethod
    def configure_me(cls):
        print(
            f"""
# Wikipedia Module
This is the configuration helper for the wikipedia module
Introduce the length of the msgs you want to obtain (max: {MAX_SIZE}):"""
        )
        summary_size = 0
        while summary_size > MAX_SIZE or summary_size < 1:
            # The max msg in telegram is 4096 UTF char.
            try:
                summary_size = int(input(" > "))
            except ValueError:
                print(f"Please, write a number between 0 and {MAX_SIZE}")
        possible_languages = ["EN", "ES", "IT"]
        language = None
        print("Introduce the default language for Wikipedia pages")
        while language not in possible_languages:
            language = input(
                f" > Possible choices: {possible_languages} (default: {DEFAULT_LANGUAGE}) > "
            )
            if language == "":
                language = DEFAULT_LANGUAGE
        dict_out = {WIKI_NAME: {"msg_size": summary_size, "language": language}}
        return dict_out

    def get_page(self, term):
        """Gets the wikipedia page given by `term`
        If `term` returns a disambiguation page, returns a string with the options
        """
        try:
            wiki_page = wikipedia.page(term)
            return wiki_page
        except wikipedia.exceptions.DisambiguationError:
            other_terms = wikipedia.search(term)
            response = "Found disambiguation page, please try with one of these other terms: "
            response += ", ".join(other_terms)
        except wikipedia.exceptions.PageError:
            response = f"Sorry, no Wikipedia pages were found for this query: {term}"
        self.send_msg(response)
        return None

    def read_summary(self, term):
        """Gets the page given by `term` and returns a summary
        The size of the summary is given by the `summary_size` variable
        """
        wiki_page = self.get_page(term)
        if wiki_page is not None:
            summary = wiki_page.summary[: self.summary_size]
            number_of_msg = int(len(wiki_page.content) / self.summary_size)
            summary += f"\n\n This page will need {number_of_msg} msgs for the whole content"
            self.send_msg(summary)

    def read_msg_fullpage(self, msg):
        """Breaks the msg = "N term to search for" into
        N (number) and the term to search for (string)
        """
        reg_n = GET_N.search(msg)
        if reg_n is None:
            error = f"""For a whole page, write the query in the form /wiki_full N search_term
where N is the number of msgs of size {self.summary_size} you want to receive"""
            self.send_msg(error)
            return 0, None
        n_str = reg_n[0]
        n_int = int(n_str)
        term = msg.replace(n_str, "").strip()
        return n_int, term

    def read_whole_page(self, term, n_msg):
        """
        Given a `term` to search for and a number of msgs to read `n_msg`
        sends the first `n_msg`*`self.summary_size` of the
        corresponding wikipedia page
        """
        wiki_page = self.get_page(term)
        if wiki_page is not None:
            whole_page = wiki_page.content
            total_length = len(whole_page)
            final_length = min(total_length, n_msg * self.summary_size)
            for char in range(0, final_length, self.summary_size):
                response = whole_page[char : char + self.summary_size]
                self.send_msg(response)

    def telegram_message(self, msg):
        """Digest the telegram msg"""
        command = msg.command
        if command == "wiki":
            self.read_summary(msg.text.strip())
        elif command == "wiki_full":
            n_msg, term = self.read_msg_fullpage(msg.text.strip())
            if n_msg > 0:
                self.read_whole_page(term, n_msg)
