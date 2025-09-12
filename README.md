# Flashfood API Scraper

This project is a command-line tool for scraping data from the Flashfood app's API. It is designed to fetch and display items available at specific stores, using custom headers and API keys to mimic the official app's requests.

## Features
- Scrapes item and store data from the Flashfood API
- Uses custom headers and tokens to bypass app security
- Command-line interface for quick access to data
- JSON storage for persistent data

## Technical Approach
To build this tool, I used MITM proxying to analyze the Flashfood app's network traffic and reverse-engineered their API system. By studying the authentication and token generation process, I was able to recreate the necessary headers and tokens to bypass security and generate the same results as the official app.

## Future Plans
I am actively working on improving this project to create a more robust system and a graphical user interface (GUI). The current version is command-line only, but future updates will include a user-friendly GUI and additional features for better usability.

## Usage
1. Install the required dependencies:
   ```bash
   pip install requests
   ```
2. Run the script:
   ```bash
   python flashfoodhacks.py
   ```
   or
   ```bash
   python flashfoodtesting.py
   ```

## Disclaimer
This project is for educational purposes only. Use responsibly and respect the terms of service of Flashfood.

---

*Continuing development: Stay tuned for a better system and GUI!*
