from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Kirana Inventory (Your Kengeri stock)
STOCK = {
    'dal': {'qty': 98, 'buy': 72, 'sell': 98},
    'atta': {'qty': 150, 'buy': 35, 'sell': 45},
    'rice': {'qty': 200, 'buy': 45, 'sell': 60}
}
cart = {}

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    incoming_msg = request.values.get('Body', '').lower().strip()
    resp = MessagingResponse()
    msg = resp.message()
    
    # Stock check
    if incoming_msg in STOCK:
        item = incoming_msg
        profit = STOCK[item]['sell'] - STOCK[item]['buy']
        msg.body(f"{item.title()}: {STOCK[item]['qty']}kg left, "
                f"Sell ₹{STOCK[item]['sell']}/kg, Profit ₹{profit}/kg")
    
    # Order
    elif incoming_msg.startswith('order '):
        parts = incoming_msg.split()
        if len(parts) == 3:
            item, qty = parts[1], int(parts[2])
            if item in STOCK and STOCK[item]['qty'] >= qty:
                cart[item] = cart.get(item, 0) + qty
                msg.body(f"Added {qty}kg {item} to cart")
            else:
                msg.body("Low stock or invalid item")
    
    # Total
    elif incoming_msg == 'total':
        if cart:
            total = sum(cart[item] * STOCK[item]['sell'] for item in cart)
            profit = sum(cart[item] * (STOCK[item]['sell'] - STOCK[item]['buy']) for item in cart)
            msg.body(f"BILL: ₹{total}\nYOUR PROFIT: ₹{profit}\nReply YES to confirm")
        else:
            msg.body("Cart empty. Try: order atta 10")
    
    # Confirm
    elif incoming_msg == 'yes':
        msg.body("✅ Order confirmed! Send UPI to 9xxxxxxxxx\n"
                f"Total: ₹{sum(cart[item] * STOCK[item]['sell'] for item in cart)}\n"
                "Delivery: Tomorrow 8AM")
        cart.clear()
    
    else:
        msg.body("Kirana Bot Live!\n• dal (stock check)\n• order atta 10\n• total\n• profit")
    
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
