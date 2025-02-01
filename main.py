from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
opt=webdriver.ChromeOptions()
opt.add_argument("--disable-popup-blocking")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=opt)
if not os.path.exists('./csvs'):
    os.mkdir('./csvs')

if not os.path.exists('./logs'):
    os.mkdir('./logs')

DIR = './csvs/' + FOLDER_NAME

if not os.path.exists(DIR):
    os.mkdir(DIR)

processed = []
if os.path.exists('./logs/processed.txt'):
    with open('./logs/processed.txt', 'r') as f:
        processed = f.read()
        processed = processed.split('\n')
        processed = [x.strip() for x in processed if x.strip() != '']

