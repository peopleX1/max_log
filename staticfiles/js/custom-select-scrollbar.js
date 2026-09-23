(function () {
    var SHOW_DELAY = 60;
    var HIDE_DELAY = 1000;
    var VISIBLE_CLASS = 'custom-select__scrollbar-thumb--visible';

    function initScrollbarHover(wrap) {
        var list = wrap.querySelector('.custom-select__list');
        var thumb = wrap.querySelector('.custom-select__scrollbar-thumb');
        if (!list || !thumb) {
            return;
        }

        var showTimer = null;
        var hideTimer = null;

        function clearShowTimer() {
            if (showTimer) { clearTimeout(showTimer); showTimer = null; }
        }
        function clearHideTimer() {
            if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
        }

        function updateThumb() {
            var trackHeight = list.clientHeight;
            var scrollHeight = list.scrollHeight;
            if (scrollHeight <= trackHeight) {
                thumb.style.height = '0px';
                return;
            }
            var thumbHeight = Math.max(24, (trackHeight / scrollHeight) * trackHeight);
            var maxTop = trackHeight - thumbHeight;
            var scrollableHeight = scrollHeight - trackHeight;
            var top = scrollableHeight > 0 ? (list.scrollTop / scrollableHeight) * maxTop : 0;
            thumb.style.height = thumbHeight + 'px';
            thumb.style.transform = 'translateY(' + top + 'px)';
        }

        list.addEventListener('scroll', updateThumb);

        // список фильтруется поиском (custom-select.js скрывает опции через [hidden]) —
        // scrollHeight меняется без события scroll, пересчитываем thumb
        new MutationObserver(updateThumb).observe(list, {
            attributes: true,
            attributeFilter: ['hidden'],
            subtree: true,
        });

        list.addEventListener('mouseenter', function () {
            clearHideTimer();
            clearShowTimer();
            showTimer = setTimeout(function () {
                updateThumb();
                thumb.classList.add(VISIBLE_CLASS);
                showTimer = null;
            }, SHOW_DELAY);
        });

        list.addEventListener('mouseleave', function () {
            clearShowTimer();
            clearHideTimer();
            hideTimer = setTimeout(function () {
                thumb.classList.remove(VISIBLE_CLASS);
                hideTimer = null;
            }, HIDE_DELAY);
        });

        updateThumb();
    }

    function init() {
        document.querySelectorAll('.custom-select__list-wrap').forEach(initScrollbarHover);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
