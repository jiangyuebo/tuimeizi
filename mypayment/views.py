from django.shortcuts import render


# Create your views here.
def my_payment(request):
    return render(request, 'mypayment/payment.html')
