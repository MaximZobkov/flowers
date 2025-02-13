// Получаем элементы
var cartModal = document.getElementById("cart-modal");
var orderModal = document.getElementById("order-modal");
var cartBtn = document.getElementById("cart-button");
var checkoutBtn = document.getElementById("checkout-button");
var clearCartBtn = document.getElementById("clear-cart-button");
var closeBtns = document.getElementsByClassName("close-button");
var modalBackdrop = document.getElementById("modal-backdrop");
var cartItems = document.getElementById("cart-items");
var totalPrice = document.getElementById("total-price");
var cartCount = document.getElementById("cart-count");

// Открываем модальное окно корзины при нажатии на кнопку
cartBtn.onclick = function() {
    cartModal.style.display = "block";
    modalBackdrop.style.display = "block";
    updateCart();
}

// Открываем модальное окно оформления заказа при нажатии на кнопку "Оформить заказ"
checkoutBtn.onclick = function() {
    cartModal.style.display = "none";
    orderModal.style.display = "block";
}

// Закрываем модальное окно при нажатии на крестик
for (var i = 0; i < closeBtns.length; i++) {
    closeBtns[i].onclick = function() {
        cartModal.style.display = "none";
        orderModal.style.display = "none";
        modalBackdrop.style.display = "none";
    }
}

// Обработка отправки формы оформления заказа
document.getElementById("order-form").onsubmit = function(event) {
    event.preventDefault();
    var name = document.getElementById("name").value;
    var phone = document.getElementById("phone").value;
    var promo_code = document.getElementById("promo_code").value;

    fetch('/submit_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            name: name,
            phone: phone,
            promo_code: promo_code
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Заказ успешно оформлен!");
            // Очистка корзины после успешного оформления заказа
            fetch('/clear_cart', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCart();
                }
            });
        } else {
            alert("Произошла ошибка при оформлении заказа.");
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}



// Обработка удаления товара из корзины
document.addEventListener('DOMContentLoaded', function () {
    cartItems.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-from-cart-mark')) {
            var flowerId = event.target.parentElement.getAttribute('data-flower-id');
            fetch('/remove_from_cart/' + flowerId, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCart();
                } else {
                    alert("Произошла ошибка при удалении товара из корзины.");
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });

    // Обработка очистки корзины
    clearCartBtn.addEventListener('click', function(event) {
        event.preventDefault();
        fetch('/clear_cart', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCart();
            } else {
                alert("Произошла ошибка при очистке корзины.");
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    // Обработка прокрутки изображений
    var thumbnails = document.querySelectorAll('.thumbnail');
    var mainImage = document.getElementById('main-image');

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function () {
            mainImage.src = this.src;
        });
    });

    // Обработка увеличения изображения при наведении
    var flowerCards = document.querySelectorAll('.flower-card img');

    flowerCards.forEach(flowerCard => {
        flowerCard.addEventListener('mouseover', function () {
            this.style.transform = 'scale(1.1)';
        });

        flowerCard.addEventListener('mouseout', function () {
            this.style.transform = 'scale(1)';
        });
    });

    // Обработка стрелок прокрутки изображений
    var leftArrow = document.querySelector('.thumbnail-arrow.left');
    var rightArrow = document.querySelector('.thumbnail-arrow.right');

    leftArrow.addEventListener('click', function () {
        var currentIndex = Array.from(thumbnails).indexOf(document.querySelector('.thumbnail.active'));
        var newIndex = (currentIndex - 1 + thumbnails.length) % thumbnails.length;
        thumbnails[newIndex].click();
    });

    rightArrow.addEventListener('click', function () {
        var currentIndex = Array.from(thumbnails).indexOf(document.querySelector('.thumbnail.active'));
        var newIndex = (currentIndex + 1) % thumbnails.length;
        thumbnails[newIndex].click();
    });
});

// Функция для обновления корзины
function updateCart() {
    fetch('/get_cart')
    .then(response => response.json())
    .then(data => {
        cartItems.innerHTML = '';
        totalPrice.textContent = data.total_price;
        cartCount.textContent = data.cart.length;
        data.cart.forEach(item => {
            var cartItem = document.createElement('div');
            cartItem.classList.add('cart-item');
            cartItem.setAttribute('data-flower-id', item.id);
            cartItem.innerHTML = `
                <div class="img-carts">
                        <img style="height: 8vh" src="../${item.image}" alt="${item.name}">
                    </div>
                    <div class="name-products" >
                        <span>${item.name} (x${item.quantity})</span>
                    </div>
                    <div class="cost-div">
                        <span class="cost">${item.price * item.quantity}&nbsp</span><span>р.</span>
                    </div>
                        <a class="remove-from-cart-mark">&times;</a>
            `;
            cartItems.appendChild(cartItem);
        });
        checkoutBtn.disabled = data.cart.length === 0;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}



document.addEventListener('DOMContentLoaded', function () {
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('main-image');

    thumbnails.forEach(thumbnail => {
        thumbnail.addEventListener('click', function () {
            mainImage.src = this.src;
        });
    });
});

