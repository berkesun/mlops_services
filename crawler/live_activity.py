from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from decouple import config
import time as _time
from django.db import transaction

from db_models.models import LiveActivity


def crawl_live_activity():
    url = config('live_activity_url')
    df = pd.DataFrame(columns=["event_title", "upper_category", "lower_category", "date", "start_time", "location"])
    driver = webdriver.Chrome()
    driver.get(url)
    _time.sleep(4)


    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    event_links = soup.find_all("a", class_="ln1 searchResultEventName")

    for event_link in event_links[1:3]:
        event_url = "https://www.biletix.com" + event_link['href']  # Etkinlik bağlantısını tam URL olarak al
        driver.get(event_url)  # Etkinlik sayfasına git
        event_page_source = driver.page_source  # Etkinlik sayfasının kaynağını al
        event_soup = BeautifulSoup(event_page_source, "html.parser")

        event_title_element = event_soup.find("h1", class_="btx-title")
        if not event_title_element:
            # Etkinlik başlığı alınamadı, bu etkinliği atla
            continue

        event_title = event_title_element.get_text()
        location_span = event_soup.find_all('span', class_='ng-star-inserted')[-2].get_text()
        category_links = event_soup.find_all("a", class_="breadcrumb-link")
        category_texts = [link.get_text() for link in category_links]
        date_spans = event_soup.find_all('span', style="margin-right: 8px;")
        date_span = [da.get_text() for da in date_spans]
        if len(date_span) == 0:
            continue

        date = date_span[0]
        time = date_span[1]

        df = df.append({"event_title": event_title,
                        "upper_category": category_texts[0],
                        "lower_category": category_texts[1],
                        "date": date,
                        "start_time": time,
                        "location": location_span},
                       ignore_index=True)
        driver.back()
    driver.quit()
    combined_values = df["event_title"] + df["upper_category"] + df["lower_category"] + df["date"]
    duplicates = combined_values.duplicated()
    df = df[~duplicates]
    df["date"].replace('', pd.NA, inplace=True)
    df = df.dropna(subset=["date"])
    turkish_months = {
        'Oca': 'Jan', 'Şub': 'Feb', 'Mar': 'Mar', 'Nis': 'Apr', 'May': 'May', 'Haz': 'Jun',
        'Tem': 'Jul', 'Ağu': 'Aug', 'Eyl': 'Sep', 'Eki': 'Oct', 'Kas': 'Nov', 'Ara': 'Dec'
    }

    df["date"] = df["date"].apply(
        lambda x: " ".join(turkish_months[month] if month in turkish_months else month for month in x.split()))
    df["date"] = pd.to_datetime(df["date"], format="%d %b %Y")

    with transaction.atomic():
        for index, row in df.iterrows():
            liveadb, created = LiveActivity.objects.update_or_create(
                event_title = row["event_title"],
                upper_category = row["upper_category"],
                lower_category = row["lower_category"],
                date=row['date'],
                defaults={
                    'start_time': row['start_time'],
                    'location': row['location']
                }
            )
            liveadb.save()
