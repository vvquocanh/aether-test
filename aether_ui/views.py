from django.shortcuts import render

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
        
        return render(request, 'calculation.html')