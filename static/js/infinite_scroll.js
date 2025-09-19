
(function () {
    function throttle(fn, wait) {
        let last = 0;
        return function () {
            const now = Date.now();
            if (now - last >= wait) {
                last = now;
                fn.apply(this, arguments);
            }
        };
    }

    const $list = $('#post-list');
    if (!$list.length) return;

    let page = parseInt($list.data('page')) || 1;
    let hasNext = $list.data('has-next') === 1 || $list.data('has-next') === '1';
    let loading = false;

    function loadNext() {
        if (loading || !hasNext) return;
        loading = true;

        const requested = page + 1;
        console.log('[infinite] requesting page', requested);

        $.ajax({
            url: window.location.pathname,
            data: { page: requested },
            method: 'GET',
            dataType: 'json',
            success: function (data) {
                if (!data) {
                    console.warn('[infinite] empty response');
                    hasNext = false;
                    $(window).off('scroll.infinite');
                    return;
                }
                if (data.html && data.html.trim().length) {
                    $list.append(data.html);
                }
                if (typeof data.page !== 'undefined') {
                    page = parseInt(data.page) || page;
                } else {
                    page = requested;
                }
                hasNext = !!data.has_next;
                if (!hasNext) {
                    $(window).off('scroll.infinite');
                    console.log('[infinite] no more pages');
                }
            },
            error: function (xhr, status, err) {
                console.error('[infinite] ajax error', status, err);
            },
            complete: function () {
                loading = false;
            }
        });
    }

    $(window).on('scroll.infinite', throttle(function () {
        if (loading || !hasNext) return;
        if ($(window).scrollTop() + $(window).height() >= $(document).height() - 150) {
            loadNext();
        }
    }, 200));
})();
