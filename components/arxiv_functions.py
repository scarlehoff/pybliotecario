# arxiv-useful functions

import arxiv

from datetime import datetime
from datetime import timedelta
import time
import os
from ipdb import set_trace

def is_today(time_struct, i = None):
    """
    Checks whether the given time_struct corresponds to today
    or to the previous day
    Remember, the previous day for arxiv purposes only starts at 19.00 
    """
    # First we need to find out which day is today
    today = datetime.now()
    day = today.day
    wday = today.weekday() # 0 == Monday
    base_hour = 18

    if wday < 2:
        # If today is monday or tuesday, we should look at thursday/friday for the cutoff
        base_today = today - timedelta(days = 4)
    else: # yesterday
        base_today = today - timedelta(days = 2)
    base_today = base_today.replace(hour = base_hour, minute=0, second=0, microsecond=0)

    # Make the time struct into a datetime object
    dt = datetime.fromtimestamp(time.mktime(time_struct))

    # Now, if the paper date (dt) is from before the base time (base_today), that means it is not from today
    return dt >= base_today

def query_recent(category):
    """
    Query the arxiv for the updates of the last day for a given category
    """
    update_key = 'updated_parsed'
    results = arxiv.query( search_query = category, max_results = 50, sort_by = "lastUpdatedDate" )
    try:
        today = results[0][update_key]
    except:
        print("Nothing was found in the arxiv for the category: {0}, check that it is correct".format(category))
        return []
    indx = 1
    for i, element in enumerate(results):
        time_s = element[update_key]
        if not is_today(time_s, i = i):
            indx = i
            break
    return results[:indx]


def filter_results(result_list, filter_dictionary):
    """
    Given a dictionary and a list of results (paper dictionaries)
    returns the results which pass the filter
    The items in the filter_dictionary must be a list
    """ # TODO: save the reason for the query to pass
    lista = []
    for paper in result_list:
        done = False
        for key, item in filter_dictionary.items():
            if done: break
            val = paper[key]
            for keyword in item:
                if isinstance(val, str):
                    if keyword.lower() in val.lower():
                        lista.append(paper)
                        done = True
                        break
                elif isinstance(val, list):
                    if done: break
                    for keyval in val:
                        if keyword.lower() in keyval.lower():
                            lista.append(paper)
                            done = True
                            break
    # Ok, this might be very dangerous here
    return lista

def url_to_id(arxiv_url):
    """
    Given an arxiv url return the corresponding id
    if arxiv_url is already an id, returns unchanged
    """
    return os.path.basename(arxiv_url)
    

# Telegram-usable functions
def arxiv_get_pdf(arxiv_id_raw):
    """ Downloads a paper from the arxiv given an id """
    arxiv_id = url_to_id(arxiv_id_raw)
    # First we recover the information about the paper
    paper = arxiv.query( id_list=[arxiv_id] )[0]
    # Now download the pdf (the download command only needs a dictionary with the pdf_url, but that is given by the query)
    file_name = arxiv.download(paper)
    return file_name

def arxiv_recent_filtered(categories, filter_dict, abstract = False):
    lines = []
    for category in categories:
        tmp = query_recent(category)
        results = filter_results(tmp, filter_dict)
        line = "{0} new papers in {1}, {2} interesting ones: \n".format(len(tmp), category, len(results))
        for paper in results:
            authors = ", ".join(paper['authors'])
            title = paper['title']
            arxiv_id = os.path.basename(paper['id']).replace('v1', '')
            line += " > {2}: {0}\n     by {1}\n".format(title, authors, arxiv_id)
            if abstract:
                line += paper['summary']
        lines.append(line)
    return "\n".join(lines)

def arxiv_query_info(arxiv_id_raw):
    """
    Returns extra information about the queried paper
    """
    arxiv_id = url_to_id(arxiv_id_raw)
    paper = arxiv.query( id_list=[arxiv_id] )[0]
    title = paper['title']
    authors = ", ".join(paper['authors'])
    abstract = paper['summary']
    msg = """ > {0}
Title: {1} 

Authors: {2}

Abstract: {3}""".format(arxiv_id, title, authors, abstract)
    return msg

if __name__ == "__main__":
    print("Testing the arxiv component")
    print("Query a category")
    category = "hep-ph"
    recent_papers = query_recent(category)
    dict_search = {'title' : ["Higgs"], 'authors' : ['Cruz-Martinez'], 'summary' : ["VBF"]}
    filter_papers = filter_results(recent_papers, dict_search)
    tlg_msg = arxiv_recent_filtered([category], dict_search)
    print(tlg_msg)

#     print("Test download")
#     test_id = "1802.02445"
#     name = arxiv_get_pdf(test_id)
#     os.remove(name)
