from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import role_required

from .models import Payment


@login_required
@role_required('patient')
def payment_list(request):
    payments = Payment.objects.filter(appointment__patient__user=request.user).select_related('appointment__doctor__user')
    return render(request, 'payments/payment_list.html', {'payments': payments})


@login_required
@role_required('patient')
def make_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk, appointment__patient__user=request.user)
    if payment.status == Payment.PENDING:
        payment.mark_as_paid()
        messages.success(request, 'Mock payment completed successfully.')
    return redirect('payments:payment_list')
