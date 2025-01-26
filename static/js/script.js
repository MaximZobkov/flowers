// Получаем элементы
var cartModal = document.getElementById("cart-modal");
var orderModal = document.getElementById("order-modal");
var cartBtn = document.getElementById("cart-button");
var checkoutBtn = document.getElementById("checkout-button");
var closeBtns = document.getElementsByClassName("close-button");

// Открываем модальное окно корзины при нажатии на кнопку
cartBtn.onclick = function() {
    cartModal.style.display = "block";
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
        } else {
            alert("Произошла ошибка при отправке заказа.");
        }
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