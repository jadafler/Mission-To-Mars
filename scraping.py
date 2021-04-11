# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemisphere":hemisphere(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def hemisphere(browser):

    # Visit the weather website
    url = 'https://mars.nasa.gov/insight/weather/'
    browser.visit(url)

    # Parse the data
    html = browser.html
    weather_soup = soup(html, 'html.parser')

    # Scrape the Daily Weather Report table
    weather_table = weather_soup.find('table', class_='mb_table')
    print(weather_table.prettify())

    # # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles

    # ### Hemispheres

    # 1. Use browser to visit the URL
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemi_soup = soup(html, 'html.parser')

    hemi_title = hemi_soup.find_all("h3")
    hemi_titles = []
    rel_urls = []
    for title in hemi_title:
        hemi_title = title.text
        hemi_titles.append(hemi_title)
        for title in hemi_titles:
            browser.visit(url)
            html = browser.html
            hemi_soup = soup(html, 'html.parser')

            link_element = browser.links.find_by_partial_text(title)
            link_element.click()

            hypertext = browser.html
            img_soup = soup(hypertext, 'html.parser')

            rel_url = img_soup.select_one("img.wide-image").get('src')
            if rel_url not in rel_urls:
                rel_urls.append(rel_url)

    for url in rel_urls:
        full_img_url = f'https://astrogeology.usgs.gov{url}'
        hemisphere_image_urls.append(full_img_url)

    hemi_zip = zip(hemisphere_image_urls, hemi_titles)
    hemi_list = []
    for img_url, title in hemi_zip:
        hemispheres = {}

        hemispheres['img_url'] = img_url

        hemispheres['title'] = title

        hemi_list.append(hemispheres)

    # 4. Print the list that holds the dictionary of each image url and title.
    return hemi_list

if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())