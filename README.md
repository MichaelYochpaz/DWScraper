# DWScraper
A Python web-scraper for downloading [DigitalWhisper](https://www.digitalwhisper.co.il) issues.

## Usage
```
Usage: DWScraper (last | all | issue <issue-number> | range [start] <end>) [-m <issue | articles | both>] [-o PATH] [-h] [-v]

last                   Download the most recent issue.
issue <issue-number>   Download a specific issue number.
all                    Download all available issues.
range [start] <end>    Download all issues between a range of numbers.
                       If a single arguments is given, the range will start with 1.

Options:
-h, --help             Print this help menu and exit.
-v, --version          Print program version and exit.
-m, --mode <mode>      Set download mode. Options are:
                       "issue" to download full issues (default),
                       "articles" to download articles of issues as separate files,
                       "both" to download both full issues and separate article files.
-o, --output           Set output folder to download files to (default: current working directory).
```
