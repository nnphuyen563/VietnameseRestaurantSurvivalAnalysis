DATA_PATH = "./res_hn.csv"
ONLY_IMAGE = False


import undetected_chromedriver as uc

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from tqdm.auto import tqdm
import time, json, os, re

import pandas as pd
from urllib.parse import urlsplit, parse_qs, urlencode

lang_mapping = {
    "stars": {
        "vi": "sao"
    },
    "reviews": {
        "vi": "đánh giá"
    },
    "See more": {
        "vi": "Xem thêm"
    }
}

def get_driver_by_lang(lang = "en"):
    options = uc.ChromeOptions()
    
    options.add_argument(f"--accept-lang={lang}")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')        


    driver = uc.Chrome(
        options = options,
        headless=True,
        version_main = 130
    )

    return driver

def extract_data(driver, restaurant_link, lang = "en", print_title = True):
    
    driver.get(restaurant_link)

    if print_title:
        print(driver.title)

    review_button_xpath = "//button[@role='tab' and @data-tab-index='1']"
    try:
        element_present = EC.presence_of_element_located((By.XPATH, review_button_xpath))
        WebDriverWait(driver, 60).until(element_present)
    except TimeoutException as err:
        return None

    # driver.save_screenshot('results/loaded_page.png')

    aria_label_star = lang_mapping['stars'].get(lang, "stars")
    aria_label_reviews = lang_mapping['reviews'].get(lang, "reviews")
    aria_label_see = lang_mapping['See more'].get(lang, 'See more')

    overall_xpath = f"//div[contains(@class, 'fontBodyMedium') and .//*[contains(@aria-label, '{aria_label_star}')] and .//*[contains(@aria-label, '{aria_label_reviews}')]]"

    try:
        overall_element = driver.find_element(By.XPATH, overall_xpath)
    except:
        aria_label_star = "stars"
        aria_label_reviews = "reviews"
        aria_label_see = "See more"

        overall_xpath = f"//div[contains(@class, 'fontBodyMedium') and .//*[contains(@aria-label, '{aria_label_star}')] and .//*[contains(@aria-label, '{aria_label_reviews}')]]"

    overall_element = driver.find_element(By.XPATH, overall_xpath)

    overall_data = overall_element.find_elements(By.XPATH, './/span[@aria-label]')

    if len(overall_data) == 3:
        overall_stars, total_reviews, price = overall_data
    else:
        overall_stars, total_reviews = overall_data
        price = None

    overall_stars = float(overall_stars.get_attribute('aria-label').split(" ")[0].replace(",", "."))
    total_reviews = int(total_reviews.get_attribute('aria-label').split(" ")[0].replace(",", "").replace(".", ""))

    if price is not None:
        price = price.get_attribute('aria-label').split(" ")[1]

    data = {
        'star': overall_stars,
        'price': price,
        "total_reviews": total_reviews
    }
    
    if total_reviews == 0:
        return None

    review_button = driver.find_element(By.XPATH, review_button_xpath)
    review_button.click()
    time.sleep(1)

    comment_xpath = "//div[@class='MyEned' and @lang and @tabindex='-1']"
    try:
        element_present = EC.presence_of_element_located((By.XPATH, comment_xpath))
        WebDriverWait(driver, 60).until(element_present)
    except TimeoutException as err:
        return None

    # driver.save_screenshot('results/click_review.png')

    review_xpath = "//div[@data-review-id and @aria-label]"
    reviews = driver.find_elements(
        By.XPATH,
        review_xpath
    )

    scrollable = driver.find_element(By.XPATH, "//div[@tabindex='-1' and contains(@jsaction, 'scrollable') and .//div[@role='main']]")
    scrollable = scrollable.find_element(By.XPATH, ".//div[@tabindex='-1' and contains(@jslog, 'mutable')]")

    idx = 0
    force_stop = 0
    old_length = 0
    
    with tqdm(total = total_reviews, desc = "Loading", leave = False) as loading_bar:
        loading_bar.update(len(reviews))
        
        while len(reviews) < total_reviews:
            if force_stop == 5:
                break
            
            idx += 1
            for _ in range(50):
                scrollable.send_keys(Keys.PAGE_DOWN)
            
            reviews = driver.find_elements(
                By.XPATH,
                review_xpath
            )

            loading_bar.update(len(reviews) - old_length)

            if len(reviews) != old_length:
                old_length = len(reviews)
            else:
                force_stop += 1
                
    data['reviews'] = []
    for review in tqdm(reviews, desc = f"Crawling [{lang.upper()}]"):

        date = None
        if ONLY_IMAGE:
            try:
                image_element = review.find_element(By.XPATH, f".//button[@data-photo-index='0']")
                image_element.click()
                time.sleep(3)
            except Exception as e:
                continue

            try:
                date_element = driver.find_element(By.XPATH, "//div[@role='contentinfo']")
                date_text = date_element.text
                date_match = re.search(r'thg (\d+) (\d+)', date_text)
                date = date_match.group(1) + "," + date_match.group(2)
            except:
                continue

        try:
            stars_time_element = review.find_element(By.XPATH, f".//div[./span[contains(@aria-label, '{aria_label_star}')]]")
            stars, timestamp = stars_time_element.find_elements(By.XPATH, './span')
            stars = float(stars.get_attribute('aria-label').split(" ")[0].replace(",", "."))

            if date is None:
                date = timestamp.text
        except:
            continue

        try:
            review_class = review.find_element(By.XPATH, ".//div[@class='MyEned']")
        except:
            continue

        lang = review_class.get_attribute("lang")

        try:
            more_button = review_class.find_element(By.XPATH, f".//button[@aria-label='{aria_label_see}']")
            more_button.click()
        except:
            pass

        comment = review_class.find_element(By.TAG_NAME, "span")
        
        aspects_dicts = {}

        try:
            aspects = review_class.find_elements(By.XPATH, ".//div[@class and contains(@jslog, 'metadata')]")
            for aspect in aspects:
                aspect = aspect.find_elements(By.XPATH, ".//span[text()]")

                if len(aspect) > 1:
                    text = f"<b>{aspect[0].text}:</b> {aspect[1].text}"
                else:
                    text = aspect[0].get_attribute("innerHTML")

                key, value = text.split(":</b>")
                key = key.strip("<b>").strip()
                value = value.strip()
                
                aspects_dicts[key] = value
        except:
            continue

        if len(aspects_dicts) == 0:
            continue

        data['reviews'].append({
            'star': stars,
            'time': date,
            'comment': comment.text,
            'aspects': aspects_dicts,
            'lang': lang
        })


    data["accepted_review"] = len(data['reviews'])
    
    return data

