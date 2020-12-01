#!/usr/bin/env python3

import sys
import os
import requests
import re
from enum import Enum
from bs4 import BeautifulSoup

# GitHub: https://github.com/MichaelYochpaz/DWScraper

VERSION = "1.0.2"
SITE_URL = "https://www.digitalwhisper.co.il"
FORMAT = ".pdf"


class Mode(Enum):
    issue = 1
    articles = 2
    both = 3


def main():
    # disable print for SSL warnings
    requests.packages.urllib3.disable_warnings()

    # -- Arguments parsing starts here --
    if len(sys.argv) < 2:
        show_usage()

    if ("-h" in sys.argv or "--help" in sys.argv):
        show_help()

    elif ("-v" in sys.argv or "--version" in sys.argv):
        print("DWScraper " + VERSION)
        exit(0)

    download_type = sys.argv[1].lower()

    if download_type == "last":
        additional_args_index = 2

    elif download_type == "all":
        first_issue_number = 1
        last_issue_number = issue_url_to_number(find_last_issue_url())
        additional_args_index = 2
    
    elif download_type == "issue":
        if len(sys.argv) >= 3 and sys.argv[2].isdigit():
            issue_number = sys.argv[2]
            additional_args_index = 3

        else:
            show_usage()
    
    elif download_type == "range":
        if len(sys.argv) >= 3 and sys.argv[2].isdigit():
            if len(sys.argv) >= 4 and sys.argv[3].isdigit():
                first_issue_number = int(sys.argv[2])
                last_issue_number = int(sys.argv[3])
                additional_args_index = 4

            else:
                first_issue_number = 1
                last_issue_number = int(sys.argv[2])   
                additional_args_index = 3

        else:
            show_usage()

    else:
        show_usage()  

    additional_args = parse_optional_arguments(sys.argv[additional_args_index:])
    download_mode = additional_args[0]
    output = additional_args[1]
    # -- Arguments parsing ends here --

    if download_type == "last":
        download_issue(find_last_issue_url(), download_mode, output)

    elif download_type == "all" or download_type == "range":
        urls = []
        for i in range(first_issue_number, last_issue_number+1):
            urls.append(issue_number_to_url(i))

        download_issues(urls, download_mode, output)

    elif download_type == "issue":
        download_issue(issue_number_to_url(issue_number), download_mode, output)


# Parse the remaining arguments
def parse_optional_arguments(arguments: list):
    mode = Mode.issue
    output = os.getcwd()

    for i,arg in enumerate(arguments):
        if (arg == "-m" or arg == "--download-mode"):
            if i < (len(arguments)-1):
                temp = arguments[i+1].lower()
                if temp == "issue" or temp == "articles" or temp == "both":
                    mode = Mode[temp]
                else:
                    show_usage()
            else:
                show_usage()

        if (arg == "-o" or arg == "--output"):
            if i < (len(arguments)-1):
                if os.path.exists(arguments[i+1]):
                    if arguments[i+1].endswith('/') or arguments[i+1].endswith('\\'):
                        output = arguments[i+1][:-1]
                    else:
                        output = arguments[i+1]
                else:
                    print(f"Folder {arguments[i+1]} could not be found.")
                    exit(2)
            else:
                show_usage()

    return (mode, output)


# Finds the URL of the last issue
def find_last_issue_url():
    LOOKUP_STRING = "הורד את הגליון האחרון"
    web_page = BeautifulSoup(requests.get(SITE_URL).text, "lxml")

    return web_page.find_all('a', string=LOOKUP_STRING)[0].attrs['href']


# Given an issue number, generate issue's URL
def issue_number_to_url(issue_number: int):
    return SITE_URL + "/issue" + str(issue_number)


# Given an issue URL, returns the issue's number
def issue_url_to_number(url: str):
    if url.endswith('/'):
        url = url[:-1]

    return int(url.replace(SITE_URL + "/issue",''))


