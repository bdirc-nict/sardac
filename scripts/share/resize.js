function resize() {
    var width = $(window).width();
    var height = $(window).height();

    var leftWidth = $("#left").width();

    var footerHeight = $("footer").height();
    var headerHeight = $("#header").height();
    var subheaderHeight = $("#subheader").height();

    var mapHeight = height - headerHeight - subheaderHeight - footerHeight;


    $("#map").width(width - leftWidth);
    $("#header").width(width);
    $("#subheader").width(width - 20);

    $("#map").height(mapHeight);

    //// タブの高さ制御
    $("#left").height(mapHeight);
    var tabHeight = $("#tab").height();
    $(".tab-content").height(mapHeight - tabHeight - 21);
}

onresize = function () { resize(); };