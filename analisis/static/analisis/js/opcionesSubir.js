document.addEventListener("DOMContentLoaded", function () {
    const selectAll = document.getElementById("select_all");
    const checkboxes = document.querySelectorAll("input[name='opciones']");

    if (selectAll) {
        selectAll.addEventListener("change", function () {
            checkboxes.forEach(cb => cb.checked = this.checked);
        });
    }
});
