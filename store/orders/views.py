import stripe
import json
from http import HTTPStatus

from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from common.views import TitleMixin
from orders.forms import OrderForm

stripe.api_key = settings.STRIPE_SECRET_KEY

class SuccessTemplateView(TitleMixin, TemplateView):
    template_name = "orders/success.html"
    title = "Store - Спасибо за заказ!"

class CanceledTemplateVIew(TemplateView):
    template_name = "orders/canceled.html"

class OrderCreateView(TitleMixin, CreateView):
    template_name = "orders/order-create.html"
    form_class = OrderForm
    success_url = reverse_lazy("orders:order_success")
    title = "Store - Оформление заказа"

    def post(self, request, *args, **kwargs):
        super(OrderCreateView, self).post(request, *args, **kwargs)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    "price": "price_1Q0f6yP37XViIZAKLuUHM2Wi",
                    "quantity": 1,
                },
            ],
            metadata={'order_id':self.object.id},
            mode="payment",
            success_url="{}{}".format(settings.DOMAIN_NAME, reverse("orders:order_success")),
            cancel_url="{}{}".format(settings.DOMAIN_NAME, reverse("orders:order_canceled")),
        )

        return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        return super(OrderCreateView, self).form_valid(form)

# Using Django
@csrf_exempt
def stripe_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = stripe.Webhook.construct_event(
      payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )
    print("Event constructed successfully:", event)
  except ValueError as e:
    # Invalid payload
    print('Error parsing payload: {}'.format(str(e)))
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    print('Error verifying webhook signature: {}'.format(str(e)))
    return HttpResponse(status=400)

  print("Received event:", event['type'])

  if (
          event['type'] == 'checkout.session.completed'
          or event['type'] == 'checkout.session.async_payment_succeeded'
  ):
      session = event['data']['object']
      fulfill_checkout(session)

  return HttpResponse(status=200)

def fulfill_checkout(session):
    order_id = int(session.metadata.order_id)
    print("Fulfilling Checkout Session")

  # TODO: Make this function safe to run multiple times,
  # even concurrently, with the same session ID

  # TODO: Make sure fulfillment hasn't already been
  # peformed for this Checkout Session

  # Retrieve the Checkout Session from the API with line_items expanded
  # checkout_session = stripe.checkout.Session.retrieve(
  #   session_id,
  #   expand=['line_items'],
  # )
  #
  # # Check the Checkout Session's payment_status property
  # # to determine if fulfillment should be peformed
  # if checkout_session.payment_status != 'unpaid':
  #     pass
  #   # TODO: Perform fulfillment of the line items
  #
  #   # TODO: Record/save fulfillment status for this
  #   # Checkout Sessiong order")