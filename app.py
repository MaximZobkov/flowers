import logging
import os

import requests
from PIL import Image
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename

import models

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Замените на свой секретный ключ
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Настройки Telegram
TELEGRAM_TOKEN = '7436726184:AAEpRkFBNMfT63moNvD7MCRbXZ9a2rvq6lo'  # Замените на ваш токен API
TELEGRAM_USERNAME = '754086992'  # Замените на имя пользователя, например, @myflowerbot
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Новые категории товаров
CATEGORIES = [
    "Букеты, композиции, корзины",
    "Комнатные растения",
    "Грунт, удобрения",
    "Кашпо, вазы",
    "Шары и товары для праздника",
    "Мягкие игрушки",
    "Аксессуары, очки, бижутерия",
    "Сувениры",
    "Премиум уходовая косметика",
    "Подарочные пакеты, открытки",
    "Флористическое оформление",
    "Цветы оптом"
]

CATEGORY_DESCRIPTIONS = {
    "Букеты, композиции, корзины": "Наши букеты, композиции и корзины — это искусство, созданное из живых цветов. Каждый букет уникален и собран с любовью, чтобы подарить радость и красоту в любой момент вашей жизни.",
    "Комнатные растения, грунт, удобрения, кашпо, вазы": "Создайте уют в вашем доме с нашими комнатными растениями. Мы предлагаем широкий ассортимент растений, грунтов, удобрений, кашпо и ваз, чтобы ваш дом всегда был зеленым и полным жизни.",
    "Шары и товары для праздника": "Сделайте любой праздник незабываемым с нашими яркими шарами и товарами для праздника. Мы поможем вам создать атмосферу радости и веселья на любом мероприятии.",
    "Мягкие игрушки": "Наши мягкие игрушки — это не только забава для детей, но и отличный подарок для любого возраста. Они мягкие, уютные и всегда готовы подарить улыбку.",
    "Аксессуары, очки, бижутерия": "Дополните свой образ стильными аксессуарами, очками и бижутерией. Мы предлагаем широкий выбор изделий, которые подчеркнут вашу индивидуальность и добавят изюминку в ваш гардероб.",
    "Сувениры": "Наши сувениры — это маленькие частички памяти, которые всегда будут напоминать вам о приятных моментах. Мы предлагаем уникальные и оригинальные сувениры для любого случая.",
    "Премиум уходовая косметика": "Побалуйте себя и своих близких нашей премиум уходовой косметикой. Мы предлагаем только лучшие средства для ухода за кожей, которые помогут вам чувствовать себя уверенно и красиво.",
    "Подарочные пакеты, открытки": "Сделайте ваш подарок особенным с нашими подарочными пакетами и открытками. Мы предлагаем широкий выбор упаковки и открыток, чтобы ваш подарок выглядел по-настоящему празднично.",
    "Флористическое оформление": "Наши флористы готовы воплотить в жизнь любые ваши идеи по оформлению мероприятий. Мы создаем уникальные флористические композиции, которые сделают любое событие незабываемым.",
    "Цветы оптом": "Для тех, кто занимается бизнесом, мы предлагаем оптовые поставки свежих цветов. Наши цветы всегда высокого качества и готовы украсить любое мероприятие или интерьер."
}


