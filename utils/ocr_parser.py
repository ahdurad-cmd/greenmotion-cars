"""
OCR-based parser for car advertisements from mobile.de, Blocket, etc.
Extracts structured data from advertisement images/screenshots and PDF files.
"""
import re
from PIL import Image
try:
    import pytesseract
except ImportError:
    pytesseract = None
from typing import Dict, Any, Optional
import os
import requests
from bs4 import BeautifulSoup

class AdParser:
    """Parse car advertisement images and extract structured data"""
    
    # Approximate distances from major cities to Aalborg (km)
    CITY_DISTANCES = {
        # German cities
        'BERLIN': 680, 'MÜNCHEN': 1250, 'HAMBURG': 450, 'KÖLN': 750, 'FRANKFURT': 850,
        'STUTTGART': 1050, 'DÜSSELDORF': 730, 'DORTMUND': 700, 'ESSEN': 720, 'LEIPZIG': 650,
        'BREMEN': 420, 'DRESDEN': 720, 'HANNOVER': 550, 'NÜRNBERG': 970, 'DUISBURG': 730,
        'BOCHUM': 700, 'WUPPERTAL': 740, 'BIELEFELD': 620, 'BONN': 760, 'MÜNSTER': 630,
        'MANNHEIM': 950, 'AUGSBURG': 1200, 'WIESBADEN': 860, 'MÖNCHENGLADBACH': 740,
        'KARLSRUHE': 990, 'AACHEN': 800, 'KIEL': 280, 'FLENSBURG': 180,
        'SIEGEN': 873, 'KASSEL': 660, 'ERFURT': 720, 'HALLE': 680, 'MAGDEBURG': 620,
        'BRAUNSCHWEIG': 600, 'CHEMNITZ': 740, 'LÜBECK': 350, 'ROSTOCK': 480, 'POTSDAM': 690,
        'OLDENBURG': 400, 'OSNABRÜCK': 560, 'REGENSBURG': 1080, 'WÜRZBURG': 900, 'INGOLSTADT': 1150,
        'ULM': 1150,
        # Swedish cities
        'STOCKHOLM': 1100, 'GÖTEBORG': 330, 'MALMÖ': 470, 'UPPSALA': 1050, 'VÄSTERÅS': 1000,
        'ÖREBRO': 900, 'LINKÖPING': 950, 'HELSINGBORG': 460, 'JÖNKÖPING': 700, 'NORRKÖPING': 950,
        'LUND': 480, 'UMEÅ': 1800, 'GÄVLE': 1200, 'BORÅS': 400, 'SÖDERTÄLJE': 1100,
        'ESKILSTUNA': 1000, 'KARLSTAD': 800, 'SUNDSVALL': 1450, 'HALMSTAD': 400, 'VÄXJÖ': 550
    }
    
    # Diesel consumption and price (average for transport vehicles)
    DIESEL_CONSUMPTION_PER_100KM = 12.0  # liters per 100 km
    DIESEL_PRICE_DKK = 13.50  # DKK per liter (approximate)
    
    # Common patterns for extracting information
    VIN_PATTERN = re.compile(r'\b[A-HJ-NPR-Z0-9]{17}\b', re.IGNORECASE)
    PRICE_PATTERN = re.compile(r'([\d\s\.\,]+)\s*((?:DKK|EUR|SEK|€|kr))(?=\s|\n|$)', re.IGNORECASE)
    PRICE_PATTERN_AFTER = re.compile(r'(?:Pris|Price|Preis)[:\s\n]*([\d\s\.\,]+)\s*((?:DKK|EUR|SEK|€|kr))', re.IGNORECASE)
    YEAR_PATTERN = re.compile(r'\b(19\d{2}|20[0-2]\d)\b')
    MILEAGE_PATTERN = re.compile(r'([\d\.\,]+)\s*(?:km|kilometer)', re.IGNORECASE)
    POWER_PATTERN = re.compile(r'([\d]+)\s*(?:hk|hp|ps|kw)', re.IGNORECASE)
    REGISTRATION_PATTERN = re.compile(r'(?:Reg|Registration|Första reg|Erstzulassung|Første indregistrering)[:\s]*([\d]{1,2}[\/\-\.][\d]{1,2}[\/\-\.][\d]{2,4})', re.IGNORECASE)
    COLOR_PATTERN = re.compile(r'(?:Farve|Färg|Color|Colour|Farbe)[:\s]*([A-Za-zæøåÆØÅäöüÄÖÜß\s]+?)(?:\n|,|$)', re.IGNORECASE)
    DOORS_PATTERN = re.compile(r'([\d])\s*(?:døre|dörrar|doors|türen)', re.IGNORECASE)
    SEATS_PATTERN = re.compile(r'([\d])\s*(?:sæde|säten|seats|sitzplätze)', re.IGNORECASE)
    ENGINE_SIZE_PATTERN = re.compile(r'([\d]+[,\.]?[\d]*)\s*(?:L|liter)', re.IGNORECASE)
    
    # Dealer/Seller patterns
    MOBILE_DE_PATTERN = re.compile(r'(?:Händler|Dealer|Forhandler)[:\s]*([A-ZÄÖÜ][A-Za-zäöüÄÖÜß\s&\.\-]+?)(?:\n|Standort|Location|$)', re.IGNORECASE)
    BLOCKET_SELLER_PATTERN = re.compile(r'(?:Säljare|Säljer)[:\s]*([A-ZÄÖÜ][A-Za-zäöüÄÖÜß\s&\.\-]+?)(?:\n|Ort|Location|$)', re.IGNORECASE)
    # Updated to handle postal codes like "DE-57074 Siegen" or "12345 Berlin"
    LOCATION_PATTERN = re.compile(r'(?:Standort|Ort|Placering)[:\s]*(?:[A-Z]{2}-)?(?:\d{4,5}\s+)?([A-ZÄÖÜ][A-Za-zäöüÄÖÜß\s\-]+?)(?:\n|,|$)', re.IGNORECASE)
    PHONE_PATTERN = re.compile(r'(?:\+[\d]{1,3}[\s]?)?[\(]?[\d]{2,4}[\)]?[\s\-]?[\d]{3,4}[\s\-]?[\d]{2,4}', re.IGNORECASE)
    
    # Country detection patterns
    GERMAN_CITIES = ['BERLIN', 'MÜNCHEN', 'HAMBURG', 'KÖLN', 'FRANKFURT', 'STUTTGART', 'DÜSSELDORF', 
                     'DORTMUND', 'ESSEN', 'LEIPZIG', 'BREMEN', 'DRESDEN', 'HANNOVER', 'NÜRNBERG',
                     'DUISBURG', 'BOCHUM', 'WUPPERTAL', 'BIELEFELD', 'BONN', 'MÜNSTER', 'MANNHEIM',
                     'AUGSBURG', 'WIESBADEN', 'MÖNCHENGLADBACH', 'KARLSRUHE', 'AACHEN', 'KIEL',
                     'SIEGEN', 'KASSEL', 'ERFURT', 'HALLE', 'MAGDEBURG', 'BRAUNSCHWEIG', 'CHEMNITZ',
                     'LÜBECK', 'ROSTOCK', 'POTSDAM', 'OLDENBURG', 'OSNABRÜCK', 'REGENSBURG', 
                     'WÜRZBURG', 'INGOLSTADT', 'FREIBURG', 'ULM', 'HEILBRONN', 'WOLFSBURG']
    
    SWEDISH_CITIES = ['STOCKHOLM', 'GÖTEBORG', 'MALMÖ', 'UPPSALA', 'VÄSTERÅS', 'ÖREBRO', 'LINKÖPING',
                      'HELSINGBORG', 'JÖNKÖPING', 'NORRKÖPING', 'LUND', 'UMEÅ', 'GÄVLE', 'BORÅS',
                      'SÖDERTÄLJE', 'ESKILSTUNA', 'KARLSTAD', 'SUNDSVALL', 'HALMSTAD', 'VÄXJÖ',
                      'VIMMERBY', 'KALMAR', 'KRISTIANSTAD', 'TROLLHÄTTAN', 'LIDKÖPING', 'SKÖVDE']
    
    # Equipment patterns
    EQUIPMENT_KEYWORDS = [
        'Navigation', 'Navi', 'GPS', 'Klimaanlæg', 'Klimaanlage', 'AC', 'Air Condition',
        'Læder', 'Leder', 'Leather', 'Alcantara', 'Xenon', 'LED', 'Panorama',
        'Cruise Control', 'Fartpilot', 'Tempomat', 'Parking', 'Park', 'Sensor',
        'Camera', 'Kamera', 'Bluetooth', 'DAB', 'Sound', 'Harman', 'Bose', 'Bang & Olufsen',
        'Sædevarme', 'Sitzheizung', 'Heated Seats', 'Keyless', 'Start/Stop',
        'Trailer', 'Anhænger', 'Anhängerkupplung', 'Tow', 'Adaptiv', 'ACC'
    ]
    
    # Common car makes to look for
    CAR_MAKES = [
        'Mercedes-Benz', 'Mercedes', 'BMW', 'Audi', 'Volkswagen', 'VW', 'Volvo', 'Toyota', 
        'Honda', 'Ford', 'Opel', 'Peugeot', 'Renault', 'Citroën', 'Skoda',
        'Seat', 'Nissan', 'Mazda', 'Hyundai', 'Kia', 'Porsche', 'Tesla',
        'Lexus', 'Jaguar', 'Land Rover', 'Range Rover', 'Mini', 'Fiat', 'Alfa Romeo',
        'Dacia', 'Suzuki', 'Subaru', 'Mitsubishi', 'Jeep', 'Chevrolet', 'Cadillac'
    ]
    
    @staticmethod
    def parse_image(image_path: str) -> Dict[str, Any]:
        """
        Parse an advertisement image and extract car information
        
        Args:
            image_path: Path to the advertisement image file
            
        Returns:
            Dictionary with extracted fields (vin, make, model, year, price, mileage, etc.)
        """
        try:
            if pytesseract is None:
                return {'error': 'OCR not available - pytesseract not installed'}
            
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image, lang='eng+dan+deu+swe')
            
            # Parse extracted text
            data = AdParser._parse_text(text)
            
            return data
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def parse_pdf(pdf_path: str) -> Dict[str, Any]:
        """
        Parse a PDF advertisement and extract car information
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extracted fields
        """
        try:
            try:
                from pdf2image import convert_from_path
            except ImportError:
                convert_from_path = None
            import PyPDF2
            
            combined_text = ""
            
            # First try to extract text directly from PDF (if it's not scanned)
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            combined_text += page_text + "\n"
            except:
                pass
            
            # If no text or very little text, use OCR on images
            if len(combined_text.strip()) < 50:
                if convert_from_path is None or pytesseract is None:
                    return {'error': 'PDF OCR not available - dependencies not installed'}
                # Convert PDF pages to images
                images = convert_from_path(pdf_path, dpi=300, first_page=1, last_page=3)
                
                # Extract text from each page
                for i, image in enumerate(images):
                    text = pytesseract.image_to_string(image, lang='eng+dan+deu+swe')
                    combined_text += text + "\n"
            
            # Parse the combined text
            data = AdParser._parse_text(combined_text)
            
            return data
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def parse_url(url: str) -> Dict[str, Any]:
        """
        Parse an advertisement URL and extract car information
        
        Args:
            url: URL of the advertisement
            
        Returns:
            Dictionary with extracted fields
        """
        try:
            # Mobile.de has very strong bot protection - try requests with special headers first
            if 'mobile.de' in url:
                print(f"[INFO] Detected mobile.de - trying with optimized headers...")
                
                # Try multiple strategies for mobile.de
                session = requests.Session()
                
                # Strategy 1: Desktop Chrome with German locale
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'de-DE,de;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
                
                try:
                    response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
                    
                    # Check if we got blocked
                    if response.status_code == 403 or 'Zugriff verweigert' in response.text or 'Access denied' in response.text:
                        # Mobile.de has blocked us - return helpful error
                        return {
                            'error': 'Mobile.de blokerer automatisk adgang',
                            'blocked': True,
                            'ad_url': url,
                            'help_text': 'Mobile.de har stærk bot-beskyttelse. Alternativer:\n1. Kopier bilens data manuelt og indsæt i "Noter" feltet\n2. Tag et screenshot af annoncen og upload det (OCR)\n3. Brug en anden tysk bilsite (autoscout24.de fungerer måske bedre)'
                        }
                    
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style", "noscript"]):
                        script.decompose()
                    
                    # Get text
                    text = soup.get_text(separator='\n')
                    
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    # Check if we actually got car data
                    if len(text) < 500 or 'Zugriff' in text:
                        return {
                            'error': 'Mobile.de blokerer automatisk adgang',
                            'blocked': True,
                            'ad_url': url,
                            'help_text': 'Brug alternativ metode: kopier data manuelt eller upload screenshot'
                        }
                    
                    # Parse the text
                    data = AdParser._parse_text(text)
                    data['ad_url'] = url
                    
                    return data
                    
                except Exception as e:
                    return {
                        'error': f'Kunne ikke hente data fra mobile.de: {str(e)}',
                        'blocked': True,
                        'ad_url': url,
                        'help_text': 'Prøv at kopiere bilens data manuelt fra mobile.de'
                    }
            
            # For Blocket, use Selenium directly (JavaScript rendering)
            elif 'blocket.se' in url:
                print(f"[INFO] Detected Blocket.se - using Selenium...")
                return AdParser._parse_url_with_selenium(url)
            
            # Try with requests first (faster) for other sites
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'da,en-US;q=0.9,en;q=0.8,de;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=15, allow_redirects=True)
            
            # If blocked, try with Selenium
            if response.status_code == 403:
                return AdParser._parse_url_with_selenium(url)
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Parse the text
            data = AdParser._parse_text(text)
            data['ad_url'] = url
            
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                # Try with Selenium as fallback
                return AdParser._parse_url_with_selenium(url)
            return {'error': f'HTTP fejl: {str(e)}'}
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def _parse_url_with_selenium(url: str) -> Dict[str, Any]:
        """
        Parse URL using Selenium WebDriver to bypass bot detection
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
            
            print(f"[SELENIUM] Loading URL: {url}")
            
            # Setup Chrome options with stronger anti-detection
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Different user agents for different sites
            if 'blocket.se' in url:
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                chrome_options.add_argument(f'user-agent={user_agent}')
                chrome_options.add_argument('--lang=sv-SE')
            elif 'mobile.de' in url:
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                chrome_options.add_argument(f'user-agent={user_agent}')
                chrome_options.add_argument('--lang=de-DE')
            else:
                user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                chrome_options.add_argument(f'user-agent={user_agent}')
            
            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            
            # Execute CDP commands to further mask automation
            try:
                driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": user_agent,
                    "platform": "Windows" if 'mobile.de' in url else "MacIntel"
                })
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except:
                pass
            
            try:
                # Navigate to URL
                driver.get(url)
                print(f"[SELENIUM] Page loaded, waiting for content...")
                
                # For Blocket, wait for specific elements
                if 'blocket.se' in url:
                    try:
                        # Wait for the main content to load (title or price)
                        WebDriverWait(driver, 10).until(
                            lambda d: d.find_element(By.TAG_NAME, "body") and len(d.page_source) > 10000
                        )
                        print("[SELENIUM] Blocket content detected")
                        time.sleep(3)  # Extra wait for dynamic content
                    except:
                        print("[SELENIUM] Timeout waiting for Blocket content, continuing anyway")
                        time.sleep(5)
                else:
                    # For other sites, general wait
                    time.sleep(4)
                
                # Get page text directly using JavaScript for better encoding
                try:
                    # Try to get body text via JavaScript
                    body_text = driver.execute_script("return document.body.innerText;")
                    if body_text and len(body_text) > 100:
                        text = body_text
                        print(f"[SELENIUM] Got text via JavaScript: {len(text)} chars")
                    else:
                        raise Exception("Empty text")
                except:
                    # Fallback to parsing HTML
                    page_source = driver.page_source
                    print(f"[SELENIUM] Page source length: {len(page_source)} bytes")
                    
                    # Parse with BeautifulSoup
                    soup = BeautifulSoup(page_source, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style", "noscript"]):
                        script.decompose()
                    
                    # Get text
                    text = soup.get_text(separator='\n')
                    
                    # Clean up text - better cleaning for Swedish characters
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)
                    
                    print(f"[SELENIUM] Extracted text via BS4: {len(text)} chars")
                
                # Parse the text
                data = AdParser._parse_text(text)
                data['ad_url'] = url
                
                return data
                
            finally:
                driver.quit()
                print("[SELENIUM] Driver closed")
                
        except ImportError:
            return {'error': 'Selenium ikke installeret. Kør: pip install selenium', 'needs_selenium': True}
        except Exception as e:
            return {'error': f'Selenium fejl: {str(e)}', 'selenium_error': True}

    @staticmethod
    def _parse_text(text: str) -> Dict[str, Any]:
        """Extract structured data from OCR text with improved multilingual support"""
        data = {}
        text_upper = text.upper()
        
        # Extract VIN - more flexible pattern
        vin_match = AdParser.VIN_PATTERN.search(text)
        if vin_match:
            data['vin'] = vin_match.group(0).upper()
        
        # Extract car make and model FIRST (improved detection)
        make_found = False
        for make in AdParser.CAR_MAKES:
            # Case-insensitive search with word boundaries
            pattern = re.compile(rf'\b{re.escape(make)}\b', re.IGNORECASE)
            make_match = pattern.search(text)
            if make_match:
                data['make'] = make
                make_found = True
                
                # Try to extract model (words after make, before year/price/specs)
                # Look for 2-3 words after the make
                after_make = text[make_match.end():make_match.end()+150]
                # Clean and extract model - improved pattern to capture model numbers/letters
                # Skip over newlines and slashes first
                model_pattern = re.compile(r'^[\s/\n]*([A-Z0-9][A-Za-z0-9\-\s\+]{1,40}?)(?:[\s\n]*(?:\d{4}|€|DKK|SEK|kr|\n\n|Säljs|Modellår|Model|AMG|Benzin|Diesel|Automatik|Manuel))', re.IGNORECASE)
                model_match = model_pattern.search(after_make)
                if model_match:
                    model = model_match.group(1).strip()
                    # Clean up model (remove trailing junk but keep + and numbers)
                    # Split by newline first to avoid getting too much
                    model = model.split('\n')[0].strip()
                    # Remove any leading slashes or spaces
                    model = model.lstrip('/ ')
                    model_words = model.split()[:4]  # Max 4 words/parts
                    if model_words:
                        data['model'] = ' '.join(model_words)
                break
        
        # If make not found in list, try to extract from common patterns
        if not make_found:
            # Look for patterns like "Brand Model Year" or "Year Brand Model"
            brand_model_pattern = re.compile(r'(?:^|\n)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([A-Z0-9][A-Za-z0-9\-\s]{2,20}?)\s+(?:\d{4})', re.MULTILINE)
            bm_match = brand_model_pattern.search(text)
            if bm_match:
                data['make'] = bm_match.group(1).strip()
                data['model'] = bm_match.group(2).strip()
        
        # Extract year (first registration) - improved
        year_matches = AdParser.YEAR_PATTERN.findall(text)
        if year_matches:
            years = [int(y) for y in year_matches if 2000 <= int(y) <= 2026]  # Filter reasonable years
            if years:
                data['year'] = max(years)  # Most recent year is usually the car year
        
        # Extract registration date
        reg_match = AdParser.REGISTRATION_PATTERN.search(text)
        if reg_match:
            data['registration_date'] = reg_match.group(1)
        
        # Extract price and currency
        # Try pattern with "Pris" label first
        price_match = AdParser.PRICE_PATTERN_AFTER.search(text)
        after = False
        if not price_match:
            price_match = AdParser.PRICE_PATTERN.search(text)
            after = True
        
        if price_match:
            if after:
                price_str = price_match.group(1)
                currency_raw = price_match.group(2).upper()
            else:
                price_str = price_match.group(1)
                currency_raw = price_match.group(2).upper()
            # Remove ALL separators (spaces, non-breaking spaces, dots, commas, newlines)
            price_str = price_str.replace('.', '').replace(',', '').replace(' ', '').replace('\xa0', '').replace('\n', '').strip()
            try:
                data['price'] = int(price_str)
            except:
                pass
            # Normalize currency
            if currency_raw in ('DKK', 'KR'):  # 'kr' default DKK but check context
                # If Swedish indicators, it's likely SEK
                if 'BLOCKET' in text.upper() or 'SVERIGE' in text.upper():
                    data['purchase_currency'] = 'SEK'
                else:
                    data['purchase_currency'] = 'DKK'
            elif currency_raw in ('EUR', '€'):
                data['purchase_currency'] = 'EUR'
            elif currency_raw == 'SEK':
                data['purchase_currency'] = 'SEK'
        
        # Extract mileage - improved with multilingual support
        # Note: Swedish "mil" = 10 km, so convert accordingly
        mileage_patterns = [
            # Swedish format: "670 mil" - need to convert (1 mil = 10 km)
            (re.compile(r'(?:Miltal|Körda mil)[:\s]*([0-9\s]+)\s*mil(?!j|k)', re.IGNORECASE), 10),
            (re.compile(r'([0-9\s]+)\s*mil(?!j|k)(?:\n|\s|$)', re.IGNORECASE), 10),  # "670 mil"
            # German/Danish/English: km format
            (re.compile(r'(?:Kilometerstand|Mileage)[:\s]*([0-9\.\,\s]+)\s*km', re.IGNORECASE), 1),
            (re.compile(r'([0-9]{2,7}[\.]{0,1}[0-9]{3})\s*km', re.IGNORECASE), 1),  # Standard format
            (re.compile(r'([0-9\.\,\s]+)\s*km', re.IGNORECASE), 1)  # Any number + km
        ]
        for pattern, multiplier in mileage_patterns:
            mileage_match = pattern.search(text)
            if mileage_match:
                mileage_str = mileage_match.group(1).replace('.', '').replace(',', '').replace(' ', '')
                try:
                    mileage_val = int(mileage_str) * multiplier
                    if 10 <= mileage_val <= 9999999:  # Reasonable mileage range
                        data['mileage'] = mileage_val
                        break
                except:
                    pass
        
        # Extract color - multilingual
        color_patterns = [
            re.compile(r'(?:Farve|Färg|Color|Colour|Farbe|Lackierung)[:\s]*([A-Za-zæøåÆØÅäöüÄÖÜß\s\-]+?)(?:\n|,|;|\||$)', re.IGNORECASE),
            re.compile(r'\b(Sort|Hvid|Grå|Sølv|Rød|Blå|Grøn|Gul|Brun|Schwarz|Weiß|Grau|Silber|Rot|Blau|Grün|Gelb|Braun|Black|White|Gray|Silver|Red|Blue|Green|Yellow|Brown|Svart|Vit|Grå|Silver|Röd|Blå|Grön|Gul|Brun)\b', re.IGNORECASE)
        ]
        for pattern in color_patterns:
            color_match = pattern.search(text)
            if color_match:
                color = color_match.group(1).strip()
                if len(color) < 30 and not color.isdigit():  # Reasonable color name
                    data['color'] = color
                    break
        
        # Extract power (horsepower)
        power_match = AdParser.POWER_PATTERN.search(text)
        if power_match:
            try:
                data['power'] = int(power_match.group(1))
            except:
                pass
        
        # Extract doors
        doors_match = AdParser.DOORS_PATTERN.search(text)
        if doors_match:
            data['doors'] = int(doors_match.group(1))
        
        # Extract dealer/seller information - improved multilingual
        dealer_patterns = [
            re.compile(r'(?:Säljs av|Säljare)[:\s]+([A-ZÄÖÜ0-9][A-Za-zäöüÄÖÜß0-9\s&\.\-]+?)(?:\n|Skriv|Visa|Tel|$)', re.IGNORECASE),
            re.compile(r'(?:Händler|Dealer|Forhandler|Anbieter)[:\s]*([A-ZÄÖÜ0-9][A-Za-zäöüÄÖÜß0-9\s&\.\-]+?)(?:\n|Standort|Location|Ort|Tel|Telefon|Phone|$)', re.IGNORECASE),
            re.compile(r'(?:Verkäufer|Seller)[:\s]*([A-ZÄÖÜ0-9][A-Za-zäöüÄÖÜß0-9\s&\.\-]+?)(?:\n|Standort|Location|Ort|Tel|$)', re.IGNORECASE),
            re.compile(r'([A-ZÄÖÜ][A-Za-zäöüÄÖÜß\s&\.]+?)\s+(?:GmbH|AG|AB|KG|OHG|Ltd|ApS|A/S)', re.IGNORECASE)
        ]
        
        for i, pattern in enumerate(dealer_patterns):
            dealer_match = pattern.search(text)
            if dealer_match:
                dealer = dealer_match.group(1).strip()
                # Filter out invalid values
                invalid_dealer_values = ['Location', 'This listing', 'Standort', 'Ort', 'Description', 'Details', 
                                        'Map', 'View', 'Show', 'Contact', 'Call', 'Email', 'Website']
                if 3 <= len(dealer) <= 80 and not any(inv.lower() in dealer.lower() for inv in invalid_dealer_values):
                    # Remove trailing junk
                    dealer = re.sub(r'\s*(?:Tel|Phone|Telefon|Contact).*$', '', dealer, flags=re.IGNORECASE)
                    data['dealer'] = dealer.strip()
                    break
        
        # Extract location/city - improved with better filtering
        location_patterns = [
            # Pattern 1: Swedish format like "598 21 VIMMERBY" or "Badhusgatan 7, 598 21 VIMMERBY"
            re.compile(r'\d{3}\s+\d{2}\s+([A-ZÄÖÜ][A-Za-zäöüÄÖÜß\s\-]{3,30})(?:\n|,|$|Till)', re.IGNORECASE),
            # Pattern 2: After "Standort/Location/Ort" label with optional postal code
            re.compile(r'(?:Standort|Location|Ort|Placering|Bilens plats)[:\s]*(?:[A-Z]{2}[-\s])?\d{4,5}\s+([A-ZÄÖÜ][A-Za-zäöüÄÖÜß\s\-]+?)(?:\n|,|;|\||Tel|Phone|Dealer)', re.IGNORECASE),
            # Pattern 3: Just postal code + city (German format)
            re.compile(r'(?:[A-Z]{2}[-\s])?\d{4,5}\s+([A-ZÄÖÜ][A-Za-zäöüÄÖÜß\s\-]{3,30})(?:\n|,|;)', re.IGNORECASE),
            # Pattern 4: Known city names in text
            re.compile(r'\b(' + '|'.join(AdParser.GERMAN_CITIES + AdParser.SWEDISH_CITIES) + r')\b', re.IGNORECASE)
        ]
        
        location_found = False
        for i, pattern in enumerate(location_patterns):
            for match in pattern.finditer(text):
                candidate = match.group(1).strip() if match.lastindex else match.group(0).strip()
                
                # Skip invalid candidates
                invalid_words = ['this', 'listing', 'map', 'location', 'click', 'view', 'see',
                               'description', 'show', 'more', 'details', 'information', 'contact',
                               'website', 'email', 'phone', 'telefon', 'dealer', 'seller',
                               'stolar', 'säten', 'dörrar', 'wheels', 'doors', 'seats']
                if any(iw in candidate.lower() for iw in invalid_words):
                    continue
                if candidate.replace(' ', '').replace('-', '').isdigit():
                    continue
                if len(candidate) < 3 or len(candidate) > 50:
                    continue
                    
                # Clean the candidate
                candidate = re.sub(r'\s*(?:Tel|Phone|Telefon).*$', '', candidate, flags=re.IGNORECASE)
                candidate = candidate.strip()
                
                if candidate:
                    data['location'] = candidate
                    location_found = True
                    break
            
            if location_found:
                break
        
        # Determine import country from multiple signals
        import_country = None
        
        # Check for German indicators
        german_indicators = 0
        if 'MOBILE.DE' in text_upper or 'MOBILE DE' in text_upper:
            german_indicators += 3
        if any(city in text_upper for city in AdParser.GERMAN_CITIES):
            german_indicators += 2
        if any(word in text_upper for word in ['STANDORT', 'HÄNDLER', 'ERSTZULASSUNG', 'FAHRZEUGHALTER', 'HU', 'TÜV']):
            german_indicators += 1
        if any(word in text_upper for word in ['GMBH', 'KG', 'OHG']):
            german_indicators += 1
        if re.search(r'\+49\s|\(49\)', text):  # German phone code
            german_indicators += 2
        
        # Check for Swedish indicators
        swedish_indicators = 0
        if 'BLOCKET' in text_upper:
            swedish_indicators += 5  # Strong indicator
        if 'BLOCKET.SE' in text_upper:
            swedish_indicators += 5
        if any(city in text_upper for city in AdParser.SWEDISH_CITIES):
            swedish_indicators += 2
        if any(word in text_upper for word in ['SÄLJARE', 'SÄLJS AV', 'FÖRSTA REG', 'ÄGARE', 'BESIKTAD', 'MILTAL', 'KÖRDA MIL']):
            swedish_indicators += 1
        if any(word in text_upper for word in [' AB ', 'AKTIEBOLAG']):
            swedish_indicators += 1
        if re.search(r'\+46\s|\(46\)|^46\s', text):  # Swedish phone code
            swedish_indicators += 2
        if 'SVERIGE' in text_upper or 'SWEDEN' in text_upper:
            swedish_indicators += 2
        
        # Decide based on indicators
        if german_indicators > swedish_indicators and german_indicators >= 2:
            import_country = 'Tyskland'
        elif swedish_indicators > german_indicators and swedish_indicators >= 2:
            import_country = 'Sverige'
        
        if import_country:
            data['import_country'] = import_country
        
        # Extract phone number
        phone_match = AdParser.PHONE_PATTERN.search(text)
        if phone_match:
            data['phone'] = phone_match.group(0)
        
        # Extract fuel type - improved detection
        # Check for "Drivmedel\nEl" or "Drivmedel: El" pattern first (most specific)
        fuel_patterns = [
            (re.compile(r'Drivmedel[:\s\n]*(El|Diesel|Bensin|Hybrid)', re.IGNORECASE), 'direct'),
            (re.compile(r'Fuel[:\s\n]*(Electric|Diesel|Petrol|Gasoline|Hybrid)', re.IGNORECASE), 'direct'),
        ]
        
        fuel_found = False
        for pattern, match_type in fuel_patterns:
            fuel_match = pattern.search(text)
            if fuel_match:
                fuel_value = fuel_match.group(1).upper()
                if fuel_value in ['EL', 'ELECTRIC']:
                    data['fuel_type'] = 'electric'
                elif fuel_value == 'DIESEL':
                    data['fuel_type'] = 'diesel'
                elif fuel_value in ['BENSIN', 'PETROL', 'GASOLINE']:
                    data['fuel_type'] = 'gasoline'
                elif fuel_value == 'HYBRID':
                    data['fuel_type'] = 'hybrid'
                fuel_found = True
                break
        
        # Fallback to keyword search if no direct match
        if not fuel_found:
            if any(word in text_upper for word in ['DIESEL', 'DIESELMOTOR', 'TDI', 'D-']):
                data['fuel_type'] = 'diesel'
            elif any(word in text_upper for word in ['BENZIN', 'PETROL', 'GASOLINE', 'TSI', 'FSI', 'BENSIN']):
                data['fuel_type'] = 'gasoline'
            elif any(word in text_upper for word in ['ELECTRIC', 'ELEKTRISK', 'BATTERY', 'BATTERI', 'EQB', 'EQC', 'EQA', 'E-TRON', 'TAYCAN']):
                data['fuel_type'] = 'electric'
            elif any(word in text_upper for word in ['HYBRID', 'PLUG-IN', 'PHEV']):
                data['fuel_type'] = 'hybrid'
        
        # Extract transmission
        if any(word in text_upper for word in ['AUTOMATIC', 'AUTOMATGEAR', 'AUTOMAT', 'DSG', 'TIPTRONIC', 'STEPTRONIC']):
            data['transmission'] = 'automatic'
        elif any(word in text_upper for word in ['MANUAL', 'MANUELL', 'SCHALTGETRIEBE']):
            data['transmission'] = 'manual'
        
        # Extract equipment/features
        equipment = []
        for keyword in AdParser.EQUIPMENT_KEYWORDS:
            if keyword.upper() in text_upper:
                equipment.append(keyword)
        if equipment:
            data['equipment'] = ', '.join(equipment[:10])  # Limit to 10 items
        
        # Detect platform
        if 'MOBILE.DE' in text_upper or 'MOBILE DE' in text_upper:
            data['source'] = 'mobile.de'
        elif 'BLOCKET' in text_upper:
            data['source'] = 'Blocket'
        elif 'BILBASEN' in text_upper:
            data['source'] = 'Bilbasen'
        elif 'AUTOSCOUT' in text_upper:
            data['source'] = 'AutoScout24'
        
        # Calculate estimated transport cost if location is found
        if 'location' in data:
            # Pass import_country if available to help with estimation
            import_country = data.get('import_country', None)
            transport_cost, distance_km = AdParser._calculate_transport_cost(data['location'], import_country)
            if transport_cost:
                data['transport_cost'] = transport_cost
                data['distance_km'] = distance_km
        
        # Store raw text for reference
        data['raw_ocr_text'] = text
        
        return data
    
    @staticmethod
    def _calculate_transport_cost(location: str, import_country: Optional[str] = None) -> tuple[Optional[float], Optional[int]]:
        """
        Calculate estimated diesel cost for transport from location to Aalborg
        
        Args:
            location: City name from the advertisement
            import_country: Import country ('Tyskland', 'Sverige', etc.) if known
            
        Returns:
            Tuple of (cost in DKK, distance in km), or (None, None) if city not found
        """
        location_upper = location.upper().strip()
        
        # Try to find matching city
        distance_km = None
        for city, dist in AdParser.CITY_DISTANCES.items():
            if city in location_upper:
                distance_km = dist
                break
        
        # If no specific city found, use average distance based on country
        if not distance_km:
            # First check if we have import_country
            if import_country == 'Tyskland':
                distance_km = 700  # Average distance to Germany
            elif import_country == 'Sverige':
                distance_km = 650  # Average distance to Sweden
            # Otherwise check location string for country indicators
            elif any(indicator in location_upper for indicator in ['DE-', 'DEUTSCHLAND', 'GERMANY']):
                distance_km = 700  # Average distance to Germany
            elif any(indicator in location_upper for indicator in ['SE-', 'SVERIGE', 'SWEDEN']):
                distance_km = 650  # Average distance to Sweden
            # Check for other common indicators
            elif any(word in location_upper for word in ['GMBH', 'KG', 'AG']):
                distance_km = 700  # Likely Germany
            elif any(word in location_upper for word in ['AB', 'AKTIEBOLAG']):
                distance_km = 650  # Likely Sweden
        
        if distance_km:
            # Calculate diesel cost: (distance / 100) * consumption * price
            liters_needed = (distance_km / 100.0) * AdParser.DIESEL_CONSUMPTION_PER_100KM
            cost = liters_needed * AdParser.DIESEL_PRICE_DKK
            return round(cost, 2), distance_km
        
        return None, None
    
    @staticmethod
    def parse_from_upload(file_storage) -> Dict[str, Any]:
        """
        Parse advertisement from Flask file upload (supports images and PDFs)
        
        Args:
            file_storage: Flask FileStorage object from request.files
            
        Returns:
            Dictionary with extracted fields
        """
        import tempfile
        
        try:
            # Get file extension
            filename = file_storage.filename.lower()
            is_pdf = filename.endswith('.pdf')
            
            # Save to temporary file
            suffix = '.pdf' if is_pdf else '.png'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                file_storage.save(tmp.name)
                tmp_path = tmp.name
            
            # Parse based on file type
            if is_pdf:
                data = AdParser.parse_pdf(tmp_path)
            else:
                data = AdParser.parse_image(tmp_path)
            
            # Clean up
            os.unlink(tmp_path)
            
            return data
            
        except Exception as e:
            return {'error': str(e)}
