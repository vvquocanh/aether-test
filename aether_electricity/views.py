from django.shortcuts import render
import requests

url = 'https://api.openei.org/utility_rates'
api_key = 'wA2jMcGQG4CovUDCfwZAZcBHRyv8P4jWvr1P6hBm'
version = 'latest'
format = 'json'
epoch = 1640995200

def calculate_cost_formula_1(user_input):
    consumption, escalator, most_likely_utility, utilities, energy_rate, _ = get_utilities(user_input)

    average, first_year_cost = get_price_formula_1(consumption, escalator, energy_rate) 

    context = build_context(average, most_likely_utility, utilities, first_year_cost)
    return context

def calculate_cost_formula_2(user_input):
    consumption, escalator, most_likely_utility, utilities, energy_rate, weekdays_schedule = get_utilities(user_input)

    average, first_year_cost = get_price_formula_2(consumption, escalator, energy_rate, weekdays_schedule) 

    context = build_context(average, most_likely_utility, utilities, first_year_cost)
    return context

def get_utilities(user_input):
    address = user_input.get('address')
    consumption = user_input.get('consumption')
    escalator = user_input.get('escalator')

    most_likely_utility, utilities = get_utility_list(address=address)

    energy_rate, weekdays_schedule = get_detail_utility_rate(utility=most_likely_utility)

    return consumption, escalator, most_likely_utility, utilities, energy_rate, weekdays_schedule

def build_context(average, most_likely_utility, utilities, first_year_cost):
    context = {
        'average_cost_per_kwh': average,
        'most_likely_utility_tariff': most_likely_utility,
        'utility_tariffs': utilities,
        'first_year_cost': first_year_cost
    }

    return context

def get_utility_list(address):
    params = {
        'api_key': api_key,
        'version': version,
        'format': format,
        'address': address,
        'detail': 'minimal'
    }

    utilities = requests.get(url=url, params=params).json().get('items')
    return filter_utility(utilities)

def filter_utility(utilities):
    most_likely_utility = ''
    satisfied_utilities = []

    for utility in utilities:
        if utility.get('startdate') < epoch:
            continue
        satisfied_utilities.append(utility.get('utility'))

        if most_likely_utility != '':
            continue
        
        if utility.get('approved') and utility.get('is_default'):
            most_likely_utility = utility.get('utility')

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

def get_price_formula_1(consumption, escalator, energy_rate):
    total_rate = 0
    rate_count = 0
    for period in energy_rate:
        for level in period:
            total_rate += level['rate']
            rate_count += 1

    average = total_rate / rate_count
    first_year_cost = float(consumption) * average

    return average, first_year_cost

def get_price_formula_2(consumption, escalator, energy_rate, weekdays_schedule):
    average = 0
    first_year_cost = 0

    return average, first_year_cost