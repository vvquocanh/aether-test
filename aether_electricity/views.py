from django.shortcuts import render
import requests

url = 'https://api.openei.org/utility_rates'
api_key = 'wA2jMcGQG4CovUDCfwZAZcBHRyv8P4jWvr1P6hBm'
version = 'latest'
format = 'json'
epoch = 1640995200

def get_user_input(user_input):
    address = user_input.get('address')

    most_likely_utility, utilities = get_utility_list(address=address)

    energy_rate, weekdays_schedule = get_detail_utility_rate(utility=most_likely_utility)

    average, first_year_cost = get_price( energy_rate, weekdays_schedule)

    return average, first_year_cost, utilities

def get_utility_list(address):
    params = {
        'api_key': api_key,
        'version': version,
        'format': format,
        'address': address
    }

    utilities = requests.get(url=url, params=params).json().get('items')

    return filter_utility(utilities)

def filter_utility(utilities):
    most_likely_utility = ''
    satisfied_utilities = []

    for utility in utilities:
        if utility.get('startdate') < epoch:
            continue

        satisfied_utilities.append(utility.get('label'))

        if most_likely_utility != '':
            continue
        
        if utility.get('approved') and utility.get('is_default'):
            most_likely_utility = utility

    return most_likely_utility, satisfied_utilities

def get_detail_utility_rate(utility):
    params = {
        'api_key': api_key,
        'version': version,
        'format': format,
        'ratesforutility': utility,
        'detail': 'full'
    }

    data = requests.get(url=url, params=params).json().get('items')[0]

    energy_rate = data.get('energyratestructure')
    weekdays_schedule = data.get('demandweekdayschedule')

    return energy_rate, weekdays_schedule

def get_price(energy_rate, weekdays_schedule):
    average = 0
    first_year_cost = 0

    return average, first_year_cost