def scrape_website(url):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    from selenium.webdriver.chrome.options import Options
    
    # Setup headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Inisialisasi Selenium WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Buka halaman web
        driver.get(url)
        
        # Tunggu elemen dengan class tertentu muncul
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "whitespace-pre-wrap"))
            )
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "flex.w-full.flex-col.gap-1.empty:hidden.first:pt-[3px]"))
            )
        except Exception as e:
            print(f"Error waiting for elements: {e}")
        
        # Ambil HTML setelah JavaScript selesai berjalan
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        
        # Cari semua elemen <div> dengan class spesifik
        div_prompts = soup.find_all('div', class_='whitespace-pre-wrap')
        div_responses = soup.find_all('div', class_='flex w-full flex-col gap-1 empty:hidden first:pt-[3px]')
        
        prompts = []
        responses = []
        
        # Looping untuk mengambil semua teks dalam div yang ditemukan
        for div in div_prompts:
            prompts.append(div.get_text(strip=True))
        
        for div in div_responses:
            responses.append(div.get_text(strip=True))
        
        # Tutup browser setelah selesai
        driver.quit()
        
        # Jika data berhasil diambil, kembalikan semua data (bukan hanya index 0)
        if prompts and responses:
            # Gabungkan semua prompt
            all_prompts = "".join(prompts)
            # Gabungkan semua response
            all_responses = "".join(responses)
            return all_prompts, all_responses
        else:
            return "Tidak ada prompt yang ditemukan", "Tidak ada response yang ditemukan"
            
    except Exception as e:
        driver.quit()
        print(f"Error during scraping: {e}")
        return "Error saat scraping", str(e)
    
# Fungsi preprocessing
def preprocess_text(text):
    # Memastikan teks ada dan bukan None
    if not text:
        return ""
    # Mengubah teks menjadi lowercase
    text = text.lower()
    # Membuat teks lebih mudah dibaca dengan menambahkan newline
    # Mengganti beberapa spasi dengan satu spasi
    import re
    text = re.sub(r'\s+', ' ', text)
    # Menambahkan newline setelah setiap kalimat
    text = re.sub(r'([.!?])\s+', r'\1\n\n', text)
    return text