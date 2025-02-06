//Получаем элементы
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

    fetch('/submit_order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            name: name,
            phone: phone
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            orderModal.style.display = "none";
            modalBackdrop.style.display = "none";
            updateCart();
        } else {
            alert("Произошла ошибка при отправке заказа.");
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
            cartItem.setAttribute('data-flower-id', item[0]);
            cartItem.innerHTML = `
                <img src="../${item[4].split(',')[0]}" alt="${item[1]}" style="height: 4em">
                <span class="ml-4">${item[1]}</span>
                <a class="remove-from-cart-mark">&times;</a>
                <span class="cost">${item[3]} руб.</span>
            `;
            cartItems.appendChild(cartItem);
        });
        checkoutBtn.disabled = data.cart.length === 0;
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
