import requests
from src.constants import SOLVE_URL
from itertools import product

def solve_multi_choice_task(task_guid: str):
    cookies = {
        'PHPSESSID': 'l05rodk7k5ul2ejlirhj3dlr47',
        '__ddg1_': '51QNxivaOddslX6I0uHG',
        '_ym_d': '1732536813',
        '_ym_uid': '1732536813833014376',
        'md_auto': 'qprint'
    }
    
    session = requests.Session()
    
    for combination in product(range(2), repeat=5):
        answer = ''.join(map(str, combination))
        data = {
            'guid': task_guid,
            'answer': answer
        }
        
        response = session.post(SOLVE_URL, data=data, cookies=cookies)
        if response.text == '3':
            return answer
            
    return None