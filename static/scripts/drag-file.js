document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.querySelector(".drop-zone");
    const fileInput = document.querySelector(".file-input");
    const fileNameDisplay = document.querySelector(".file-name");
    const fileIconDisplay = document.querySelector(".file-icon");

    if (!dropZone || !fileInput || !fileNameDisplay || !fileIconDisplay) {
        console.error("Элементы не найдены.");
        return;
    }

    // Открыть диалог выбора файла при клике на зону загрузки
    dropZone.addEventListener("click", () => fileInput.click());

    // Обработчик событий для перетаскивания файла
    dropZone.addEventListener("dragover", (event) => {
        event.preventDefault();
        dropZone.style.borderColor = "#745FF2";
        dropZone.style.background = "#e8e8e8";
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.style.borderColor = "#728AB7";
        dropZone.style.background = "#F0F0F3";
    });

    dropZone.addEventListener("drop", (event) => {
        event.preventDefault();
        dropZone.style.borderColor = "#728AB7";
        dropZone.style.background = "#F0F0F3";

        const files = event.dataTransfer.files;
        if (files.length) {
            fileInput.files = files;
            displayFileInfo(files[0]);
        }
    });

    // Обработчик событий для выбора файла через input
    fileInput.addEventListener("change", () => {
        if (fileInput.files.length) {
            displayFileInfo(fileInput.files[0]);
        }
    });

    // Функция для отображения имени и иконки файла
    function displayFileInfo(file) {
        // Отображаем имя файла
        fileNameDisplay.textContent = file.name;

        // Определяем тип файла и устанавливаем иконку
        const fileType = file.type;

        let icon = '';

        // Пример для изображений (PNG, JPG, GIF)
        if (fileType.includes("image")) {
            icon = '📷';  // Иконка изображения
        }
        // Пример для текстовых файлов
        else if (fileType.includes("text")) {
            icon = '📄';  // Иконка текста
        }
        // Пример для PDF
        else if (fileType.includes("pdf")) {
            icon = '📖';  // Иконка PDF
        }
        // Пример для видео
        else if (fileType.includes("video")) {
            icon = '🎥';  // Иконка видео
        }
        // Пример для аудио
        else if (fileType.includes("audio")) {
            icon = '🎵';  // Иконка аудио
        } else {
            icon = '📂';  // Общая иконка для других типов
        }

        // Устанавливаем иконку
        fileIconDisplay.textContent = icon;
    }
});
