import re
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import tldextract
import joblib
import requests

pd.set_option('display.max_columns', None)
content_model = joblib.load('./models/content_RF_model.pkl')

def content_analysis(url):
    try:
        response_html = requests.get(url)
        response_html.raise_for_status()
        html = response_html.text

        df_content = preprocess_content(html, url)
        prediction = content_model.predict(df_content)
        return prediction
    except Exception as e:
        print("Error:", e)
        return {"error": "Error while analyzing the HTML content"}

def preprocess_content(html, base_url):
    df = pd.DataFrame([{"html": html, "base_url": base_url}])

    df_features = df.apply(lambda row: extract_features(row['html'], row['base_url']), axis=1, result_type='expand') 
    df = pd.concat([df, df_features], axis=1)


    df = df.drop(columns=['html', 'base_url'])
    return df

def extract_features(html, base_url):
    base_domain = get_domain(base_url)

    features = {
        "PctExtHyperlinks": pct_ext_hyperlinks(html, base_domain),
        "PctExtResourceUrls": pct_ext_resource_urls(html, base_domain),
        "ExtFavicon": ext_favicon(html, base_domain),
        "InsecureForms": insecure_forms(html),
        "RelativeFormAction": relative_form_action(html),
        "ExtFormAction": ext_form_action(html, base_domain),
        "AbnormalFormAction": abnormal_form_action(html),
        "PctNullSelfRedirectHyperlinks": pct_null_self_redirect_hyperlinks(html, base_url),
        "FrequentDomainNameMismatch": frequent_domain_name_mismatch(html, base_domain),
        "FakeLinkInStatusBar": fake_link_in_status_bar(html),
        "RightClickDisabled": right_click_disabled(html),
        "PopUpWindow": pop_up_window(html),
        "SubmitInfoToEmail": submit_info_to_email(html),
        "IframeOrFrame": iframe_or_frame(html),
        "MissingTitle": missing_title(html),
        "ImagesOnlyInForm": images_only_in_form(html),
        "PctExtResourceUrlsRT": pct_ext_resource_urls_rt(html, base_domain),
        "AbnormalExtFormActionR": abnormal_ext_form_action_r(html, base_domain),
        "ExtMetaScriptLinkRT": ext_meta_script_link_rt(html, base_domain),
        "PctExtNullSelfRedirectHyperlinksRT": pct_ext_null_self_redirect_hyperlinks_rt(html, base_domain)
    }

    return features