# restaurant_link = "https://www.google.com/maps/place/Lumiere+Byblos+-+Mediterranean+cuisine/@10.801645,106.6548835,1086m/data=!3m1!1e3!4m16!1m9!3m8!1s0x317529f887d2e447:0x3f6190336dadfc9c!2sLumiere+Byblos+-+Mediterranean+cuisine!8m2!3d10.801645!4d106.6548835!9m1!1b1!16s%2Fg%2F11lcj9tqsm!3m5!1s0x317529f887d2e447:0x3f6190336dadfc9c!8m2!3d10.801645!4d106.6548835!16s%2Fg%2F11lcj9tqsm?authuser=0&hl=en&entry=ttu&g_ep=EgoyMDI0MDkyNC4wIKXMDSoASAFQAw%3D%3D"
# restaurant_link = "https://www.google.com/maps/place/Century+Tower/@20.9971719,105.865484,17z/data=!4m16!1m9!3m8!1s0x3135add09c5daa7b:0xb977de42fa0f8ce3!2sCentury+Tower!8m2!3d20.9971669!4d105.8680589!9m1!1b1!16s%2Fg%2F11qndjqm_n!3m5!1s0x3135add09c5daa7b:0xb977de42fa0f8ce3!8m2!3d20.9971669!4d105.8680589!16s%2Fg%2F11qndjqm_n?authuser=0&hl=en&entry=ttu&g_ep=EgoyMDI0MDkzMC4wIKXMDSoASAFQAw%3D%3D"

lang = "vi"
driver = get_driver_by_lang(lang)

links = []
if os.path.exists("data/links.in"):
    with open("data/links.in", "r", encoding="utf8") as f:
        links = f.readlines()

print(len(links))

try:
    data_res = pd.read_csv(DATA_PATH)["link"].tolist()
except:
    data_res = pd.read_csv(DATA_PATH)["url"].tolist()

for idx, restaurant_link in enumerate(data_res):
    if idx < len(links):
        continue
    
    url_parsed = urlsplit(restaurant_link)

    query = url_parsed.query
    query_dict = parse_qs(query)
    query_dict['hl'] = [lang]

    # re-build url to string
    new_query = urlencode(query_dict, doseq=True)
    new_url = url_parsed._replace(query=new_query).geturl()

    try:
        data = extract_data(driver, new_url, lang)
    except Exception as e:
        print(e)

        try:
            driver.quit()
        except:
            pass

        driver = get_driver_by_lang(lang)
        
        data = extract_data(driver, new_url, lang)
        
    if data is None:
        print("DO NOT FOUND ANY REVIEWS")
    else:
        print(f"ACCEPT : {len(data['reviews']): >5} / {data['total_reviews']: >5}")
    
    with open("data/links.in", "a", encoding="utf8") as f:
        f.write(new_url)
        f.write("\n")
    
    with open("data/data.out", "a", encoding="utf8") as f:
        f.write(json.dumps(data, ensure_ascii=False))
        f.write("\n")

    print()

driver.quit()
