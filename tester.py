import asyncio
import json
from logger import log
from sheet import Sheet
from config import RANGES, SOURCE_RANGES
from original import fill_original
from mangalib import load_url
from session import main
from helper_funcs import connect_to_browser


def test_mangalib():
    with connect_to_browser() as driver:
        print([load_url(driver, url) for url in Sheet().get_values('TestData!C1:C100')[0]], sep='\n')

def test_original():
    print(asyncio.run(fill_original(Sheet().get_values('TestData!A1:A100')[0])), sep='\n')


if __name__ == '__main__':
    test_mangalib()
    test_original()
