from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime

def setup_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    return driver

def extract_next_links(soup, current_link):
    links = soup.find_all('a', href=True)
    next_links = []
    for link in links:
        href = link['href']
        # Check if the href attribute matches the expected pattern for province codes
        if href.startswith(current_link):
            next_links.append(href)
    return(next_links)

def extract_vote_data(soup):
    try:
        # Extracting location information
        breadcrumb_items = soup.find_all('li', class_='breadcrumb-item')
        breadcrumbs = [item.get_text(strip=True) for item in breadcrumb_items]
        print("Location: ", " > ".join(breadcrumbs))
            
        # Extracting total valid votes
        total_valid_votes = int(soup.find(string="JUMLAH SELURUH SUARA SAH").find_next('td').text.replace(',', '').strip())
            
        # Extracting individual candidate votes
        candidate_votes = []
        for row in soup.findAll('table')[1].findAll('tr')[1:]:
            votes = int(row.findAll('td')[-1].text.replace(',', '').strip())
            candidate_votes.append(votes)
            
        sum_votes_candidates = sum(candidate_votes)
        return total_valid_votes, sum_votes_candidates, candidate_votes
    except Exception as e:
        return None, None, None

def fetch_and_parse_page(driver, url):
    driver.get(url)
    time.sleep(1)  # Adjust based on page load time
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def append_to_file(file_path, message):
    with open(file_path, 'a') as file:  # 'a' mode for appending to the file without overwriting existing content
        file.write(message + "\n")

def main():
    driver = setup_selenium_driver()    
    
    # Generate a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = f"file_{timestamp}.txt"  # Example: file_2023-01-28_15-30-25.txt

    # Create a new file with the timestamp in its name and write a message
    with open(file_path, 'w') as file:
        file.write("This file was created at: " + timestamp + "\n")

    # Test Jakarta only
    #provinces = ['/pilpres/hitung-suara/31']
    
    # Iteration
    national = '/pilpres/hitung-suara/'
    soup = fetch_and_parse_page(driver, 'https://pemilu2024.kpu.go.id'+national)
    provinces = extract_next_links(soup, national)
    counter = 0
    for province in provinces:
        soup = fetch_and_parse_page(driver, 'https://pemilu2024.kpu.go.id'+province)
        cities = extract_next_links(soup, province)
        for city in cities:
            soup = fetch_and_parse_page(driver, 'https://pemilu2024.kpu.go.id'+city)
            kecamatans = extract_next_links(soup, city)
            for kecamatan in kecamatans:
                soup = fetch_and_parse_page(driver, 'https://pemilu2024.kpu.go.id'+kecamatan)
                kelurahans = extract_next_links(soup, kecamatan)
                for kelurahan in kelurahans:
                    soup = fetch_and_parse_page(driver, 'https://pemilu2024.kpu.go.id'+kelurahan)
                    tpss = extract_next_links(soup, kelurahan)
                    for tps in tpss:
                        counter = counter + 1
                        print(str(counter)+'/823,236')
                        soup = fetch_and_parse_page(driver, 'https://pemilu2024.kpu.go.id'+tps)
                        try:
                            total_valid_votes, sum_votes_candidates, candidate_votes = extract_vote_data(soup)
                            print(f"01 Anies - Imin: {candidate_votes[0]}")
                            print(f"02 Prabowo - Gibran: {candidate_votes[1]}")
                            print(f"03 Ganjar - Mahfud : {candidate_votes[2]}")
                            print(f"Total: {sum_votes_candidates}")
                            print(f"Suara Sah: {total_valid_votes}")
                            if total_valid_votes == sum_votes_candidates:
                                print("Valid")
                            else:
                                print("Invalid")
                                append_to_file(file_path, 'https://pemilu2024.kpu.go.id'+tps)
                            print()
                        except Exception as e:
                            print("Data in process")
                            print()
    driver.quit()

if __name__ == "__main__":
    main()
