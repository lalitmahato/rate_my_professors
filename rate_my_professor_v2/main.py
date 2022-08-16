# importing library
import time
from bs4 import BeautifulSoup
from pymongo import MongoClient
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.chrome.service import Service
from pymongo import MongoClient

# Remove Character from the text
def Remove_Character(Text, characters):
    val = Text.get_text(separator=' ').rstrip().split()
    val = ' '.join(val)
    for c in characters:
        val = ''.join(val.split(c))
    return val

# Get the position value
def Get_Position_Value(Text_Value, value_address):
    val = Text_Value.get_text(separator=' ').rstrip().split()
    return(val[value_address])

# Join the array with given tag
def Join_Value_With(value, join_value):
    val = value.get_text(separator=' ').rstrip().split()
    val = join_value.join(val)
    return(val)

# To Reamove Unusal Spaces
def Remove_Unusal_Spaces(value):
    try:
        val = value.get_text(separator=' ').rstrip().split()
        val = ' '.join(val)
    except:
        val = ''
    return(val)

# Make the attributes naming 
def Name_Attribute(attribute):
    """remove the unusual spaces and convert the sentence into array"""
    attr = attribute.get_text(separator=' ').rstrip().split()
    attr = [x.casefold() for x in attr] # capitalize the first letter of the word
    attr = '_'.join(attr) # Join each word with "_"
    return(attr)

def Get_href(anchor):
    """scrap the anchor tag href"""
    href =  anchor.find('a', href=True)['href']
    return href

s = Service("C:\Program Files (x86)\chromedriver.exe")
driver = webdriver.Chrome(service=s)

# Go through the url
def get_url(url):
    driver.get(url)

# click cookies close btn
def close_cookies():
    cookies = driver.find_element(By.CLASS_NAME, 'CCPAModal__StyledCloseButton-sc-10x9kq-2')
    cookies.click()
    
# click on close btn to close the Ad
def close_Ad():
    close_ad = driver.find_element(By.ID, 'bx-close-inside-1177612')
    close_ad.click()
    
# Try to close cookies or ad    
def close_cookies_or_ad():
    try:
        close_cookies()
    except:
        try:
            close_Ad()
        except:
            pass

# click on show more btn
def show_more_btn():
    close_cookies_or_ad()
    show_more = driver.find_element(By.CLASS_NAME, 'Buttons__Button-sc-19xdot-1')
    show_more.click()

def to_bs4_object(html_page):
    soup = BeautifulSoup(html_page, "html.parser")
    return soup

# Return the current url html code
def get_page_source():
    close_cookies_or_ad()
    result = driver.page_source
    soup = to_bs4_object(result)
    return soup

def get_professor_count():
    close_cookies_or_ad()
    soup = get_page_source()
    pagination_header = soup.find('div', class_='SearchResultsPage__SearchResultsPageHeader-vhbycj-3')
    try:
        professor_count = int(Get_Position_Value(pagination_header, 0))
        uni_name = pagination_header.div.h1.span.b.get_text(separator=' ')
    except:
        professor_count = 0
        uni_name = pagination_header.div.h1.span.b.get_text(separator=' ')
    return (professor_count, uni_name)

def scrapper(page, uni_name, uid):
    professor_data = []
    professor_cards = page.find_all('a', class_='TeacherCard__StyledTeacherCard-syjs0d-0 dLJIlx')
    for card in professor_cards:
        u_name = card.find('div', class_='CardSchool__School-sc-19lmz2k-1').text
        if u_name == uni_name:
            pro_data = {}
            pro_data['overall_rating'] = float(card.find('div', class_='CardNumRating__CardNumRatingNumber-sc-17t4b9u-2').text)
            rating = card.find('div', class_='CardNumRating__CardNumRatingCount-sc-17t4b9u-3')
            pro_data['ratings'] = int(Get_Position_Value(rating, 0))
            pro_data['professor_name'] = card.find('div', class_='CardName__StyledCardName-sc-1gyrgim-0').text
            pro_data['subject'] = card.find('div', class_='CardSchool__Department-sc-19lmz2k-0').text
            card_feed = card.find_all('div', class_='CardFeedback__CardFeedbackNumber-lq6nix-2')
            pro_data['level_of_difficulty'] = card_feed[1].text
            pro_data['would_take_again'] = card_feed[0].text
            professor_data.append(pro_data)
    whole_data = {
        'uni_id': uid,
        'university_name': uni_name,
        'professors': professor_data,
    }
    return whole_data

# Database Configuration
user = 'web_scrapper'
password = 'CW8Cty2cc9khaTdy'
database = 'rate_my_professor_v2'
connection_str = "mongodb+srv://" + user + ":" + password + "@cluster0.c4cev.mongodb.net/" + database + "?retryWrites=true&w=majority"

client = MongoClient(connection_str)
db = client.get_database(database)
college_db = db.rate_my_professor.rate_my_professor_v2
print('Connection Status:\n',college_db)

end = 6049
start = 0
status_count = db['status_lalit'].count_documents({})
unable_scrap = 0
scrap_data_count = status_count
number = status_count + start

main_url = 'https://www.ratemyprofessors.com/search/teachers?query=*&sid='
counter = 0
# while number < 24:
while number < end:
    print('\n',number)
    perc = scrap_data_count/(end-start) * 100
    print("Completed: {} %".format(perc))
    print("Data Scraped: ", scrap_data_count)
    print("Unable to scrap count: ", unable_scrap)
    url = main_url + str(number+1)
    get_url(url)
    print('URL: ', url)
    try:
        close_cookies_or_ad()
        professor_count, uni_name = get_professor_count()
        print('professor_count: ', professor_count)
        for i in range(int(professor_count/8)):
            try:
                close_cookies_or_ad()
                time.sleep(3)
                show_more_btn()
                time.sleep(3)
            except:
                pass
        if professor_count !=0:
            close_cookies_or_ad()
            data_result_page = get_page_source()
            data = scrapper(data_result_page, uni_name, number+1)
            db['rate_my_professir_v2'].insert_one(data)
            db['status_lalit'].insert_one({
                'institution_name': uni_name,
                'url': url,
                'information_retereaved': True,
            })
            scrap_data_count = scrap_data_count + 1
            number = number + 1
            counter = 0
            print('Successfully Scrapped!!...')
        elif professor_count == 0:
            db['rate_my_professir_v2'].insert_one({
                'uni_id': number+1,
                'university_name': uni_name,
                'professors': [],
            })
            db['status_lalit'].insert_one({
                'institution_name': uni_name,
                'url': url,
                'information_retereaved': True,
            })
            scrap_data_count = scrap_data_count + 1
            number = number + 1
            counter = 0
            print('Successfully Scrapped!!...')
    except:
        try:
            close_cookies_or_ad()
            if counter == 1:
                db['status_lalit'].insert_one({
                    'institution_name': '',
                    'url': url,
                    'information_retereaved': False,
                })
                number = number + 1
                counter = 0
                print('Unable to scrap...!')
            else:
                counter = counter + 1
                print('Something went Wrong!')
                print('Trying to scrap again...!')
        except:
            db['status_lalit'].insert_one({
                'institution_name': uni_name,
                'url': url,
                'information_retereaved': False,
            })
            unable_scrap = unable_scrap + 1
            print('Something went Wrong!')
            print('Unable to scrap...!')
            number = number + 1