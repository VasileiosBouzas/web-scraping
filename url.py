import pandas as pd
import urllib.request
import numpy as np
import socket
from datetime import datetime
import logging


IMPORT = 'urls.txt'
EXPORT = 'results.txt'
LOGFILE = 'progress.log'


def printf(string, end=None):
    """
    print with timestamp
    """
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(f'{current_time}: {string}', end=end)


def print_log(string):
    """
    print & log
    """
    print(string)
    logging.info(string)


def count_scripts(url):
    """
    reads url & counts <script> tags
    """
    try:
        # open a connection to a URL using urllib
        urlOpen = urllib.request.urlopen(url)

        # read HTML
        html = urlOpen.read()

        # close connection
        urlOpen.close()

        # count tags
        num = html.count(b'</script>')
    except (
        urllib.error.URLError,  # failed request
        socket.timeout          # timed out request
    ) as e:
        logging.warning(f'URL failed: {url} (Error: {e})')
        num = np.nan
    return num


def save(df):
    """
    exports results to csv
    """
    print_log(f'Export results to "{EXPORT}"...')
    print_log(f'Check "{LOGFILE}" for more info...')
    df.to_csv(EXPORT, index=False)


def process(df):
    """
    process pandas dataframe per row
    enables program pause & exit
    """
    # total row number
    total = len(df)
    print_log(f'Number of URLs: {total}')

    # iterate dataframe rows as tuples
    for idx, url in df.itertuples():
        try:
            # progress bar
            progress = round((idx + 1) / total * 100, 1)
            printf(f'Progress ({str(progress)}%)', end='\r')

            # count scripts in url
            df.loc[idx, 'num_scripts'] = count_scripts(url)
        except KeyboardInterrupt:
            # resume or exit program
            resume = input('\nRESUME? Y/N ')
            if resume.lower() == 'n':
                # export current results
                # if exit program
                save(df)
                exit()

    # export after finishing processing
    save(df)


if __name__ == "__main__":
    # logging: timestamp, warning level & message
    logging.basicConfig(filename=LOGFILE,  # file name
                        filemode="w",  # overwrite
                        level=logging.DEBUG,  # lowest warning level
                        format="%(asctime)s [%(levelname)s]: %(message)s")  # message format

    # import url file
    print_log(f'Import "{IMPORT}"...')
    try:
        df = pd.read_csv(IMPORT, sep=" ", header=None, low_memory=False)
        df.columns = ['url']
    except Exception as error:
        if type(error) == FileNotFoundError:
            logging.critical('File not found!')
        elif type(error) == AssertionError:
            logging.critical('File is empty!')

    # set request timeout
    timeout = 10
    socket.setdefaulttimeout(timeout)

    # apply function on dataframe
    # to count scripts in HTML
    process(df)


