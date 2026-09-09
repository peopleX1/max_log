(function () {
    var instances = [];

    function closeOthers(except) {
        instances.forEach(function (instance) {
            if (instance !== except) {
                instance.close();
            }
        });
    }

    function bindSwipe(sheet, closeList) {
        var handle = sheet.querySelector('.custom-select__handle');
        if (!handle) {
            return;
        }

        var startY = 0;
        var currentY = 0;
        var sheetHeight = 0;
        var dragging = false;

        handle.addEventListener('pointerdown', function (event) {
            dragging = true;
            startY = event.clientY;
            currentY = startY;
            sheetHeight = sheet.getBoundingClientRect().height;
            sheet.style.transition = 'none';
            handle.setPointerCapture(event.pointerId);
        });

        handle.addEventListener('pointermove', function (event) {
            if (!dragging) {
                return;
            }
            currentY = event.clientY;
            var delta = Math.max(0, currentY - startY);
            sheet.style.setProperty('--select-drag-y', delta + 'px');
        });

        function release() {
            if (!dragging) {
                return;
            }
            dragging = false;
            sheet.style.transition = '';
            var delta = Math.max(0, currentY - startY);
            sheet.style.removeProperty('--select-drag-y');
            if (sheetHeight && delta > sheetHeight * .3) {
                closeList();
            }
        }

        handle.addEventListener('pointerup', release);
        handle.addEventListener('pointercancel', release);
    }

    function bind(wrapper) {
        if (wrapper.dataset.customSelectReady) {
            return;
        }
        wrapper.dataset.customSelectReady = 'true';

        var select = wrapper.querySelector('.custom-select__native');
        var trigger = wrapper.querySelector('.custom-select__trigger');
        var label = trigger.querySelector('.custom-select__trigger-label');
        var triggerFlag = trigger.querySelector('.custom-select__trigger-flag');
        var triggerCode = trigger.querySelector('.custom-select__trigger-code');
        var overlay = wrapper.querySelector('.custom-select__overlay');
        var sheet = wrapper.querySelector('.custom-select__sheet');
        var list = wrapper.querySelector('.custom-select__list');
        var searchWrap = wrapper.querySelector('.custom-select__search');
        var searchInput = wrapper.querySelector('.custom-select__search-input');
        var searchClear = wrapper.querySelector('.custom-select__search-clear');
        var emptyState = wrapper.querySelector('.custom-select__empty');

        function syncTrigger() {
            var current = select.options[select.selectedIndex];
            if (label) {
                label.textContent = current ? current.textContent : '';
            }
            if (triggerFlag) {
                var flagUrl = current ? current.dataset.flag : '';
                triggerFlag.src = flagUrl || '';
                triggerFlag.hidden = !flagUrl;
            }
            if (triggerCode) {
                triggerCode.textContent = current ? current.dataset.dialCode : '';
            }
        }

        function filterList(query) {
            var q = query.trim().toLowerCase();
            var visibleCount = 0;
            Array.prototype.forEach.call(list.children, function (item) {
                var matches = item.dataset.search.indexOf(q) !== -1;
                item.hidden = !matches;
                if (matches) {
                    visibleCount += 1;
                }
            });
            if (emptyState) {
                emptyState.hidden = visibleCount > 0;
            }
        }

        function isOpen() {
            return wrapper.classList.contains('custom-select--open');
        }

        function closeList() {
            wrapper.classList.remove('custom-select--open');
            trigger.setAttribute('aria-expanded', 'false');
        }

        var instance = { close: closeList };
        instances.push(instance);

        function openList() {
            closeOthers(instance);
            wrapper.classList.add('custom-select--open');
            trigger.setAttribute('aria-expanded', 'true');
            if (searchInput) {
                searchInput.value = '';
                if (searchWrap) {
                    searchWrap.classList.remove('custom-select__search--filled');
                }
                filterList('');
                setTimeout(function () {
                    searchInput.focus({ preventScroll: true });
                }, 0);
            }
        }

        function selectValue(value) {
            select.value = value;
            select.dispatchEvent(new Event('change', { bubbles: true }));
            syncTrigger();
            Array.prototype.forEach.call(list.children, function (item) {
                var isSelected = item.dataset.value === value;
                item.classList.toggle('custom-select__option--selected', isSelected);
                item.setAttribute('aria-selected', String(isSelected));
            });
        }

        trigger.addEventListener('click', function () {
            if (isOpen()) {
                closeList();
            } else {
                openList();
            }
        });

        overlay.addEventListener('click', closeList);

        list.addEventListener('click', function (event) {
            var item = event.target.closest('.custom-select__option');
            if (!item) {
                return;
            }
            selectValue(item.dataset.value);
            closeList();
            trigger.focus({ preventScroll: true });
        });

        document.addEventListener('click', function (event) {
            if (!wrapper.contains(event.target)) {
                closeList();
            }
        });

        wrapper.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') {
                closeList();
                trigger.focus({ preventScroll: true });
                return;
            }
            if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
                event.preventDefault();
                var items = Array.prototype.slice.call(list.children);
                var currentIndex = items.findIndex(function (item) {
                    return item.dataset.value === select.value;
                });
                var nextIndex = event.key === 'ArrowDown'
                    ? Math.min(currentIndex + 1, items.length - 1)
                    : Math.max(currentIndex - 1, 0);
                selectValue(items[nextIndex].dataset.value);
            }
        });

        if (searchInput) {
            searchInput.addEventListener('input', function (event) {
                if (searchWrap) {
                    searchWrap.classList.toggle('custom-select__search--filled', Boolean(event.target.value));
                }
                filterList(event.target.value);
            });
            searchInput.addEventListener('click', function (event) {
                event.stopPropagation();
            });
        }

        if (searchClear) {
            searchClear.addEventListener('click', function (event) {
                event.stopPropagation();
                searchInput.value = '';
                if (searchWrap) {
                    searchWrap.classList.remove('custom-select__search--filled');
                }
                filterList('');
                searchInput.focus();
            });
        }

        if (select.hasAttribute('data-submit-on-change')) {
            select.addEventListener('change', function () {
                if (select.form) {
                    select.form.submit();
                }
            });
        }

        bindSwipe(sheet, closeList);

        syncTrigger();
    }

    function init(root) {
        var scope = root || document;
        Array.prototype.forEach.call(scope.querySelectorAll('.custom-select'), bind);
    }

    document.addEventListener('DOMContentLoaded', function () {
        init(document);
    });

    if (window.htmx) {
        document.body.addEventListener('htmx:afterSwap', function (event) {
            init(event.target);
        });
    }

    window.CustomSelect = { init: init };
})();
