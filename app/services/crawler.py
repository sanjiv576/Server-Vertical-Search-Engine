# importing necessary modules
import time
from datetime import datetime, timezone
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import undetected_chromedriver as uc
from urllib.robotparser import RobotFileParser


# importing configuration and database collections
from app.core.config import settings
from app.core import raw_pages_publications, raw_pages_profiles


# fetching the content of the robots.txt file


def fetch_robots(base_url, USER_AGENT):
    parsed_url = urlparse(base_url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rfp = RobotFileParser()
    rfp.set_url(robots_url)

    try:
        res = requests.get(robots_url, headers={
                           "User-Agent": USER_AGENT}, timeout=10)
        if res.status_code == 200:
            rfp.parse(res.text.splitlines())
        else:
            rfp = None
    except BaseException as err:
        print(f"Error: {err}")
        rfp = None

    return rfp


def can_fetch(rfp, url, USER_AGENT=settings.USER_AGENT):
    if rfp is None:
        return True
    return rfp.can_fetch(USER_AGENT, url)

#


def setup_driver(current_chrome_version):
    # getting chrome options
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options, version_main=current_chrome_version)
    return driver


def extract_research_output(base_url, driver):
    print(f"\n{'='*20} Publications HTML extraction initialized {'='*20}\n")

    # for all research output data
    extracted_data = []

    # tracking page number since, research ouptut is divided into page 1, 2
    page_number = 0

    while True:
        # making paginated url
        current_url = f"{base_url}publications/?page={page_number}"
        print(f"Fetching: {current_url}")

        driver.get(current_url)

        # waiting for cloudflare on the first page, subsequent pages might load faster
        if page_number == 0:
            time.sleep(20)
        else:
            # waiting shorter for subsequent pages assuming cloudflare is already passed
            time.sleep(10)

        # extracting all HTML content of the page
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # finding all research outputs on the current page
        results = soup.find_all('div', class_='rendering_researchoutput')

        # if no results are found on this page, we have reached the end
        if not results:
            print(f"No more results found. Exiting loop.")
            break

        print(
            f"Found {len(results)} outputs on page {page_number}. Extracting...\n")

        for div in results:
            title = None
            title_link = None

            # extracting title and its link
            h3 = div.find('h3', class_='title')
            if h3:
                a_tag = h3.find('a', class_='link')
                if a_tag:
                    title = a_tag.text.strip()
                    title_link = a_tag.get('href')
                else:
                    # fallback in case there is no link
                    title = h3.text.strip()

            # extracting authors along with link
            authors = []
            if h3:
                # authors are floating between the h3 tag and the date span
                for sibling in h3.next_siblings:
                    # stop looking for authors once we hit the date span
                    if isinstance(sibling, Tag) and sibling.name == 'span':
                        sibling_class = sibling.get('class')
                        if sibling_class and 'date' in sibling_class:
                            break

                    # if the sibling is raw text
                    if isinstance(sibling, NavigableString) and not isinstance(sibling, Tag):
                        # cleaning up the raw text to remove dangling commas and whitespace
                        text = sibling.strip(', & \n\r\t')
                        if text:
                            authors.append({'name': text, 'link': None})

                    # if the sibling is an a tag
                    elif isinstance(sibling, Tag) and sibling.name == 'a':
                        sibling_class = sibling.get('class')
                        if sibling_class and 'person' in sibling_class:
                            authors.append({
                                'name': sibling.text.strip(),
                                'link': sibling.get('href')
                            })

            # extracting publish date
            date_span = div.find('span', class_='date')
            publish_date = date_span.text.strip() if date_span else None

            # extracting journal name
            journal_span = div.find('span', class_='journal')
            journal_name = journal_span.text.strip() if journal_span else None

            # extracting journal volume
            volume_span = div.find('span', class_='volume')
            journal_volume = volume_span.text.strip() if volume_span else None

            # extracting number of pages
            pages_span = div.find('span', class_='numberofpages')
            number_of_pages = pages_span.text.strip() if pages_span else None

            research_output = {
                'title': title,
                'title_link': title_link,
                'authors': authors,
                'publish_date': publish_date,
                'journal_name': journal_name,
                'journal_volume': journal_volume,
                'number_of_pages': number_of_pages
            }

            if research_output['title'] is None:
                continue

            # store each research output as its own document, keyed by title/link
            document_to_store = {
                **research_output,
                'url': title_link if title_link else f"{current_url}#{title}", 'source_page_url': current_url,
                'crawled_at': datetime.now(timezone.utc)
            }

            key = {"title": title}
            if title_link:
                key = {"title_link": title_link}

            raw_pages_publications.update_one(
                key,
                {"$set": document_to_store},
                upsert=True
            )
            extracted_data.append(research_output)

        # adding page number to go to the next page
        page_number += 1

    # saving json file
    output_filename = "all_research_outputs.json"

    print(
        f"\nSuccessfully saved a total of {len(extracted_data)} research outputs to '{output_filename}'!")
    print(f"\n{'='*20} Publications HTML extraction closed {'='*20}\n")

    # returning the extracted output
    return extracted_data


