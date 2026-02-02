import requests
from lxml import html

def parse_groq_stream(stream):
    for chunk in stream:
        if chunk.choices:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

def al_bayan(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        title_element = tree.xpath('//h1')
        title_text = title_element[0].text_content().strip() if title_element else "Title not found"

        date_element = tree.xpath('//time[@class="post-time"]')
        date_text = date_element[0].text_content().strip() if date_element else "Date not found"

        paragraph_divs = tree.xpath('//p[@class="article-text"]')
        content = "\n".join([p.text_content().strip() for p in paragraph_divs]) if paragraph_divs else "Content not found"

        return {
            "title": title_text,
            "date": date_text,
            "content": content
        }

    except requests.RequestException as e:
        return {"error": f"Failed to fetch the URL: {e}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def aletihad(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        title_element = tree.xpath('//h1')
        title_text = title_element[0].text_content().strip() if title_element else "Title not found"

        date_element = tree.xpath('//div[@class="art-date"]')
        date_text = date_element[0].text_content().strip() if date_element else "Date not found"

        paragraph_divs = tree.xpath('//p[@style="text-align: justify;"]')
        content = "\n".join([p.text_content().strip() for p in paragraph_divs]) if paragraph_divs else "Content not found"

        return {"title": title_text, "date": date_text, "content": content}

    except requests.RequestException as e:
        return {"error": f"Failed to fetch the URL: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def gulf_news(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        title_element = tree.xpath('//h1')
        title_text = title_element[0].text_content().strip() if title_element else "Title not found"

        date_element = tree.xpath('//time[@class="publish"]')
        date_text = date_element[0].text_content().strip() if date_element else "Date not found"

        paragraph_divs = tree.xpath('//div[@class="article-body"]')
        content = "\n".join([p.text_content().strip() for p in paragraph_divs]) if paragraph_divs else "Content not found"

        return {
            "title": title_text,
            "date": date_text,
            "content": content
        }

    except requests.RequestException as e:
        return {"error": f"Failed to fetch the URL: {e}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def emarat_alyoum(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        title_element = tree.xpath('//h1')
        title_text = title_element[0].text_content().strip() if title_element else "Title not found"

        date_element = tree.xpath('//time[@class="date"]')
        date_text = date_element[0].text_content().strip() if date_element else "Date not found"

        paragraph_divs = tree.xpath('//div[@class="col"]')
        content = "\n".join([p.text_content().strip() for p in paragraph_divs]) if paragraph_divs else "Content not found"

        return {
            "title": title_text,
            "date": date_text,
            "content": content
        }

    except requests.RequestException as e:
        return {"error": f"Failed to fetch the URL: {e}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def cnn_arabic(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        title_element = tree.xpath('//h1')
        title_text = title_element[0].text_content().strip() if title_element else "Title not found"

        date_element = tree.xpath('//time')
        date_text = date_element[0].attrib.get('datetime') if date_element else "Date not found"

        paragraph_divs = tree.xpath('//div[@id="body-text"]')
        content = "\n".join([p.text_content().strip() for p in paragraph_divs]) if paragraph_divs else "Content not found"

        return {
            "title": title_text,
            "date": date_text,
            "content": content
        }

    except requests.RequestException as e:
        return {"error": f"Failed to fetch the URL: {e}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def masaader(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        tree = html.fromstring(response.content)

        title_element = tree.xpath('//h1')
        title_text = title_element[0].text_content().strip() if title_element else "Title not found"

        date_element = tree.xpath('//abbr[@class="date published"]')
        date_text = date_element[0].text_content().strip() if date_element else "Date not found"

        paragraph_divs = tree.xpath('//div[@class="entry-content clearfix"]')
        content = "\n".join([p.text_content().strip() for p in paragraph_divs]) if paragraph_divs else "Content not found"

        return {
            "title": title_text,
            "date": date_text,
            "content": content
        }

    except requests.RequestException as e:
        return {"error": f"Failed to fetch the URL: {e}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def site_selector(url):
    if "www.aletihad.ae" in url:
        return aletihad(url)
    elif "gulfnews.com" in url:
        return gulf_news(url)
    elif "www.emaratalyoum.com" in url:
        return emarat_alyoum(url)
    elif "arabic.cnn.com" in url:
        return cnn_arabic(url)
    elif "masaadernews.com" in url:
        return masaader(url)
    else:
        return {"error": "Unsupported URL"}