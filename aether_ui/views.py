from django.shortcuts import render
from aether_electricity.views import (calculate_cost_formula_1, calculate_cost_formula_2)

# Create your views here.
def main_view(request):
    if request.method != 'GET':  
        return render(request, 'method_not_allowed.html')
    else:
        return render(request, 'main.html')
    
def calculation_view(request):
    if request.method != 'POST':
        return render(request, 'method_not_allowed.html')
    else:
        data = request.POST
        if 'calculate_formula_1' in data:
            context = calculate_cost_formula_1(data)
            return render(request, 'calculation_method_1.html', context)

        elif 'calculate_formula_2' in data:
            context = calculate_cost_formula_2(data)
            return render(request, 'calculation_method_2.html', context)
        else:
            return render(request, 'method_not_allowed.html')
