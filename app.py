import logging
import os
import random
import string

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
    "Букеты, сборные моно",
    "Коробки, композиции",
    "Корзины",
    "Горшечные растения",
    "Горшки, кашпо",
    "Грунт, дренаж, удобрения",
    "Вазы",
    "Игрушки",
    "Шары, хлопушки",
    "Свечи, подсвечники, свечи для торта",
    "Уходовая косметика",
    "Бижутерия",
    "Сувениры",
    "Подарочные пакеты",
    "Упаковка, коробки, корзины",
    "Очки солнцезащитные",
    "Открытки, топперы",
    "Сухоцветы",
    "Шоколад без сахара",
    "Флористическое оформление",
    "Цветы оптом"
]

CATEGORY_DESCRIPTIONS = {
    "Букеты, сборные моно": "Наши букеты — это произведения искусства, созданные из свежих и ярких цветов. Каждый букет собран с любовью и вниманием к деталям, чтобы подарить радость и красоту в любой момент вашей жизни.",
    "Коробки, композиции": "Наши цветочные коробки и композиции — это идеальный способ украсить любое событие. Мы тщательно подбираем цветы и декоративные элементы, чтобы создать неповторимые и стильные композиции.",
    "Корзины": "Корзины с цветами — это не только красивый подарок, но и отличное украшение для интерьера. Мы предлагаем разнообразные корзины, наполненные свежими цветами и зеленью, которые принесут уют и радость в ваш дом.",
    "Горшечные растения": "Создайте зеленый уголок в своем доме с нашими горшечными растениями. Мы предлагаем широкий ассортимент растений в горшках, которые не только украсят ваш интерьер, но и очистят воздух.",
    "Горшки, кашпо": "Наши горшки и кашпо — это стильное решение для ваших комнатных растений. Мы предлагаем разнообразные формы и материалы, чтобы подчеркнуть красоту ваших растений и добавить изюминку в интерьер.",
    "Грунт, дренаж, удобрения": "Для здорового роста ваших растений мы предлагаем качественный грунт, дренаж и удобрения. Наши продукты помогут вашим растениям расти и цвести, создавая зеленый оазис в вашем доме.",
    "Вазы": "Наши вазы — это не только функциональные, но и декоративные элементы интерьера. Мы предлагаем широкий выбор ваз различных форм и материалов, чтобы подчеркнуть красоту ваших цветов.",
    "Игрушки": "Наши мягкие игрушки — это отличный способ подарить радость и уют. Они мягкие, уютные и всегда готовы стать верным другом для детей и взрослых.",
    "Шары, хлопушки": "Сделайте любой праздник незабываемым с нашими яркими шарами и хлопушками. Мы поможем вам создать атмосферу радости и веселья на любом мероприятии.",
    "Свечи, подсвечники, свечи для торта": "Наши свечи и подсвечники создадут уютную атмосферу в вашем доме. Мы предлагаем разнообразные формы и ароматы свечей, а также свечи для торта, чтобы сделать любой момент особенным.",
    "Уходовая косметика": "Побалуйте себя и своих близких нашей уходовой косметикой. Мы предлагаем только лучшие средства для ухода за кожей, которые помогут вам чувствовать себя уверенно и красиво.",
    "Бижутерия": "Дополните свой образ стильной бижутерией. Мы предлагаем широкий выбор украшений, которые подчеркнут вашу индивидуальность и добавят изюминку в ваш гардероб.",
    "Сувениры": "Наши сувениры — это маленькие частички памяти, которые всегда будут напоминать вам о приятных моментах. Мы предлагаем уникальные и оригинальные сувениры для любого случая.",
    "Подарочные пакеты": "Сделайте ваш подарок особенным с нашими подарочными пакетами. Мы предлагаем широкий выбор упаковки, чтобы ваш подарок выглядел по-настоящему празднично.",
    "Упаковка, коробки, корзины": "Наши упаковки, коробки и корзины помогут вам создать идеальный подарок. Мы предлагаем разнообразные варианты упаковки, чтобы подчеркнуть уникальность вашего подарка.",
    "Очки солнцезащитные": "Защитите свои глаза стильно с нашими солнцезащитными очками. Мы предлагаем широкий выбор моделей и цветов, чтобы подчеркнуть ваш индивидуальный стиль.",
    "Открытки, топперы": "Наши открытки и топперы помогут вам выразить свои чувства и сделать любой подарок особенным. Мы предлагаем разнообразные дизайны для любого случая.",
    "Сухоцветы": "Сухоцветы — это элегантное и долговечное украшение для вашего дома. Мы предлагаем широкий ассортимент сухоцветов, которые сохранят свою красоту на долгие годы.",
    "Шоколад без сахара": "Побалуйте себя вкусным и полезным шоколадом без сахара. Наш шоколад — это идеальное сочетание вкуса и здоровья, которое подойдет для любого случая.",
    "Флористическое оформление": "Наши флористы готовы воплотить в жизнь любые ваши идеи по оформлению мероприятий. Мы создаем уникальные флористические композиции, которые сделают любое событие незабываемым.",
    "Цветы оптом": "Для тех, кто занимается бизнесом, мы предлагаем оптовые поставки свежих цветов. Наши цветы всегда высокого качества и готовы украсить любое мероприятие или интерьер."}


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
    total_price = sum(item['price'] for item in cart_items)  # Используем ключ 'price'

    return render_template('index.html', grouped_flowers=grouped_flowers, categories=categories_with_flowers,
                           categories_description=CATEGORY_DESCRIPTIONS, cart_items=cart_items, total_price=total_price)


