document.addEventListener('DOMContentLoaded', function () {
    let selectedCheckboxes = [];




    document.getElementsByName('checkbox_question').forEach(function (checkbox) {
        checkbox.addEventListener('click', function (event) {
            var chb_id = checkbox.id.split("_");


            var find_obj = document.getElementById("edit_token_"+chb_id[chb_id.length-1]);


            if (checkbox.checked) {

                if (selectedCheckboxes.length < 2) {
                    selectedCheckboxes.push(checkbox);

                } else {

                    selectedCheckboxes[selectedCheckboxes.length - 1].checked = false;
                    document.getElementById("counter_" + selectedCheckboxes[selectedCheckboxes.length - 1].id.split("_")[1]).textContent = "";
                    selectedCheckboxes.pop();
                    selectedCheckboxes.push(checkbox);


                }


            } else {
                selectedCheckboxes = selectedCheckboxes.filter(function (item) {
                    return item !== checkbox;
                });
                document.getElementById("counter_" + checkbox.id.split("_")[1]).textContent = "";

            }
            for (let i = 0; i <selectedCheckboxes.length; i++){
                    let txt;
                    if (i === 0) {
                        txt = document.getElementById("start-symbol").textContent;
                    }
                    else {
                        txt = document.getElementById("end-symbol").textContent;
                    }
                document.getElementById("counter_" + selectedCheckboxes[i].id.split("_")[1]).textContent = txt;
                }

        });

    });
    document.getElementById("form-relation").addEventListener('submit', function (e) {
    let hiddenInput = document.getElementById('selected_order');


    if (selectedCheckboxes.length !== 2){

        document.getElementById("form-error").textContent = "Необходимо выбрать начало и конец. Сейчас выбрано " + selectedCheckboxes.length + ".";
        e.preventDefault();
    }


    hiddenInput.value = selectedCheckboxes.map(cb => cb.value-1).join('-');

});
    document.getElementById("part_type").addEventListener("change", function (event) {

        if (event.target.value === "composition") {
            document.getElementById("start-symbol").textContent = "[";
            document.getElementById("end-symbol").textContent = "]";
        } else {
            document.getElementById("start-symbol").textContent = "(";
            document.getElementById("end-symbol").textContent = ")";
        }
        selectedCheckboxes.forEach(function (value, index, array) {
            var elem = document.getElementById("counter_" + value.id.split("_")[1]);
            if (elem.textContent === "[") {
                elem.textContent = "(";
            } else if (elem.textContent === "(") {
                elem.textContent = "[";
            } else if (elem.textContent === "]") {
                elem.textContent = ")";
            } else if (elem.textContent === ")") {
                elem.textContent = "]";
            }

        });
    });


    document.querySelectorAll("select").forEach(function (elem) {
        if (elem.id !== "part_type") {
            elem.addEventListener('change', function () {
                fetch(document.getElementById(elem.id + "-href").href + "?value=" + elem.value);

            });
        }
    });

    var elem = document.getElementById("gram_bases");
    if (elem.value === "Сложное") {
        document.getElementsByName("simple_clas").forEach(function (elem) {
            elem.hidden = "hidden";
        });
    }


});
