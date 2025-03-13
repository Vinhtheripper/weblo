let menuBtn = document.getElementById("menu-btn");
const navLinks = document.getElementById("nav-links");
const menuBtnIcon = menuBtn.querySelector("i");

menuBtn.addEventListener("click", (e) => {
  navLinks.classList.toggle("open");

  const isOpen = navLinks.classList.contains("open");
  menuBtnIcon.setAttribute("class", isOpen ? "ri-close-line" : "ri-menu-line");
});

navLinks.addEventListener("click", (e) => {
  navLinks.classList.remove("open");
  menuBtnIcon.setAttribute("class", "ri-menu-line");
});

const scrollRevealOption = {
  distance: "50px",
  origin: "bottom",
  duration: 1000,
};
ScrollReveal().reveal(".container__left h1", {
  ...scrollRevealOption,
});
ScrollReveal().reveal(".container__left .container__btn", {
  ...scrollRevealOption,
  delay: 500,
});

ScrollReveal().reveal(".container__right h4", {
  ...scrollRevealOption,
  delay: 2000,
});
ScrollReveal().reveal(".container__right h2", {
  ...scrollRevealOption,
  delay: 2500,
});
ScrollReveal().reveal(".container__right h3", {
  ...scrollRevealOption,
  delay: 2500,
});
ScrollReveal().reveal(".container__right p", {
  ...scrollRevealOption,
  delay: 2500,
});

ScrollReveal().reveal(".container__right .tent-1", {
  duration: 1000,
  delay: 3000,
});
ScrollReveal().reveal(".container__right .tent-2", {
  duration: 1000,
  delay: 3500,
});

ScrollReveal().reveal(".location", {
  ...scrollRevealOption,
  origin: "left",
  delay: 3000,
});

ScrollReveal().reveal(".socials span", {
  ...scrollRevealOption,
  origin: "top",
  delay: 3500,
  interval: 500,
});

document.addEventListener("DOMContentLoaded", function () {
        const openSearch = document.getElementById("openSearch");
        const overlay = document.getElementById("overlay");
        const searchBox = document.getElementById("searchBox");

        // Khi bấm vào icon 🔍 -> Hiện thanh tìm kiếm
        openSearch.addEventListener("click", function (event) {
            event.stopPropagation(); // Ngăn chặn sự kiện lan ra ngoài
            overlay.classList.add("active");
            searchBox.focus();
        });

        // Khi bấm ra ngoài overlay -> Ẩn thanh tìm kiếm
        overlay.addEventListener("click", function (event) {
            if (event.target === overlay) {
                overlay.classList.remove("active");
            }
        });

        // Ngăn chặn việc bấm vào ô tìm kiếm mà bị tắt
        searchBox.addEventListener("click", function (event) {
            event.stopPropagation();
        });
    });
document.addEventListener("DOMContentLoaded", function () {
    let stars = document.querySelectorAll(".rating .star");
    let ratingInput = document.getElementById("rating-value");

    stars.forEach(star => {
        star.addEventListener("click", function () {
            let value = this.getAttribute("data-value");
            ratingInput.value = value;

            // Xóa class "rated" của tất cả sao trước khi cập nhật
            stars.forEach(s => s.classList.remove("rated"));

            // Đánh dấu các sao được chọn
            for (let i = 0; i < value; i++) {
                stars[i].classList.add("rated");
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    function setupScrollButtons(containerId, prevBtnId, nextBtnId) {
        const scrollContainer = document.getElementById(containerId);
        const prevButton = document.getElementById(prevBtnId);
        const nextButton = document.getElementById(nextBtnId);

        if (!scrollContainer || !prevButton || !nextButton) {
            console.error("Không tìm thấy phần tử cần thiết:", { scrollContainer, prevButton, nextButton });
            return;
        }

        nextButton.addEventListener("click", () => {
            console.log(`Next button for ${containerId} clicked!`);
            scrollContainer.scrollBy({ left: 300, behavior: "smooth" });
        });

        prevButton.addEventListener("click", () => {
            console.log(`Prev button for ${containerId} clicked!`);
            scrollContainer.scrollBy({ left: -300, behavior: "smooth" });
        });
    }

    // Setup cho COMBO DEALS
    setupScrollButtons("scrollContainer_combo", "prev_combo", "next_combo");

    // Setup cho BEST SELLER
    setupScrollButtons("scrollContainer_digital", "prev_digital", "next_digital");
});

let countdownInterval;

function showQR(method) {
    const qrImage = document.getElementById('qr-image');
    const paymentMethodInput = document.getElementById('payment_method');
    const qrOverlay = document.getElementById('qr-overlay');
    const countdownText = document.getElementById('countdown-timer');

    paymentMethodInput.value = method;

    if (method === 'cash') {
        qrOverlay.classList.add('d-none');
        return;
    }

    if (method === 'momo') {
        qrImage.src = "/static/app/images/momo_qr.png";
    } else if (method === 'vnpay') {
        qrImage.src = "/static/app/images/vnpay_qr.png";
    } else if (method === 'bank') {
        qrImage.src = "/static/app/images/banking_qr.png";
    }

    qrOverlay.classList.remove('d-none');
    document.getElementById('payment-alert').classList.add('d-none');

    // Khởi động bộ đếm ngược
    let timeLeft = 15;
    countdownText.innerText = `QR will close in ${timeLeft}s`;

    clearInterval(countdownInterval);
    countdownInterval = setInterval(() => {
        timeLeft--;
        countdownText.innerText = `QR will close in ${timeLeft}s`;

        if (timeLeft <= 0) {
            clearInterval(countdownInterval);
            hideQR();
        }
    }, 1000);
}

function hideQR() {
    document.getElementById('qr-overlay').classList.add('d-none');
    clearInterval(countdownInterval);
}

document.getElementById('qr-overlay').addEventListener('click', function(event) {
    if (event.target === this) {
        hideQR();
    }
});

function validatePaymentMethod() {
    const paymentMethodInput = document.getElementById('payment_method');
    const paymentAlert = document.getElementById('payment-alert');

    if (!paymentMethodInput.value) {
        paymentAlert.classList.remove('d-none');
        return false;
    }
    return true;
}

document.addEventListener("DOMContentLoaded", function() {
  const swup = new Swup();
  swup.hooks.on('contentReplaced', function() {
    console.log("Nội dung trang đã thay đổi, khởi động lại script...");
    initSearchFunction();
  });

  function initSearchFunction() {
    const searchBtn = document.getElementById("openSearch");
    const overlay = document.getElementById("overlay");

    if (searchBtn) {
      searchBtn.addEventListener("click", function () {
        overlay.style.display = "block";
      });
    }
  }

  initSearchFunction();  // Chạy lần đầu khi load trang
});


