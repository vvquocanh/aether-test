from django.shortcuts import render
import numpy as np
import requests
import matplotlib.pyplot as plt
import mpld3

from aether_electricity.models import ElectricityUser, ProposalUtility

url = 'https://api.openei.org/utility_rates'
api_key = 'wA2jMcGQG4CovUDCfwZAZcBHRyv8P4jWvr1P6hBm'
version = 'latest'
format = 'json'
epoch = 1640995200

daily_usage = [0.02568, 0.02397, 0.02142, 0.01884, 0.01712, 0.01799, 0.01799, 0.02226, 
                0.02998, 0.03597, 0.04110, 0.04284, 0.04452, 0.04541, 0.04966, 0.05137, 
                0.04966, 0.04284, 0.04027, 0.05993, 0.07877, 0.08562, 0.07877, 0.05822]

class UtilityTariff:
    def __init__(self, id, name):
        self.id = id
        self.name = name

def calculate_cost_formula_1(user, user_input):
    address, consumption, escalator, most_likely_tariff, tariffs, energy_rate, _ = get_utilities(user_input)

    if len(tariffs) < 0:
        return None

    average, first_year_cost, cost_graph = get_price_formula_1(consumption, escalator, energy_rate) 

    store_electricity_user(user, address, consumption, escalator, most_likely_tariff, tariffs, average, first_year_cost, energy_rate)

    context = build_context(average, most_likely_tariff, tariffs, first_year_cost, cost_graph)
    return context

def calculate_cost_formula_2(user, user_input):
    address, consumption, escalator, most_likely_tariff, tariffs, energy_rate, weekdays_schedule = get_utilities(user_input)

    if len(tariffs) < 0:
        return None

    average, first_year_cost, cost_graph = get_price_formula_2(consumption, escalator, energy_rate, weekdays_schedule) 

    store_electricity_user(user, address, consumption, escalator, most_likely_tariff, tariffs, average, first_year_cost, energy_rate)

    context = build_context(average, most_likely_tariff, tariffs, first_year_cost, cost_graph)
    return context

def store_electricity_user(user, 
                           address, 
                           consumption, 
                           escalator, 
                           most_likely_tariff, 
                           tariffs, 
                           average, 
                           first_year_cost, 
                           energy_rate):
    if user.is_anonymous:
        return None

    proposal_utility, _ = ProposalUtility.objects.get_or_create(
        id=most_likely_tariff.id,
        defaults={
            'tariff_name': most_likely_tariff.name,
            'tariff_matrix': energy_rate,
        }
    )

    ElectricityUser.objects.create(
        user = user,
        address = address,
        consumption = consumption,
        escalator = escalator,
        average_rate = average,
        most_likely_utility_tariff = most_likely_tariff.name,
        utility_tariff_list = [tariff.name for tariff in tariffs],
        first_year_cost = first_year_cost,
        selected_utility_tariff = proposal_utility
    )
    

def recalculate_formula_1(id, consumption, escalator):
    energy_rate, _ = get_detail_utility_rate(id)

    average, first_year_cost, cost_graph = get_price_formula_1(consumption, escalator, energy_rate)
    
    context = build_update_context(average, first_year_cost, cost_graph)
    
    return context

def recalculate_formula_2(id, consumption, escalator):
    energy_rate, weekdays_schedule = get_detail_utility_rate(id)

    average, first_year_cost, cost_graph = get_price_formula_2(consumption, escalator, energy_rate, weekdays_schedule)
    
    context = build_update_context(average, first_year_cost, cost_graph)
    
    return context

def get_utilities(user_input):
    address = user_input.get('address')
    consumption = int(user_input.get('consumption'))
    escalator = int(user_input.get('escalator'))

    most_likely_tariff, tariffs = get_tariff_list(address)
    energy_rate, weekdays_schedule = get_detail_utility_rate(label=most_likely_tariff.id)

    return address, consumption, escalator, most_likely_tariff, tariffs, energy_rate, weekdays_schedule

def build_context(average, most_likely_tariff, tariffs, first_year_cost, cost_graph):
    context = {
        'average_cost_per_kwh': average,
        'most_likely_utility_tariff': most_likely_tariff.name,
        'utility_tariffs': tariffs,
        'first_year_cost': first_year_cost,
        'cost_graph': cost_graph
    }

    return context

