import requests
from bs4 import BeautifulSoup
import json
import regex as re

url = 'https://www.bajajfinserv.in/investments/mutual-funds'
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

# Define regex patterns for different product features
patterns = {
    "Term Loan": r"Term Loan",
    "Flexi Hybrid": r"Flexi Hybrid",
    "Interest as EMI": r"Interest as EMI",
    "Personal Loan eligibility and documents": r"Personal Loan eligibility and documents",
    "Loan up to Rs\. %\$\$PL-Loan-Amount\$\$%": r"Loan up to Rs\. %\$\$PL-Loan-Amount\$\$%",
    "Personal Loan amount": r"Personal Loan amount",
    "Flexi Term loan": r"Flexi Term loan",
    "Instant approval": r"Instant approval",
    "Money in bank in 24 hours": r"Money in bank in 24 hours",
    "Loan tenure": r"Loan tenure",
    "Personal Loan online": r"Personal Loan online",
    "Minimal paperwork": r"Minimal paperwork",
    "No collateral": r"No collateral",
    "No hidden charges": r"No hidden charges",
    "instant loans": r"instant loans",
    "customer type": r"customer type",
    "Intrest amount freequency": r"Intrest amount freequency",
    "SDP": r"SDP",
    "customer below 60": r"customer below 60",
    "Gold loan": r"Gold loan",
    "EMI": r"EMI",
    "technology": r"technology",
    "insurance": r"insurance",
    "payments": r"payments",
}

# Initialize an empty dictionary to store extracted information
extracted_info = {}

# Apply regex patterns and extract information
for key, pattern in patterns.items():
    match = re.search(pattern, html_content, flags=re.IGNORECASE)
    extracted_info[key] = bool(match)

# Include URL, meta title, and meta keywords in the extracted information
extracted_info['url'] = url
extracted_info['meta_title'] = soup.title.text
extracted_info['meta_keywords'] = soup.find('meta', {'name': 'keywords'}).get('content', '')

# Filter out null values
filtered_info = {k: v for k, v in extracted_info.items() if v is not None}

# Convert the extracted information to a JSON object
json_output = json.dumps(filtered_info, indent=4)

# Print the JSON object
print(json_output)
