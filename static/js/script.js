document.addEventListener('DOMContentLoaded', function () {
    const filterApply = document.querySelector('.filter-apply');
    const categoryFilter = document.getElementById('categoryFilter');
    const brandFilter = document.getElementById('brandFilter');
    const minRange = document.getElementById('minPriceRange');
    const maxRange = document.getElementById('maxPriceRange');
    const minPriceLabel = document.getElementById('minPriceLabel');
    const maxPriceLabel = document.getElementById('maxPriceLabel');

    if (filterApply && categoryFilter && brandFilter && minRange && maxRange) {
        filterApply.addEventListener('click', function () {
            const params = new URLSearchParams(window.location.search);
            const category = categoryFilter.value;
            const brand = brandFilter.value;
            const min = minRange.value;
            const max = maxRange.value;

            params.set('category', category);
            params.set('brand', brand);
            params.set('min_price', Math.min(min, max));
            params.set('max_price', Math.max(min, max));

            window.location.href = `${window.location.pathname}?${params.toString()}`;
        });
    }

    if (minRange && maxRange && minPriceLabel && maxPriceLabel) {
        const refreshRangeLabels = () => {
            const minValue = Math.min(Number(minRange.value), Number(maxRange.value));
            const maxValue = Math.max(Number(minRange.value), Number(maxRange.value));
            minRange.value = minValue;
            maxRange.value = maxValue;
            minPriceLabel.textContent = `${minValue} ₽`;
            maxPriceLabel.textContent = `${maxValue} ₽`;
        };

        minRange.addEventListener('input', refreshRangeLabels);
        maxRange.addEventListener('input', refreshRangeLabels);
    }

    document.querySelectorAll('.qty-btn').forEach(function (button) {
        button.addEventListener('click', function () {
            const input = button.parentElement.querySelector('input[name="quantity"]');
            if (!input) return;
            const current = Number(input.value) || 1;
            const next = button.dataset.action === 'plus' ? current + 1 : Math.max(1, current - 1);
            input.value = next;
        });
    });

    setTimeout(function () {
        const flash = document.querySelector('.flash-message');
        if (flash) {
            flash.style.opacity = '0';
            flash.style.transition = 'opacity 0.5s ease';
            setTimeout(() => flash.remove(), 500);
        }
    }, 2500);
});
