from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re

app = Flask(__name__)

# Kirana Inventory & Pricing (kg)
STOCK = {
    'atta': {'qty': 150, 'cost': 45, 'sell': 79},
    'rice': {'qty': 200, 'cost': 38, 'sell': 52},
    'dal': {'qty': 98, 'cost': 72, 'sell': 98}
}

# Track customer orders
orders = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    from_num = request.values.get('From', '')
    incoming_msg = request.values.get('Body', '').lower().strip()
    
    # Initialize customer
    if from_num not in orders:
        orders[from_num] = []
    
    # Stock check
    if 'dal' in incoming_msg or 'dhal' in incoming_msg:
        item = 'dal'
        profit = STOCK[item]['sell'] - STOCK[item]['cost']
        msg = f"🍛 Dal: {STOCK[item]['qty']}kg left\n💰 Sell ₹{STOCK[item]['sell']}/kg | Buy ₹{STOCK[item]['cost']}/kg\n💵 Profit ₹{profit}/kg"
        
    elif 'rice' in incoming_msg:
        item = 'rice'
        profit = STOCK[item]['sell'] - STOCK[item]['cost']
        msg = f"🍚 Rice: {STOCK[item]['qty']}kg left\n💰 Sell ₹{STOCK[item]['sell']}/kg | Buy ₹{STOCK[item]['cost']}/kg\n💵 Profit ₹{profit}/kg"
        
    elif 'atta' in incoming_msg:
        item = 'atta'
        profit = STOCK[item]['sell'] - STOCK[item]['cost']
        msg = f"🫓 Atta: {STOCK[item]['qty']}kg left\n💰 Sell ₹{STOCK[item]['sell']}/kg | Buy ₹{STOCK[item]['cost']}/kg\n💵 Profit ₹{profit}/kg"
        
    # Profit summary + low stock
    elif 'profit' in incoming_msg:
        msg = "💰 GROSS PROFITS:\n"
        low_stock = []
        for item, data in STOCK.items():
            profit = data['sell'] - data['cost']
            msg += f"• {item.title()}: ₹{profit}/kg ({data['qty']}kg left)\n"
            if data['qty'] < 30:
                low_stock.append(item.title())
        if low_stock:
            msg += f"\n⚠️ LOW STOCK: {', '.join(low_stock)}"
    
    # Bill total
    elif 'total' in incoming_msg or 'bill' in incoming_msg:
        if orders[from_num]:
            total = sum(STOCK[item]['sell'] * qty for item, qty in orders[from_num])
            profit = sum((STOCK[item]['sell'] - STOCK[item]['cost']) * qty for item, qty in orders[from_num])
            msg = f"🧾 YOUR BILL:\n"
            for item, qty in orders[from_num]:
                cost = STOCK[item]['sell'] * qty
                msg += f"• {item.title()}: {qty}kg @ ₹{STOCK[item]['sell']} = ₹{cost}\n"
            msg += f"\n💰 TOTAL: ₹{total}\n💵 YOUR PROFIT: ₹{profit}"
        else:
            msg = "🛒 Cart empty. Add: 'order atta 10'"
    
    # Add to cart
    elif incoming_msg.startswith('order '):
        parts = incoming_msg.split()
        if len(parts) >= 3 and parts[1] in STOCK:
            try:
                qty = float(parts[2])
                item = parts[1]
                if STOCK[item]['qty'] >= qty:
                    orders[from_num].append((item, qty))
                    STOCK[item]['qty'] -= qty
                    msg = f"✅ Added {qty}kg {item.title()}\n📦 Stock left: {STOCK[item]['qty']}kg"
                else:
                    msg = f"❌ Only {STOCK[item]['qty']}kg left"
            except:
                msg = "❌ Format: 'order atta 10'"
        else:
            msg = "❌ Items: atta, rice, dal"
    
    elif incoming_msg == 'clear':
        orders[from_num] = []
        msg = "🗑️ Cart cleared"
        
    elif incoming_msg == 'yes':
        orders[from_num] = []
        msg = "✅ Order confirmed! Delivery tomorrow.\n💰 UPI ready?"
    
    else:
        msg = """🏪 KIRANA BOT:
• dal/rice/atta → Stock + Profit
• profit → All profits + low stock
• order atta 10 → Add to cart
• total → Calculate bill + YOUR profit
• clear → Empty cart"""
    
    resp = MessagingResponse()
    resp.message(msg)
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)

