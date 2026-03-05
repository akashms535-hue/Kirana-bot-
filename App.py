from flask import Flask, request
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def kirana_ai():
    msg = request.values.get('Body', '').lower()
    if 'bill' in msg:
        return "<Response><Message>🛒 Bill: ₹130\nPay ₹79?</Message></Response>"
    elif 'stock' in msg:
        return "<Response><Message>DAL: 12kg left</Message></Response>"
    else:
        return "<Response><Message>Kirana AI!\nStock dal?</Message></Response>"

app.run(host='0.0.0.0', port=10000)