def extract_profiles(base_url, driver):
    print(f"\n{'='*20} Profiles HTML extraction initialized {'='*20}\n")

    # storing all data across all pages here
    extracted_profiles = []

    # starting pagination at page 0
    page_number = 0

    while True:
        # constructing the paginated url
        current_url = f"{base_url}persons/?page={page_number}"
        print(f"Fetching: {current_url}")

        driver.get(current_url)

        # waiting for cloudflare on the first page, subsequent pages might load faster
        if page_number == 0:
            time.sleep(20)
        else:
            # waiting a shorter time for subsequent pages assuming cloudflare is already passed
            time.sleep(10)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        # targeting the main container for each profile card
        results = soup.find_all('div', class_='result-container')

        # breaking the loop if no results are found on this page
        if not results:
            print("No more profiles found. Exiting loop.")
            break

        print(
            f"Found {len(results)} profiles on page {page_number}. Extracting...\n")

        if page_number == 3:
            break

        for div in results:
            # skipping if this container doesn't actually hold a person profile
            if not div.find('div', class_='rendering_person'):
                continue

            # extracting image url
            image_url = None
            img_tag = div.find('img', class_='image')
            if img_tag and img_tag.get('src'):
                image_url = img_tag.get('src')
                # appending the base domain because pureportal often uses relative image paths
                if image_url and isinstance(image_url, str) and image_url.startswith('/'):
                    image_url = f"https://pureportal.coventry.ac.uk{image_url}"

            # extracting name and profile link
            name = None
            profile_link = None
            h3 = div.find('h3', class_='title')
            if h3:
                a_tag = h3.find('a')
                if a_tag:
                    name = a_tag.text.strip()
                    profile_link = a_tag.get('href')
                else:
                    name = h3.text.strip()

            # extracting relations / organisations
            organizations = []
            org_ul = div.find('ul', class_='relations organisations')
            if org_ul:
                # finding all list items within the relations ul
                for li in org_ul.find_all('li'):
                    org_text = li.text.strip()
                    if org_text:
                        organizations.append(org_text)

            # extracting person type (e.g., academic staff)
            type_p = div.find('p', class_='type')
            person_type = type_p.text.strip() if type_p else None

            # extracting active publication years (from the stacked-trend-widget)
            start_year = None
            end_year = None
            years = div.find_all('span', class_='stacked-trend-graph-year')

            if years:
                # assigning the first span as the start year
                start_year = years[0].text.strip()
                # assigning the last span as the end year (if there is more than one year)
                if len(years) > 1:
                    end_year = years[-1].text.strip()
                else:
                    # setting the end year same as start year if only one year is listed
                    end_year = start_year

            # compiling into a dictionary
            profile_data = {
                'name': name,
                'profile_link': profile_link,
                'image_url': image_url,
                'organizations': organizations,
                'person_type': person_type,
                'active_years': {
                    'start': start_year,
                    'end': end_year
                }
            }

            # preparingto store profile data in DB
            document_to_store = {
                **profile_data,
                'url': profile_link if profile_link else f"{current_url}#{name}", 'source_page_url': current_url,
                'crawled_at': datetime.now(timezone.utc)
            }

            profile_key = {"name": name}
            if profile_link:
                profile_key = {"profile_link": profile_link}

            # storing profiles data
            raw_pages_profiles.update_one(
                profile_key,
                {"$set": document_to_store},
                upsert=True
            )

            extracted_profiles.append(profile_data)

        # incrementing page number to go to the next page    #
        page_number += 1

    output_filename = "all_profiles.json"
    print(
        f"\nSuccessfully saved a total of {len(extracted_profiles)} profiles to '{output_filename}'!")
    print(f"\n{'='*20} Profiles HTML extraction closed {'='*20}\n")

    # returning extracted profile data
    return extracted_profiles


def run_background_crawler():
    print(f"\n{'='*20} Crawling initialization {'='*20}\n")

    # checking robots.txt permissions first
    rfp = fetch_robots(settings.SEED_URL, settings.USER_AGENT)
    if not can_fetch(rfp, settings.SEED_URL):
        print(f"Blocked by robots.txt: {settings.SEED_URL}")
        return 0

    print(f"{10*'='} Initializing browser and bypassing Cloudflare {10*'='}")
    driver = setup_driver(settings.CHROME_VERSION)

    crawled_count = 0
    try:
        # navigating to the main seed url (the organisation home page)
        print(f"Fetching seed URL: {settings.SEED_URL}")
        driver.get(settings.SEED_URL)

        # waiting for Cloudflare and dynamic JS to load
        time.sleep(20)

        publications_url = f"{settings.SEED_URL}publications/"
        profiles_url = f"{settings.SEED_URL}persons/"

        # triggering the research output extraction if the link was found
        if publications_url:
            print(f"\n--- Starting Publications Extraction ---")
            # passing the specific publications URL to your extractor
            research_outputs = extract_research_output(
                settings.SEED_URL, driver)
            crawled_count += len(research_outputs)

        # triggering the profiles extraction if the link was found
        if profiles_url:
            print(f"\n--- Starting Profiles Extraction ---")
            # passing the specific profiles URL to your extractor
            profiles = extract_profiles(settings.SEED_URL, driver)
            crawled_count += len(profiles)

    except BaseException as err:
        print(f"Error while crawling: {err}")

    finally:
        # closing the driver safely
        driver.quit()
        print(f"{10*'='} Closed Headless Chrome driver {10*'='}")

    print(f"Crawling completed. {crawled_count} total items extracted.")
    print(f"\n{'='*20} Crawling closed {'='*20}\n")

    # returning total count of processed items
    return crawled_count
