import db_configuration
from pymongo import MongoClient
from scrapper import main_page_scrapper
import requests
# import pandas as pd

# database connection setup
client = MongoClient(db_configuration.connection_str)
db = client.get_database(db_configuration.database)
college_db = db.rate_my_professor
print('Connection Status:\n',college_db)


status_count = db['status'].count_documents({})
print(status_count)

scrap_data_count = status_count
number = status_count

domain_name = 'https://www.usnews.com/'
unable_scrap = 0
total_uid = 6049

# while number < 10:
while number < total_uid:
    flag = 0
    # container to store all the data
    print('\n',number)
    perc = scrap_data_count/total_uid * 100
    print("Completed: {} %".format(perc))
    print("Data Scraped: ", scrap_data_count)
    print("Unable to scrap count: ", unable_scrap)
    main_url = "https://www.ratemyprofessors.com/campusRatings.jsp?sid="
    main_req_url = main_url + str(number+1)
    print('URL: ',  main_req_url)
    main_page = requests.get(main_req_url, timeout=100, headers={'User-Agent': 'Mozilla/5.0'})
    print("Connection Status Code: ", main_page.status_code)
    print("Information Retereaved:", main_page.status_code == requests.codes.ok)
    try:
        whole_data = main_page_scrapper(main_page)
    except:
        flag = 1
    if flag == 0:
        db['rate_my_professir'].insert_one(whole_data)
        db['status'].insert_one({
            'institution_name': whole_data["university_name"] ,
            'url': main_req_url,
            'connection_status_code' : main_page.status_code,
            'information_retereaved': main_page.status_code == requests.codes.ok,
        })
        print('Successfully Scrapped!!...')
    else:
        db['status'].insert_one({
            'url': main_req_url,
            'connection_status_code' : main_page.status_code,
            'information_retereaved': main_page.status_code == requests.codes.ok,
        })
        db['unable_to_scrap'].insert_one({
            'url': main_req_url,
            'connection_status_code' : main_page.status_code,
            'information_retereaved': main_page.status_code == requests.codes.ok,
        })
        print('Unable to scrap!!...')
    scrap_data_count = scrap_data_count + 1
    number = number + 1
