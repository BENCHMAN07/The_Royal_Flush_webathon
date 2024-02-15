from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import spacy

app = Flask(__name__)

# Load English language model for spaCy
nlp = spacy.load("en_core_web_sm")

# Function to fetch HTML content from a URL
def fetch_html_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.RequestException:
        return None

# Function to calculate NLP-based score and missing words for a given text
def calculate_nlp_score_and_missing_words(text, reference_text):
    doc = nlp(text)
    reference_doc = nlp(reference_text)
    
    # Calculate the number of tokens in the document
    num_tokens = len(doc)
    
    # Get missing words (excluding stop words)
    missing_words = [token.text for token in reference_doc if token.text not in doc.text and not token.is_stop]
    
    # Calculate the score based on the ratio of non-stop words to total words
    if num_tokens == 0:
        score = 0
    else:
        num_stop_words = sum(1 for token in doc if token.is_stop)
        score = (num_tokens - num_stop_words) / num_tokens * 10
        score = min(10, score)
    
    return round(score, 2), missing_words

# Route to render the form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission and fetch details
@app.route('/fetch_details', methods=['POST'])
def fetch_details():
    # Get URL from the form data
    url = request.form['url']
    
    # Fetch HTML content from the URL
    html_content = fetch_html_content(url)
    
    if html_content:
        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract meta title, meta keywords, and meta description
        meta_title = soup.title.text.strip()
        meta_keywords = soup.find('meta', {'name': 'keywords'})
        meta_keywords = meta_keywords['content'].strip() if meta_keywords else ""
        meta_description = soup.find('meta', {'name': 'description'})
        meta_description = meta_description['content'].strip() if meta_description else ""
        
        # Extract page content
        paragraphs = [p.text.strip() for p in soup.find_all('p')]
        
        # Calculate missing words for URL compared to meta title
        url_score, url_missing_words = calculate_nlp_score_and_missing_words(url, meta_title)
        meta_title_score, meta_title_missing_words = calculate_nlp_score_and_missing_words(meta_title, url)
        meta_keywords_score, meta_keywords_missing_words = calculate_nlp_score_and_missing_words(meta_keywords, meta_title)
        meta_description_score, meta_description_missing_words = calculate_nlp_score_and_missing_words(meta_description, meta_keywords)
        page_content_score, page_content_missing_words = calculate_nlp_score_and_missing_words("\n".join(paragraphs), meta_description)
        
        # Overall score
        overall_score = (url_score + meta_title_score + meta_keywords_score + meta_description_score + page_content_score) / 5 * 10
        overall_score = round(overall_score, 2)
        
        # Construct details dictionary
        details = {
            'url': url,
            'meta_title': meta_title,
            'meta_keywords': meta_keywords,
            'meta_description': meta_description,
            'page_content': paragraphs,
            'scores': {
                'url_score': url_score,
                'meta_title_score': meta_title_score,
                'meta_keywords_score': meta_keywords_score,
                'meta_description_score': meta_description_score,
                'page_content_score': page_content_score,
                'overall_score': f"{overall_score}%"
            },
            'missing_words': {
                'url_missing_words': url_missing_words,
                'meta_title_missing_words': meta_title_missing_words,
                'meta_keywords_missing_words': meta_keywords_missing_words,
                'meta_description_missing_words': meta_description_missing_words,
                'page_content_missing_words': page_content_missing_words
            }
        }
        
        return render_template('details.html', details=details)
    else:
        return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