def crop_image(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        width, height = img.size
        if width != height:
            if height > width:
                top = (height - width) / 2
                bottom = (height + width) / 2
                left = 0
                right = width
            else:
                left = (width - height) / 2
                right = (width + height) / 2
                top = 0
                bottom = height
            img = img.crop((left, top, right, bottom))
        img.save(image_path)

@app.route('/')
def index():
    category = request.args.get('category')
    categories_with_flowers = models.get_categories_with_flowers()
    if category:
        flowers = models.get_flowers_by_category(category)
        grouped_flowers = {category: flowers}
    else:
        grouped_flowers = models.get_flowers_grouped_by_category()

    cart_items = session.get('cart', [])
    total_price = sum(item[3] for item in cart_items)

    return render_template('index.html', grouped_flowers=grouped_flowers, categories=categories_with_flowers,
                           categories_description=CATEGORY_DESCRIPTIONS, cart_items=cart_items, total_price=total_price)

@app.route('/flower/<int:flower_id>')
def flower(flower_id):
    flower = models.get_flower(flower_id)
    cart_items = session.get('cart', [])
    total_price = sum(item[3] for item in cart_items)
    return render_template('product.html', flower=flower, total_price=total_price)

@app.route('/add', methods=['GET', 'POST'])
def add_flower():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        image_files = request.files.getlist('image')
        image_paths = []
        for image in image_files:
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                crop_image(image_path)  # Обрезка изображения до соотношения 1:1
                image_paths.append(image_path)
        image_paths_str = ','.join(image_paths)
        models.add_flower(name, description, price, image_paths_str, category)
        return redirect(url_for('admin_panel'))
    return render_template('add.html', categories=CATEGORIES)

@app.route('/add_to_cart/<int:flower_id>')
def add_to_cart(flower_id):
    global flower_cart
    flower = models.get_flower(flower_id)
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(flower)
    session.modified = True
    flash('Товар добавлен в корзину', 'success')
    return redirect(url_for('index'))



@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return jsonify(success=True)


@app.route('/get_cart')
def get_cart():
    cart_with_quantities = []
    flower_cart = {}
    cart_items = session.get('cart', [])
    total_price = 0
    for item in cart_items:
        flower_cart[item[0]] = flower_cart.get(item[0], 0) + 1
    for item in set(cart_items):
        cart_with_quantities.append({
            'id': item[0],
            'name': item[1],
            'price': item[3],
            'image': item[4].split(',')[0] if item[4] else None,
            'quantity': flower_cart.get(item[0], 0)
        })
        total_price += item[3] * flower_cart.get(item[0])
    return jsonify(cart=cart_with_quantities, total_price=total_price)




@app.route('/remove_from_cart/<int:flower_id>', methods=['POST'])
def remove_from_cart(flower_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item[0] != flower_id]
        session.modified = True
        return jsonify(success=True)
    return jsonify(success=False)


@app.route('/submit_order', methods=['POST'])
def submit_order():
    name = request.form['name']
    phone = request.form['phone']
    cart = session.get('cart', [])
    cart_items = [f"{item[1]} - {item[3]} руб." for item in cart]
    cart_items_str = "\n".join(cart_items)
    total_price = sum([int(item.split()[-2]) for item in cart_items])

    message = f"Новый заказ:\n\nФИО: {name}\nТелефон: {phone}\n\nТовары:\n{cart_items_str}\n------------------------------------\n\nСумма: {total_price}"

    # Отправка сообщения через requests
    payload = {
        'chat_id': TELEGRAM_USERNAME,
        'text': message
    }
    response = requests.post(TELEGRAM_API_URL, data=payload)

    # Логирование ответа
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response text: {response.text}")

    if response.status_code == 200:
        return jsonify(success=True)
    else:
        return jsonify(success=False, error=response.text), 500


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'DesFleur2025':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Неверный пароль')
    return render_template('admin_login.html')


@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    return render_template('admin.html')


@app.route('/edit_flower_list')
def edit_flower_list():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    flowers = models.get_flowers()
    return render_template('edit_flower_list.html', flowers=flowers)


@app.route('/edit_flower/<int:flower_id>', methods=['GET', 'POST'])
def edit_flower(flower_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    flower = models.get_flower(flower_id)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        image_files = request.files.getlist('image_paths')
        image_path_old = models.get_path(flower_id)
        image_paths = []
        for image in image_files:
            if image:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                crop_image(image_path)  # Обрезка изображения до соотношения 1:1
                image_paths.append(image_path)
        image_paths_str = ','.join(image_paths)
        if image_paths_str == "":
            image_paths_str = str(image_path_old)[2:-3]
        models.update_flower(flower_id, name, description, price, image_paths_str, category)
        return redirect(url_for('edit_flower_list'))
    return render_template('edit_flower.html', flower=flower, categories=CATEGORIES)


@app.route('/delete_flower_list')
def delete_flower_list():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    flowers = models.get_flowers()
    return render_template('delete_flower_list.html', flowers=flowers)


@app.route('/delete_flower/<int:flower_id>', methods=['POST'])
def delete_flower(flower_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    flower = models.get_flower(flower_id)
    if flower[4]:
        image_paths = flower[4].split(',')
        for image_path in image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
    models.delete_flower(flower_id)
    return redirect(url_for('delete_flower_list'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    models.init_db()
    app.run(debug=True)
