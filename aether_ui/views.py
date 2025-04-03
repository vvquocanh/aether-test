import json
from django.http import JsonResponse
from django.shortcuts import render
from aether_electricity.views import (
    UtilityTariff,
    calculate_cost_formula_1,
    calculate_cost_formula_2, 
    recalculate_formula_1,
    recalculate_formula_2)

# Create your views here.
def main_view(request):
    if request.method != 'GET':  
        return render(request, 'method_not_allowed.html')
    else:
        return render(request, 'main.html')
    
def calculation_view(request):
    if request.method == 'POST':
        user = request.user
        data = request.POST

        request.session['consumption'] = data.get('consumption')
        request.session['escalator'] = data.get('escalator')

        if 'calculate_formula_1' in data:
            context = calculate_cost_formula_1(user, data)
            if context == None:
                return render(request, 'not_exist.html')
            else:    
                return render(request, 'calculation_method_1.html', context)

        elif 'calculate_formula_2' in data:
            context = calculate_cost_formula_2(user, data)
            if context == None:
                return render(request, 'not_exist.html')
            else:
                return render(request, 'calculation_method_2.html', context)
        else:
            return render(request, 'method_not_allowed.html')
    elif request.method == 'PUT':
        data = json.loads(request.body.decode('utf-8'))
        consumption = int(request.session.get('consumption'))
        escalator = int(request.session.get('escalator'))
        
        if data.get('calculate_formula') == 1:
            context = recalculate_formula_1(data.get('tariff_id'), consumption, escalator)
            return JsonResponse(
                {
                'average_cost_per_kwh': context['average_cost_per_kwh'],
                'first_year_cost': context['first_year_cost'],
                'cost_graph': context['cost_graph']
                }
            )
        
        elif data.get('calculate_formula') == 2:
            context = recalculate_formula_2(data.get('tariff_id'), consumption, escalator)
            print(context['average_cost_per_kwh'])
            return JsonResponse(
                {
                'average_cost_per_kwh': context['average_cost_per_kwh'],
                'first_year_cost': context['first_year_cost'],
                'cost_graph': context['cost_graph']
                }
            )

        else:
            return render(request, 'method_not_allowed.html') 
    else:

        return render(request, 'method_not_allowed.html')
