"""
    Module using the arxiv API for prelog.info tracking
    update notifications and quick-querying from the Telegram app
"""

import os
import time
import logging
from datetime import datetime, timedelta, timezone
import arxiv
from pybliotecario.components.component_core import Component

log = logging.getLogger(__name__)


def is_today(time_to_test):
    """
    Checks whether the given time to test corresponds to today
    or to the previous day
    Remember, the previous day for arxiv purposes only starts at 19.00
    """
    # First we need to find out which day is today
    today = datetime.now(timezone.utc)
    wday = today.weekday()  # 0 == Monday
    base_hour = 18

    if wday < 2:
        # If today is monday or tuesday, we should look at thursday/friday for the cutoff
        base_today = today - timedelta(days=4)
    else:  # yesterday
        base_today = today - timedelta(days=2)
    base_today = base_today.replace(hour=base_hour, minute=0, second=0, microsecond=0)

    # Now, if the paper date (pdt) is from before the base time (base_today), that means it is not from today
    return time_to_test >= base_today


def query_recent(category):
    """
    Query the arxiv for the updates of the last day for a given category
    """
    results = arxiv.Search(
        query=category, max_results=75, sort_by=arxiv.SortCriterion.LastUpdatedDate
    ).results()
    indx = -1
    elements = []
    for i, element in enumerate(results):
        time_s = element.updated
        if not is_today(time_s):
            break
        elements.append(element)
    return elements


def check_keyword(paper_value, keyword):
    """Check whether the given keywords exists in the given paper value"""
    if isinstance(paper_value, list):
        return any([check_keyword(i, keyword) for i in paper_value])
    str_value = str(paper_value)
    return keyword.lower() in str_value.lower()


def filter_results(result_list, filter_dictionary):
    """
    Given a dictionary and a list of results (paper dictionaries)
    returns the results which pass the filter
    The items in the filter_dictionary must be a list
    """  # TODO: save the reason for the query to pass
    lista = []
    for paper in result_list:
        done = False
        for key, keywords in filter_dictionary.items():
            if done:
                break
            try:
                val = getattr(paper, key)
            except AttributeError:
                log.error("Error trying to read key: %s", key)

            for keyword in keywords:
                if check_keyword(val, keyword):
                    lista.append(paper)
                    done = True
                    break
    return lista


def url_to_id(arxiv_url):
    """
    Given an arxiv url return the corresponding id
    if arxiv_url is already an id, returns unchanged
    """
    return os.path.basename(arxiv_url)


# Telegram-usable functions
def arxiv_get_pdf(arxiv_id_raw):
    """Downloads a paper from the arxiv given an id"""
    arxiv_id = url_to_id(arxiv_id_raw)
    # First we recover the information about the paper
    paper = next(arxiv.Search(id_list=[arxiv_id]).results())
    return paper.download_pdf("/tmp/")


def arxiv_recent_filtered(categories, filter_dict, abstract=False, max_authors=50):
    """Read all recent papers in each categories and save the ones matching the
    requirements of filter_dict"""
    lines = []
    for category in categories:
        tmp = query_recent(category)
        results = filter_results(tmp, filter_dict)
        line = "{0} new papers in {1}, {2} interesting ones: \n".format(
            len(tmp), category, len(results)
        )
        for paper in results:
            paper_authors = paper.authors
            if len(paper_authors) > max_authors:
                paper_authors = paper_authors[:max_authors] + ["et al"]
            authors = ", ".join(str(i) for i in paper_authors)
            title = paper.title
            arxiv_id = paper.get_short_id().replace("v1", "")
            line += f" > {title}: {title}\n     by {arxiv_id}\n"
            if abstract:
                line += paper["summary"]
        lines.append(line)
    return "\n".join(lines)


def arxiv_query_info(arxiv_id_raw):
    """
    Returns extra information about the queried paper
    """
    arxiv_id = url_to_id(arxiv_id_raw)
    paper = next(arxiv.Search(id_list=[arxiv_id]).results())
    title = paper.title
    authors = [str(i) for i in paper.authors]
    abstract = paper.summary.replace("\n", " ")
    msg = f""" > {arxiv_id}
Title: {paper.title}

Authors: {authors}

Abstract: {abstract}
    """
    return msg


class Arxiv(Component):

    help_text = """ > Arxiv module
    /arxiv arxiv_id: sends information about the given id
    /arxiv_get arxiv_id: sends the PDF for the given id """

    def __init__(self, telegram_object, configuration=None, **kwargs):
        super().__init__(telegram_object, configuration=configuration, **kwargs)
        arxiv_config = self.read_config_section("ARXIV", telegram_error=False)
        title = arxiv_config.get("title", "")
        abstract = arxiv_config.get("summary", "")
        authors = arxiv_config.get("authors", "")
        self._max_authors = arxiv_config.get("max_authors", 20)
        self.filter_dict = {
            "title": self.split_list(title),
            "summary": self.split_list(abstract),
            "authors": self.split_list(authors),
        }
        self.categories = self.split_list(arxiv_config.get("categories", ""))

    @classmethod
    def configure_me(cls):
        print("")
        print(" # Arxiv module ")
        print("This is the configuration helper for the arxiv module")
        print("First introduce (comma-separated) the categories you are interested in: ")
        categories = input(" > ")
        print(
            "Now introduce (again, comma-separated) the keywords you want to check the titles for"
        )
        title_keywords = input(" > ")
        print("Same for checking the abstract:")
        summary_keywords = input(" > ")
        print("And now authors")
        authors_keywords = input(" > ")
        dict_out = {
            "ARXIV": {
                "categories": categories,
                "title": title_keywords,
                "summary": summary_keywords,
                "authors": authors_keywords,
            }
        }
        return dict_out

    def cmdline_command(self, args):
        """
        Reads the latests arrivals to the arxiv and
        sends a notification if any of the entries fullfill any of
        the requirements set in the config file
        """
        msg = arxiv_recent_filtered(
            self.categories, self.filter_dict, max_authors=self._max_authors
        )
        self.send_msg(msg)
        log.info("Arxiv information sent")

    def telegram_message(self, msg):
        command = msg.command
        arxiv_id = msg.text.strip()
        if not arxiv_id:
            self.send_msg("This commands needs an argument")
            return
        if command in ("arxivget", "arxiv-get", "arxiv_get"):
            file_send = arxiv_get_pdf(arxiv_id)
            self.send_file(file_send, delete=True)
        else:
            msg = arxiv_query_info(arxiv_id)
            self.send_msg(msg)


if __name__ == "__main__":
    from pybliotecario.pybliotecario import logger_setup
    import tempfile

    logger_setup(tempfile.TemporaryFile(), debug=True)
    log.info("Testing the arxiv component")
    log.info("Query a category")
    categoria = "hep-ph"
    recent_papers = query_recent(categoria)
    dict_search = {
        "title": ["Higgs", "neutrinos"],
        "authors": ["Cruz-Martinez"],
        "summary": ["VBF"],
    }
    filter_papers = filter_results(recent_papers, dict_search)
    log.warning(filter_papers)
    tlg_msg = arxiv_recent_filtered([categoria], dict_search)
    log.info(tlg_msg)

#     log.info("Test download")
#     test_id = "1802.02445"
#     name = arxiv_get_pdf(test_id)
#     os.remove(name)
