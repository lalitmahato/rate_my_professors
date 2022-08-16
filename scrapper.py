from bs4 import BeautifulSoup
from helper import Remove_Unusal_Spaces


def main_page_scrapper(page):
    main_page_data = {}
    # school info
    soup = BeautifulSoup(page.content,'html.parser')
    main_page_data["university_name"] = Remove_Unusal_Spaces(soup.find('div', class_="result-text"))
    school_rating_section = soup.find('div', class_="right-breakdown school-averages")
    ins_over_rating = school_rating_section.find('div', class_='overall-rating')
    o_r = Remove_Unusal_Spaces(ins_over_rating.find('span'))
    main_page_data['over_rating'] = float(o_r) if o_r != "" else 0
    quality_breakdown = school_rating_section.find_all('div', class_='rating')
    rating_breakdown = []
    for rat in quality_breakdown:
        label = Remove_Unusal_Spaces(rat.find('span', class_='label'))
        score = Remove_Unusal_Spaces(rat.find('span', class_='score'))
        rating_breakdown.append({
            'label': label,
            'rating': float(score) if score != '' else 0
        })
    main_page_data["institution_rating_breakdown"] = rating_breakdown
    
    # Orifessir Rating info
    professor_rating = soup.find('div', class_="left-breakdown top-professors")
    pro_over_rating = professor_rating.find('div', class_='overall-rating')
    p_o_r = Remove_Unusal_Spaces(pro_over_rating.find("span"))
    main_page_data['professor_overall_rating'] = float(p_o_r) if p_o_r != "" else 0
    professor_ratings = []
    pro_ratings = professor_rating.find_all('li')
    for p_ratings in pro_ratings:
        professor_name = p_ratings.find('div', class_='professor-name').text
        pro_name = professor_name.split(',')
        p_name = pro_name[1].rstrip() + " " + pro_name[0].rstrip()
        review = p_ratings.find('div', class_='professor-rating-count').text.split()
        pro_rat = Remove_Unusal_Spaces(p_ratings.find('span', class_="professor-rating"))
        professor_ratings.append({
            'professor_name': p_name,
            'reviews': int(review[0]),
            'rating': float(pro_rat) if pro_rat != "" else 0
        })
    main_page_data['professor_ratings'] = professor_ratings
    return main_page_data