# Helper function to extract the domain from a URL
def get_domain(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

# Function to calculate the percentage of external hyperlinks
def pct_ext_hyperlinks(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    total_links = len(links)
    if total_links == 0:
        return 0.0
    ext_links = [link for link in links if get_domain(link['href']) != base_domain]
    return len(ext_links) / total_links 

# Function to calculate the percentage of external resource URLs
def pct_ext_resource_urls(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    resources = soup.find_all(['img', 'script', 'link'], src=True)
    total_resources = len(resources)
    if total_resources == 0:
        return 0.0
    ext_resources = [res for res in resources if get_domain(res.get('src', res.get('href'))) != base_domain]
    return len(ext_resources) / total_resources 

# Function to check if the favicon is from an external domain
def ext_favicon(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    favicon = soup.find('link', rel='icon')
    if favicon and get_domain(favicon['href']) != base_domain:
        return 1
    return 0

# Function to check if forms are insecure (i.e., not using HTTPS)
def insecure_forms(html):
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form', action=True)
    result = any('https://' not in form['action'] for form in forms)
    return 1 if result else 0

# Function to check if forms use a relative action URL
def relative_form_action(html):
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form', action=True)
    result = any(not urlparse(form['action']).netloc for form in forms)
    return 1 if result else 0

# Function to check if forms use an external action URL
def ext_form_action(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form', action=True)
    result = any(get_domain(form['action']) != base_domain for form in forms)
    return 1 if result else 0

# Function to check for abnormal form action attributes
def abnormal_form_action(html):
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form', action=True)
    abnormal_values = ["#", "about:blank", "", "javascript:true"]
    result = any(form['action'] in abnormal_values for form in forms)
    return 1 if result else 0

# Function to calculate the percentage of null/self-redirecting hyperlinks
def pct_null_self_redirect_hyperlinks(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    total_links = len(links)
    if total_links == 0:
        return 0.0
    null_self_links = [link for link in links if link['href'] in ["", "#", base_url] or "file://" in link['href']]
    return len(null_self_links) / total_links 

# Function to check for frequent domain name mismatch
def frequent_domain_name_mismatch(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    domain_count = {}
    for link in links:
        domain = get_domain(link['href'])
        domain_count[domain] = domain_count.get(domain, 0) + 1
    most_frequent_domain = max(domain_count, key=domain_count.get)
    return 1 if most_frequent_domain != base_domain else 0

# Function to check if a fake link is displayed in the status bar
def fake_link_in_status_bar(html):
    return 1 if "onMouseOver" in html and "window.status" in html else 0

# Function to check if right-click is disabled
def right_click_disabled(html):
    return 1 if "document.oncontextmenu" in html or "return false;" in html else 0

# Function to check if pop-up windows are triggered
def pop_up_window(html):
    return 1 if "window.open" in html else 0

# Function to check if the HTML submits information to an email
def submit_info_to_email(html):
    return 1 if "mailto:" in html else 0

# Function to check if iframes or frames are used
def iframe_or_frame(html):
    soup = BeautifulSoup(html, 'html.parser')
    return 1 if soup.find('iframe') or soup.find('frame') else 0

# Function to check if the title tag is missing
def missing_title(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('title')
    return 1 if not title or not title.string.strip() else 0

# Function to check if forms only contain images
def images_only_in_form(html):
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form')
    for form in forms:
        if all(tag.name == 'img' for tag in form.find_all()):
            return 1
    return 0


def pct_ext_resource_urls_rt(html, base_domain):
    pct_ext_resource = pct_ext_resource_urls(html, base_domain)
    if pct_ext_resource < 0.2:
        return -1  # Legit
    elif 0.2 <= pct_ext_resource <= 0.5:
        return 0  # Suspicious
    else:
        return 1  # Unsafe


# Check if the form action attribute contains a foreign domain 'about:blank', or an empty string
def abnormal_ext_form_action_r(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    forms = soup.find_all('form', action=True)
    abnormal_count = 0
    total_forms = len(forms)
    if total_forms == 0:
        return -1  # Legit as there are no forms

    for form in forms:
        action = form['action']
        if get_domain(action) != base_domain or action in ["about:blank", ""]:
            abnormal_count += 1

    pct_abnormal_forms = abnormal_count / total_forms * 100
    if pct_abnormal_forms < 20:
        return -1  # Legit
    elif 20 <= pct_abnormal_forms <= 50:
        return 0  # Suspicious
    else:
        return 1  # Unsafe


# Counts the percentage of meta, script and link tags containing external URLs in the attributes
def ext_meta_script_link_rt(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    meta_tags = soup.find_all('meta', content=True)
    script_tags = soup.find_all('script', src=True)
    link_tags = soup.find_all('link', href=True)

    total_tags = len(meta_tags) + len(script_tags) + len(link_tags)
    if total_tags == 0:
        return -1  # Legit as there are no tags to evaluate

    ext_tags = [
        tag for tag in (meta_tags + script_tags + link_tags)
        if get_domain(tag.get('src', tag.get('href', tag.get('content')))) != base_domain
    ]

    pct_ext_tags = len(ext_tags) / total_tags * 100
    if pct_ext_tags < 20:
        return -1  # Legit
    elif 20 <= pct_ext_tags <= 50:
        return 0  # Suspicious
    else:
        return 1  # Unsafe


def pct_ext_null_self_redirect_hyperlinks_rt(html, base_domain):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    total_links = len(links)
    if total_links == 0:
        return -1  # Legit as there are no links to evaluate

    abnormal_links = [
        link for link in links
        if link['href'].startswith("#") or "javascript:void(0)" in link['href'] or get_domain(link['href']) != base_domain
    ]

    pct_abnormal_links = len(abnormal_links) / total_links * 100
    if pct_abnormal_links < 20:
        return -1  # Legit
    elif 20 <= pct_abnormal_links <= 50:
        return 0  # Suspicious
    else:
        return 1  # Unsafe
