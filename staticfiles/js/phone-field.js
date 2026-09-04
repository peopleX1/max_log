(function () {
    function applyMask(digits, mask) {
        var result = '';
        var digitIndex = 0;
        for (var i = 0; i < mask.length && digitIndex < digits.length; i++) {
            if (mask[i] === '0') {
                result += digits[digitIndex];
                digitIndex++;
            } else {
                result += mask[i];
            }
        }
        return result;
    }

    function init() {
        var field = document.getElementById('phone-field');
        if (!field) {
            return;
        }

        var countrySelect = field.querySelector('#phone-country');
        var national = document.getElementById('phone_national');
        var mirror = field.querySelector('.phone-field__mirror');
        var maskEl = field.querySelector('.phone-field__mask');
        var wrap = field.querySelector('.phone-field__input-wrap');
        var hidden = document.getElementById('id_phone');
        var submitButton = document.getElementById('phone-submit');
        var form = field.closest('form');

        function currentCountry() {
            return countrySelect.options[countrySelect.selectedIndex];
        }

        function updateMaskDisplay() {
            var current = currentCountry();
            var placeholder = current ? current.dataset.placeholder : '';
            if (maskEl) {
                maskEl.textContent = placeholder.slice(national.value.length);
            }
            if (mirror) {
                mirror.textContent = national.value;
                national.style.width = mirror.offsetWidth + 'px';
            }
        }

        function sync() {
            var current = currentCountry();
            var maskPattern = current ? current.dataset.mask : '';
            var digits = national.value.replace(/\D/g, '');
            national.value = maskPattern ? applyMask(digits, maskPattern) : digits;
            updateMaskDisplay();
            var dialCode = current ? current.dataset.dialCode : '';
            var rawDigits = national.value.replace(/\D/g, '');
            hidden.value = rawDigits ? dialCode + rawDigits : '';

            if (submitButton) {
                var requiredDigits = maskPattern ? maskPattern.split('0').length - 1 : 0;
                submitButton.disabled = rawDigits.length !== requiredDigits;
            }
        }

        national.addEventListener('input', sync);
        countrySelect.addEventListener('change', sync);
        if (wrap) {
            wrap.addEventListener('click', function () {
                national.focus();
            });
        }
        if (form) {
            form.addEventListener('submit', sync);
        }
        sync();
    }

    document.addEventListener('DOMContentLoaded', init);
})();
