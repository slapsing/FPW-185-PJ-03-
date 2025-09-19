let page = 2;
let loading = false;
let hasNext = true;

function loadPage(p) {
    if (!hasNext) return;
    loading = true;
    console.debug('Loading page', p);
    $.ajax({
        url: window.location.pathname,
        data: {page: p},
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            if (data && data.html && data.html.trim().length) {
                $('#post-list').append(data.html);
                page += 1;
                hasNext = data.has_next;
                if (!hasNext) {
                    $(window).off('scroll.infinite');
                    console.debug('No more content.');
                }
            } else {
                $(window).off('scroll.infinite');
                console.debug('No more content.');
            }
        },
        error: function (xhr, status, err) {
            console.warn('JSON load failed, fallback to HTML request', status);
            $.get(window.location.pathname + '?page=' + p, function (resp) {
                if (resp && resp.trim().length) {
                    $('#post-list').append(resp);
                    page += 1;
                } else {
                    $(window).off('scroll.infinite');
                }
            });
        },
        complete: function () {
            loading = false;
        }
    });
}

$(window).on('scroll.infinite', function () {
    if (loading) return;
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 150) {
        loadPage(page);
    }
});