def build_update_context(average, first_year_cost, cost_graph):
    context = {
        'average_cost_per_kwh': average,
        'first_year_cost': first_year_cost,
        'cost_graph': cost_graph
    }

    return context

def get_tariff_list(address):
    params = {
        'api_key': api_key,
        'version': version,
        'format': format,
        'address': address,
        'detail': 'minimal'
    }
    
    tariffs = requests.get(url=url, params=params).json().get('items')
    return filter_tariff(tariffs)

def filter_tariff(tariffs):
    is_found_most_likely = False
    satisfied_tariffs = []
    most_likely_tariff = None
    for tariff in tariffs:
        if 'startdate' not in tariff or tariff.get('startdate') < epoch:
            continue
        satisfied_tariffs.append(UtilityTariff(tariff.get('label'),tariff.get('name')))

        if is_found_most_likely:
            continue
        
        if tariff.get('approved') and tariff.get('is_default'):
            most_likely_tariff = UtilityTariff(tariff.get('label'),tariff.get('name'))

    return most_likely_tariff, satisfied_tariffs

def get_detail_utility_rate(label):
    params = {
        'api_key': api_key,
        'version': version,
        'format': format,
        'getpage': label,
        'detail': 'full'
    }

    data = requests.get(url=url, params=params).json().get('items')[0]
    energy_rate = data.get('energyratestructure')
    weekdays_schedule = data.get('energyweekdayschedule')

    return energy_rate, weekdays_schedule

def get_price_formula_1(consumption, escalator, energy_rate):
    total_rate = 0
    rate_count = 0
    for period in energy_rate:
        for level in period:
            total_rate += level['rate']
            rate_count += 1

    average = total_rate / rate_count

    first_year_cost, cost_graph = calculate_annual_cost(average, consumption, escalator)

    return average, first_year_cost, cost_graph


def get_price_formula_2(consumption, escalator, energy_rate, weekdays_schedule):
    total_cost = 0    
    consumption_per_hour = get_consumption_per_hour(consumption)

    for month in range(len(weekdays_schedule)):
        for hour in range(len(consumption_per_hour)):
            temp_consumption_per_hour = consumption_per_hour[hour]
            schedule = weekdays_schedule[month]
            current_rate = energy_rate[schedule[hour]]
            for level in current_rate:
                if 'max' in level.keys():
                    if temp_consumption_per_hour <= level['max']:
                        total_cost += temp_consumption_per_hour * level['rate']
                        break
                    else:
                        total_cost += level['max'] * level['rate']
                        temp_consumption_per_hour -= level['max']
                else:
                    total_cost += temp_consumption_per_hour * level['rate']
    average = total_cost / consumption

    cost_graph = calculate_annual_cost_2(total_cost, escalator)

    return average, total_cost, cost_graph

def calculate_annual_cost(average, consumption, escalator):
    first_year_cost = 0
    x = np.arange(1, 21)
    y = np.array([])

    for i in range (0, 20):
        annual_cost = consumption * average
        if i == 0:
            first_year_cost = annual_cost
        
        y = np.append(y, annual_cost)

        consumption += consumption * escalator / 100

    cost_graph = draw_cost_graph(x, y)

    return first_year_cost, cost_graph

def calculate_annual_cost_2(annual_cost, escalator):
    x = np.arange(1, 21)
    y = np.array([])

    for i in range (0, 20):
        y = np.append(y, annual_cost)

        annual_cost += annual_cost * escalator / 100

    cost_graph = draw_cost_graph(x, y)

    return cost_graph

def draw_cost_graph(x, y):
    plt.figure(figsize=(10,6))
    plt.plot(x, y, marker='o')
    plt.title('Cost Graph')
    plt.xlabel('Year')
    plt.ylabel('Cost')

    cost_graph = mpld3.fig_to_html(plt.gcf())

    return cost_graph

def get_consumption_per_hour(consumption):
    raw_consumption_per_hour = [usage * consumption for usage in daily_usage]
    consumption_per_hour = [int(raw_consumption) for raw_consumption in raw_consumption_per_hour]

    remainder = consumption - sum(consumption_per_hour)

    differences = [(i, raw_consumption_per_hour[i] - consumption_per_hour[i]) for i in range(len(daily_usage))]

    differences.sort(key=lambda x: x[1], reverse=True)

    for i in range(remainder):
        consumption_per_hour[differences[i][0]] += 1

    return consumption_per_hour
