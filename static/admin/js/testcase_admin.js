// Скрывает поле error description  и очищает содержимое при resul=True
(function ($) {
    function updateErrorDescriptionField() {
        if ($('#id_result').prop('checked')) {
            $('#id_error_description').hide().val('');  // Скрываем поле error_description и удаляем его значение
        } else {
            $('#id_error_description').show();  // Показываем поле error_description
        }
    }

    $(document).ready(function () {
        updateErrorDescriptionField();  // Вызываем функцию при загрузке страницы

        $('#id_result').on('change', function () {
            updateErrorDescriptionField();  // Вызываем функцию при изменении значения поля result
        });
    });
})(jQuery);

// Проставляет все checkbox select = True если выбран checkbox select_all и наоборот
(function () {
    function toggleAllCheckboxes(checkbox) {
        let checkboxes = document.getElementsByClassName('select-checkbox');
        for (let i = 0; i < checkboxes.length; i++) {
            checkboxes[i].checked = checkbox.checked;
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        let mainCheckbox = document.getElementById('select_all_tests-checkbox-id');
        mainCheckbox.addEventListener('change', function () {
            toggleAllCheckboxes(this);
            // alert('Checkboxes toggled');
        });
    });
})();
