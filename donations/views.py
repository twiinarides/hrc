from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Donation
from core.models import SiteSetting
from core.notifications import notify_admin


def donate_view(request):
    site = SiteSetting.objects.first()
    if request.method == 'POST':
        name = request.POST.get('donor_name', 'Anonymous')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        method = request.POST.get('payment_method')
        ref = request.POST.get('transaction_reference')

        donation = Donation.objects.create(
            donor_name=name,
            email=email,
            phone=phone,
            amount=amount,
            payment_method=method,
            transaction_reference=ref
        )

        notify_admin(
            notification_type='donation',
            title=f"New Donation: UGX {amount} from {name}",
            message=f"Donor: {name}\nAmount: UGX {amount}\nMethod: {method}\nPhone: {phone}\nRef: {ref}",
            link=f"/admin/donations/donation/{donation.id}/change/"
        )

        messages.success(request, "Thank you for your generous donation! Our team will verify and acknowledge your contribution.")
        return redirect('donate')

    return render(request, 'donations/donate.html', {'site': site})