def download_issue(url: str, mode: Mode, download_location: str):  
    successfull = True 
    web_page = BeautifulSoup(requests.get(url).text, "lxml")
    content_div = web_page.find("div", id="content")

    search_str = "תאריך יציאה: "
    date_str = content_div.find_all(text = re.compile(search_str))[0]
    date = date_str[date_str.find("תאריך יציאה: ") + 13 : date_str.rfind(')')]
    issue_number = issue_url_to_number(url)
    issue_name = format_issue_name(issue_number, date)
    
    if mode == Mode.articles or mode == Mode.both:
        download_location = download_location + "\\" + issue_name
        if not os.path.exists(download_location):
            os.mkdir(download_location)

        for article in content_div.find("tbody").find_all('a'):
            download_url = relative_path_to_absolute(article.attrs['href'])

            if not download_file(download_url, format_article_name(article.text) + FORMAT, download_location):
                successfull = False

    if mode == Mode.issue or mode == Mode.both:
        download_url = f"https://www.digitalwhisper.co.il/files/Zines/{hex(issue_number)}/DigitalWhisper{issue_number}.pdf"

        if requests.get(download_url).status_code != 200:
            # Fallback - If previous method to generate download url doesn't work, find and use the download link on issue's page
            download_url = relative_path_to_absolute(content_div.find_all('a', text="כאן")[0].attrs["href"])
        
        if not download_file(download_url, issue_name + FORMAT, download_location):
            return False

    if successfull:
        print(f"Issue {issue_number} downloaded successfully.")


def download_issues(urls: list, mode: Mode, download_location: str):
    for url in urls:
        download_issue(url, mode, download_location)


# Downloads a file and returns True if successfull, False if not.
def download_file(url: str, file_name: str, path: str):
    file_path = path + "/" + file_name

    try:
        with open(file_path, 'wb') as file:
            try:
                file.write(requests.get(url, allow_redirects=True, verify=False).content)
            
            except Exception as e:
                print(f'Could not download "{file_name}.', "Error: " + str(e), sep="\n")
                return False

    except Exception as e:
        print(e)
        return False

    return True


# If the path is relative (example: "../../file.pdf"), change it to an absolute path
def relative_path_to_absolute(url: str):
    if "../.." in url:
        return SITE_URL + url.replace("../..", "")

    elif url.startswith("files/"):
        return SITE_URL + "/" + url

    return url


# Format a fixed & valid file name for an issue
def format_issue_name(issue_number: int, date: str):
    fixed_date = date.split("/")

    if fixed_date[0][0] != "0" and int(fixed_date[0]) < 10:
        fixed_date[0] = "0" + fixed_date[0]

    if fixed_date[1][0] != "0" and int(fixed_date[1]) < 10:
        fixed_date[1] = "0" + fixed_date[1]

    if len(fixed_date[2]) == 2:
        fixed_date[2] = "20" + fixed_date[2]

    return f"גליון {issue_number} - {'.'.join(fixed_date)}"


# Format a valid file name for an article
def format_article_name(name: str):
    return name.replace(": ", " - ").replace(":", "-").replace("/", "-").replace("\\", "-").replace("?", "").replace('"', "").replace("\r", "").replace("\n", "")


def show_usage():
    print(f"Usage: {os.path.basename(__file__)} (last | all | issue <issue-number> | range [start] <end>) [-m <issue | articles | both>] [-o PATH] [-h] [-v]",
    'For more info use "-h" or "--help"', sep="\n")
    exit(2)


def show_help():
    name = os.path.basename(__file__)
    print(f"Usage: {name} (last | all | issue <issue-number> | range [start] <end>) [-m <issue | articles | both>] [-o PATH] [-h] [-v]\n",
    "last                   Download the most recent issue.",
    "issue <issue-number>   Download a specific issue.",
    "all                    Download all available issues.",
    "range [start] <end>    Download all issues between a range of numbers.",
    "                       If a single arguments is given, the range will start with 1.",
    "\nOptions:",
    "-h, --help             Print this help menu and exit.",
    "-v, --version          Print program version and exit.",
    "-m, --mode <mode>      Set download mode. Options are:",
    '                       "issue" - download full issues (default),',
    '                       "articles" - download articles of issues as separate files,',
    '                       "both" - download both full issues and separate article files.',
    "-o, --output           Set output folder to download files to (default: current working directory).\n",
    sep="\n")
    exit(0)


if __name__ == "__main__":
    main()