document.addEventListener('DOMContentLoaded', function () {

    document.getElementsByName("student").forEach(function (elem) {
        var href_add = document.getElementById(elem.id + "-href-add");
        var href_remove = document.getElementById(elem.id + "-href-remove");
        elem.addEventListener("change", function () {
            if (elem.checked) {
                fetch(href_add);
            } else {
                fetch(href_remove);
            }

        });
    });
    document.getElementById("date-expired").addEventListener("change", function (event) {
        var elem = event.target;
        var href = document.getElementById(elem.id.split("-")[0] + "-href");
        window.location.href = href + "?date=" + elem.value;
    });
    document.getElementById("date-unlimited").addEventListener("change", function (event) {

        var elem = event.target;
        if (elem.checked) {
            var href = document.getElementById(elem.id.split("-")[0] + "-href").href;
            window.location.href = href + "?date=inf";

        }


    });
    document.getElementById("check-phrases").addEventListener("change", function (event) {

        var elem = event.target;
        var href = document.getElementById(elem.id + "-href").href;
        if (elem.checked) {

            fetch(href + "?value=true");

        } else {
            fetch(href + "?value=false");
        }


    });

});