@app.route('/flower/<int:flower_id>')
def flower(flower_id):
    flower = models.get_flower(flower_id)
    image_paths = flower[4].split(',')  # Разделяем строку путей на массив
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] for item in cart_items)  # Используем ключ 'price'
    return render_template('product.html', flower=flower, image_paths=image_paths, total_price=total_price)



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
    flower = models.get_flower(flower_id)
    if 'cart' not in session:
        session['cart'] = []

    # Преобразуем кортеж в словарь и добавляем количество
    flower_dict = {
        'id': flower[0],
        'name': flower[1],
        'description': flower[2],
        'price': flower[3],
        'image_paths': flower[4],
        'quantity': 1  # Добавляем количество
    }

    # Проверяем, есть ли уже такой товар в корзине
    for item in session['cart']:
        if item['id'] == flower_id:
            item['quantity'] += 1  # Увеличиваем количество, если товар уже в корзине
            break
    else:
        session['cart'].append(flower_dict)  # Добавляем новый товар в корзину

    session.modified = True
    flash('Товар добавлен в корзину', 'success')
    return redirect("/flower/" + str(flower_id))


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session.pop('cart', None)
    return jsonify(success=True)


@app.route('/get_cart')
@app.route('/get_cart')
def get_cart():
    cart_items = session.get('cart', [])
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return jsonify(cart=cart_items, total_price=total_price)


@app.route('/remove_from_cart/<int:flower_id>', methods=['POST'])
def remove_from_cart(flower_id):
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if item['id'] != flower_id]
        session.modified = True
        return jsonify(success=True)
    return jsonify(success=False)


@app.route('/admin_panel')
def admin_panel():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    return render_template('admin.html')


@app.route('/submit_order', methods=['POST'])
def submit_order():
    name = request.form['name']
    phone = request.form['phone']
    promo_code = request.form.get('promo_code', '')
    cart = session.get('cart', [])
    cart_items = [f"{item['name']} - {item['quantity']} шт. на {item['price'] * item['quantity']} руб." for item in cart]
    cart_items_str = "\n".join(cart_items)
    total_price = sum([item['price'] * item['quantity'] for item in cart])
    message = f"Новый заказ:\n\nФИО: {name}\nТелефон: {phone}\n\nТовары:\n{cart_items_str}\n------------------------------------\n\nСумма: {total_price} руб."

    # Check the promo code
    promo_data = models.get_promo_code(promo_code)
    if promo_data and models.use_promo_code(promo_code):
        discount = promo_data['discount']
        total_price_new = total_price * (1 - discount / 100)  # Apply the discount
        message += f"\n\nПосле применения промокода на {discount}% - стоимость: {total_price_new}"

    # Send the message via requests
    payload = {'chat_id': TELEGRAM_USERNAME, 'text': message}
    response = requests.post(TELEGRAM_API_URL, data=payload)
    # Log the response
    logging.info(f"Response status code: {response.status_code}")
    logging.info(f"Response text: {response.text}")

    if response.status_code == 200:
        flash('Заказ отправлен', 'success')
        return jsonify(success=True)
    else:
        flash('Заказ не отправлен. Произошла ошибка', 'error')
        return jsonify(success=False, error=response.text), 500


@app.route('/update_cart_quantity', methods=['POST'])
def update_cart_quantity():
    data = request.get_json()
    flower_id = data.get('flowerId')
    quantity = data.get('quantity')

    if 'cart' in session:
        for item in session['cart']:
            print(flower_id)
            if item['id'] == flower_id:
                item['quantity'] = quantity
                session.modified = True
                break

    return jsonify(success=True)


@app.route('/create_promo_code', methods=['GET', 'POST'])
def create_promo_code():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        discount = int(request.form['discount'])
        uses_left = int(request.form['uses_left'])
        promo_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        promo_codes = models.load_promo_codes()
        promo_codes['promo_codes'][promo_code] = {'discount': discount, 'uses_left': uses_left}
        models.save_promo_codes(promo_codes)
        return render_template('create_promo_code.html', promo_code=promo_code, discount=discount, uses_left=uses_left)

    return render_template('create_promo_code.html')


@app.route('/check_promo_code', methods=['POST'])
def check_promo_code():
    promo_code = request.form.get('promo_code')
    promo_data = models.get_promo_code(promo_code)
    if promo_data and promo_data['uses_left'] > 0:
        return jsonify(valid=True)
    else:
        return jsonify(valid=False)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == '64678892':
            session['admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Неверный пароль')
    return render_template('admin_login.html')


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
