from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
import os
import models
import telegram

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на свой секретный ключ
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Настройки Telegram
TELEGRAM_TOKEN = '7436726184:AAEpRkFBNMfT63moNvD7MCRbXZ9a2rvq6lo'
TELEGRAM_CHAT_ID = '754086992'
bot = telegram.Bot(token=TELEGRAM_TOKEN)

@app.route('/')
def index():
    flowers = models.get_flowers()
    return render_template('index.html', flowers=flowers)

@app.route('/flower/<int:flower_id>')
def flower(flower_id):
    flower = models.get_flower(flower_id)
    return render_template('product.html', flower=flower)

@app.route('/add', methods=['GET', 'POST'])
def add_flower():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
        else:
            image_path = None
        models.add_flower(name, description, price, image_path)
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/add_to_cart/<int:flower_id>')
def add_to_cart(flower_id):
    flower = models.get_flower(flower_id)
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(flower)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session.get('cart', []))

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/submit_order', methods=['POST'])
def submit_order():
    name = request.form['name']
    phone = request.form['phone']
    cart = session.get('cart', [])
    cart_items = [f"{item[1]} - {item[3]} руб." for item in cart]
    cart_items_str = "\n".join(cart_items)

    message = f"Новый заказ:\n\nИмя: {name}\nТелефон: {phone}\n\nТовары:\n{cart_items_str}"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

    return jsonify(success=True)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    models.init_db()
    app.run(debug=True)
