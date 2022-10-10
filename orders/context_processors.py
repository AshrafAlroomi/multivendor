
from .models import Order, OrderLine


# def orders_cart_obj(request):
#     if request.user.is_authenticated and not request.user.is_anonymous:
#         if Order.objects.all().filter(user=request.user, is_finished=False):
#             order_context = Order.objects.get(
#                 customer=request.user, is_finished=False)
#             order_details_context = OrderLine.objects.all().filter(order=order_context)
#
#             return {
#                 'order_context': order_context,
#                 "order_details_context": order_details_context,
#             }
#
#     return{
#         "none": "None",
#
#     }
