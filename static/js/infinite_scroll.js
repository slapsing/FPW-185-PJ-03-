let page = 2;
$(window).scroll(function () {
    if ($(window).scrollTop() + $(window).height() >= $(document).height() - 100) {
        $.get('/posts/?page=' + page, function (data) {
            $('#post-list').append(data.html);
            page += 1;
        });
    }
});
