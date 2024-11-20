document.addEventListener('DOMContentLoaded', function () {
    let selectedCheckboxes = [];

    var active_edits = null;

    document.getElementsByName("edit_token").forEach(function (token_edit) {
        token_edit.addEventListener("click", function () {


            if (active_edits !== null) {
                var btn = document.getElementById(active_edits.id + "_btn");
                var input = document.getElementById(active_edits.id + "_input");
                btn.hidden = "hidden";
                input.type = "hidden";
                active_edits = null;
            }


            input = document.getElementById(token_edit.id + "_input");
            btn = document.getElementById(token_edit.id + "_btn");
            if (input.type === "hidden") {
                input.type = "text";

                var txt_cont = document.getElementById(token_edit.id + "_txt").textContent

                input.value = txt_cont;
                btn.hidden = null;
                input.hidden = null;
                active_edits = token_edit;
            } else {

                input.type = "hidden";
                btn.hidden = "hidden";
                active_edits = null;

            }
        });
    });

    document.getElementsByName("edit_pos").forEach(function (token_edit) {
        token_edit.addEventListener("click", function () {


            if (active_edits !== null) {
                var btn = document.getElementById(active_edits.id + "_btn");
                var input = document.getElementById(active_edits.id + "_input");
                btn.hidden = "hidden";
                input.type = "hidden";
                active_edits = null;
            }


            input = document.getElementById(token_edit.id + "_input");
            btn = document.getElementById(token_edit.id + "_btn");
            if (input.type === "hidden") {
                input.type = "text";

                var txt_cont = document.getElementById(token_edit.id + "_txt").textContent

                input.value = txt_cont;
                btn.hidden = null;
                input.hidden = null;
                active_edits = token_edit;
            } else {

                input.type = "hidden";
                btn.hidden = "hidden";
                active_edits = null;

            }
        });
    });


    document.getElementsByName("confirm_edit").forEach(function (confirm_btn) {
        confirm_btn.addEventListener("click", function () {

            var btn = document.getElementById(active_edits.id + "_btn");
            var input = document.getElementById(active_edits.id + "_input");

            window.location.href = btn.value + input.value;


        });

    });


    document.getElementsByName('checkbox_question').forEach(function (checkbox) {
        checkbox.addEventListener('click', function (event) {
            event.stopPropagation();
            var chb_id = checkbox.id.split("_");

            console.log("edit_token_" + chb_id[chb_id.length - 1]);

            var find_obj = document.getElementById("edit_token_" + chb_id[chb_id.length - 1]);


            if (checkbox.checked) {

                if (selectedCheckboxes.length < 2) {
                    selectedCheckboxes.push(checkbox);

                } else {

                    selectedCheckboxes[selectedCheckboxes.length - 1].checked = false;
                    document.getElementsByName("counter_" + selectedCheckboxes[selectedCheckboxes.length - 1].id.split("_")[1])[0].textContent = "";
                    selectedCheckboxes.pop();
                    selectedCheckboxes.push(checkbox);


                }


            } else {
                selectedCheckboxes = selectedCheckboxes.filter(function (item) {
                    return item !== checkbox;
                });
                document.getElementsByName("counter_" + checkbox.id.split("_")[1])[0].textContent = "";

            }
            for (let i = 0; i < selectedCheckboxes.length; i++) {
                let txt;
                if (i === 0) {
                    txt = "от";
                } else {
                    txt = "к"
                }
                console.log(selectedCheckboxes)
                document.getElementsByName("counter_" + selectedCheckboxes[i].id.split("_")[1])[0].textContent = txt;
            }

        });

    });
    document.getElementById("form-relation").addEventListener('submit', function (e) {
        let hiddenInput = document.getElementById('selected_order');
        let all_tokens = document.getElementsByName("token");


        if (selectedCheckboxes.length !== 2) {

            document.getElementById("form-error").textContent = "Необходимо выбрать два слова. Сейчас выбрано " + selectedCheckboxes.length + ".";
            e.preventDefault();
        }


        hiddenInput.value = selectedCheckboxes.map(cb => cb.value - 1).join('-');


    });

    document.querySelectorAll("select").forEach(function (elem) {
        elem.addEventListener('change', function () {
            window.location.href = document.getElementById(elem.name + "-btn").value + elem.value;

        });
    });


    var idx = 0;
    document.getElementsByName("form-remove").forEach(function (form) {
        let inputs = form.getElementsByTagName("input")[1];
        inputs.value = idx;
        idx += 1;
    });

});
