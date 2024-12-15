document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('project-form');
    const addMoreButton = document.getElementById('add-more-images');
    let imageCount = 3;

    // Handle drag and drop
    document.querySelectorAll('.upload-box').forEach(box => {
        setupUploadBox(box);
    });

    // Add more images button
    addMoreButton.addEventListener('click', function() {
        const row = document.querySelector('.row');
        const newCol = document.createElement('div');
        newCol.className = 'col-md-4';
        imageCount++;
        
        newCol.innerHTML = `
            <div class="upload-box" id="upload-box-${imageCount}">
                <input type="file" name="image_file_${imageCount}" class="file-input" accept="image/*">
                <div class="upload-content">
                    <div class="upload-icon">+</div>
                    <p>Drag and Drop or Click<br>to Upload a Picture</p>
                </div>
                <img class="preview-image" style="display: none;">
                <button type="button" class="remove-image" style="display: none;">&times;</button>
            </div>
        `;
        
        row.appendChild(newCol);
        setupUploadBox(newCol.querySelector('.upload-box'));
    });

    function setupUploadBox(box) {
        const input = box.querySelector('.file-input');
        const preview = box.querySelector('.preview-image');
        const removeBtn = box.querySelector('.remove-image');
        const uploadContent = box.querySelector('.upload-content');

        box.addEventListener('dragover', (e) => {
            e.preventDefault();
            box.classList.add('dragover');
        });

        box.addEventListener('dragleave', () => {
            box.classList.remove('dragover');
        });

        box.addEventListener('drop', (e) => {
            e.preventDefault();
            box.classList.remove('dragover');
            if (e.dataTransfer.files[0]) {
                handleFile(e.dataTransfer.files[0]);
            }
        });

        input.addEventListener('change', (e) => {
            if (e.target.files[0]) {
                handleFile(e.target.files[0]);
            }
        });

        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            input.value = '';
            preview.style.display = 'none';
            removeBtn.style.display = 'none';
            uploadContent.style.display = 'block';
        });

        function handleFile(file) {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    removeBtn.style.display = 'block';
                    uploadContent.style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        }
    }

    // Form validation
    form.addEventListener('submit', function(event) {
        let isValid = true;
        const requiredInputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        requiredInputs.forEach(input => {
            if (!input.value) {
                isValid = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        });

        if (!isValid) {
            event.preventDefault();
            event.stopPropagation();
        }
        
        form.classList.add('was-validated');
    });
});
