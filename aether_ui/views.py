from django.shortcuts import render
from aether_electricity.views import (calculate_cost_formula_1, calculate_cost_formula_2)

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
    #elif request.method == 'PUT':
        data = request.PUT
    else:

        return render(request, 'method_not_allowed.html')
