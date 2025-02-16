// Получаем элементы
var cartModal = document.getElementById("cart-modal");
var orderModal = document.getElementById("order-modal");
var cartBtn = document.getElementById("cart-button");
var checkoutBtn = document.getElementById("checkout-button");
var clearCartBtn = document.getElementById("clear-cart-button");
var closeBtns = document.getElementsByClassName("close-button");
var cartItems = document.getElementById("cart-items");
var totalPrice = document.getElementById("total-price");
var cartCount = document.getElementById("cart-count");

// Открываем модальное окно корзины при нажатии на кнопку
cartBtn.onclick = function () {
    cartModal.style.display = "block";
    updateCart();
}

// Открываем модальное окно оформления заказа при нажатии на кнопку "Оформить заказ"
checkoutBtn.onclick = function () {
    cartModal.style.display = "none";
    orderModal.style.display = "block";
}

// Закрываем модальное окно при нажатии на крестик
for (var i = 0; i < closeBtns.length; i++) {
    closeBtns[i].onclick = function () {
        cartModal.style.display = "none";
        orderModal.style.display = "none";
        modalBackdrop.style.display = "none";
    }
}

// Обработка отправки формы оформления заказа
document.getElementById("order-form").onsubmit = function (event) {
    event.preventDefault();
    var name = document.getElementById("name").value;
    var phone = document.getElementById("phone").value;
    var promo_code = document.getElementById("promo_code").value;

    fetch('/submit_order', {
        method: 'POST', headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }, body: new URLSearchParams({
            name: name, phone: phone, promo_code: promo_code
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
                            location.replace("/");
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
    cartItems.addEventListener('click', function (event) {
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
    clearCartBtn.addEventListener('click', function (event) {
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

});

// Функция для обновления корзины

function updateCart() {
    fetch('/get_cart')
        .then(response => response.json())
        .then(data => {
            const cartItems = document.getElementById('cart-items');
            const totalPrice = document.getElementById('total-price');
            const cartCount = document.getElementById('cart-count');

            cartItems.innerHTML = '';
            totalPrice.textContent = data.total_price;
            cartCount.textContent = data.cart.length;

            data.cart.forEach(item => {
                const cartItem = document.createElement('div');
                cartItem.classList.add('cart-item');
                cartItem.setAttribute('data-flower-id', item.id);
                cartItem.innerHTML = `
                    <div class="cart-item" data-flower-id="${item.id}">
                    <img src="../${item.image_paths.split(',')[0]}" alt="${item.name}">
                    <div class="cart-item-info">
                        <div class="cart-item-name">${item.name}</div>
                        <div class="cart-item-price">${item.price} руб.</div>
                        <div class="cart-item-quantity">
                            <button class="decrease-quantity">-</button>
                            <span class="quantity">${item.quantity}</span>
                            <button class="increase-quantity">+</button>
                        </div>
                    </div>
                    <div class="remove-from-cart-mark">&times;</div>
                </div>
                <div style="border-bottom: 1px solid #000">   </div>
                `;
                cartItems.appendChild(cartItem);
            });
            const checkoutButton = document.getElementById('checkout-button');
            checkoutButton.disabled = data.cart.length === 0;
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
document.getElementById("order-form").onsubmit = function (event) {
    event.preventDefault();
    var name = document.getElementById("name").value;
    var phone = document.getElementById("phone").value;
    var promo_code = document.getElementById("promo_code").value;

    fetch('/submit_order', {
        method: 'POST', headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        }, body: new URLSearchParams({
            name: name, phone: phone, promo_code: promo_code
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Clear the cart after a successful order
                fetch('/clear_cart', {
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updateCart();
                            location.reload();
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
document.getElementById("apply-promo-code").onclick = function () {
    var promo_code = document.getElementById("promo_code").value;
    var promoCodeMessage = document.getElementById("promo-code-message");

    fetch('/check_promo_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            promo_code: promo_code
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                promoCodeMessage.textContent = "Промокод действителен.";
                promoCodeMessage.style.color = "green";
            } else {
                promoCodeMessage.textContent = "Неверный промокод или он уже использован.";
                promoCodeMessage.style.color = "red";
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
};

document.addEventListener('DOMContentLoaded', function () {
    cartItems.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-from-cart-mark')) {
            var flowerId = parseInt(event.target.parentElement.getAttribute('data-flower-id'));
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
        } else if (event.target.classList.contains('increase-quantity') || event.target.classList.contains('decrease-quantity')) {
            var flowerId = parseInt(event.target.closest('.cart-item').getAttribute('data-flower-id'));
            var quantityElement = event.target.closest('.cart-item-quantity').querySelector('.quantity');
            var quantity = parseInt(quantityElement.textContent);

            if (event.target.classList.contains('increase-quantity')) {
                quantity += 1;
            } else if (event.target.classList.contains('decrease-quantity') && quantity > 1) {
                quantity -= 1;
            }

            fetch('/update_cart_quantity', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({flowerId: flowerId, quantity: quantity})
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        quantityElement.textContent = quantity;
                        updateCart();
                    } else {
                        alert("Произошла ошибка при обновлении количества товара.");
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
    });
});
document.addEventListener('DOMContentLoaded', function () {
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('main-image');
    const leftArrow = document.querySelector('.thumbnail-arrow.left');
    const rightArrow = document.querySelector('.thumbnail-arrow.right');
    let currentIndex = 0;

    // Обновление основного изображения
    function updateMainImage() {
        mainImage.src = thumbnails[currentIndex].src;
    }

    // Обработчик клика на миниатюру
    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', function () {
            currentIndex = index;
            updateMainImage();
        });
    });

    // Обработчик клика на левую стрелку
    leftArrow.addEventListener('click', function () {
        currentIndex = (currentIndex - 1 + thumbnails.length) % thumbnails.length;
        updateMainImage();
    });

    // Обработчик клика на правую стрелку
    rightArrow.addEventListener('click', function () {
        currentIndex = (currentIndex + 1) % thumbnails.length;
        updateMainImage();
    });
});

