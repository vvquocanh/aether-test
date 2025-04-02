from django.urls import path

from .views import (
    main_view,
    calculation_view
)

urlpatterns = [
    path('', main_view, name='main'),
    path('calculate', calculation_view, name='calculation' )
]