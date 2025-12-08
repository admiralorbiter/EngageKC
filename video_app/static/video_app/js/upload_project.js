document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('project-form');
    const addMoreButton = document.getElementById('add-more-images');
    let imageCount = 1;

    // Handle drag and drop
    document.querySelectorAll('.upload-box').forEach(box => {
        setupUploadBox(box);
    });

    // Add more images button
    addMoreButton.addEventListener('click', function() {
        const row = document.getElementById('upload-grid');
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
        const newBox = newCol.querySelector('.upload-box');
        setupUploadBox(newBox);
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
                // Set the file to the input
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(e.dataTransfer.files[0]);
                input.files = dataTransfer.files;
                handleFile(e.dataTransfer.files[0]);
                updateRequiredAttributes();
            }
        });

        input.addEventListener('change', (e) => {
            if (e.target.files[0]) {
                handleFile(e.target.files[0]);
                updateRequiredAttributes();
            }
        });

        // Only allow clearing for the first box, removing for others
        const isFirstBox = box.id === 'upload-box-1';
        
        removeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (isFirstBox) {
                // First box: just clear the image
                input.value = '';
                preview.style.display = 'none';
                removeBtn.style.display = 'none';
                uploadContent.style.display = 'block';
            } else {
                // Other boxes: remove the entire box
                const col = box.closest('.col-md-4');
                if (col) {
                    col.remove();
                }
            }
            updateRequiredAttributes();
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

    // Update required attributes dynamically - first input is only required if no other images exist
    function updateRequiredAttributes() {
        const allFileInputs = form.querySelectorAll('.file-input');
        const fileInputsWithFiles = Array.from(allFileInputs).filter(input => input.files && input.files.length > 0);
        const firstInput = form.querySelector('input[name="image_file_1"]');
        
        // If there are other images, the first input doesn't need to be required
        // If no images exist, the first input must be required
        if (fileInputsWithFiles.length > 0) {
            firstInput.removeAttribute('required');
        } else {
            firstInput.setAttribute('required', 'required');
        }
    }

    // Form validation - check that at least one image is uploaded
    form.addEventListener('submit', function(event) {
        const allFileInputs = form.querySelectorAll('.file-input');
        const hasAtLeastOneImage = Array.from(allFileInputs).some(input => input.files && input.files.length > 0);
        
        if (!hasAtLeastOneImage) {
            event.preventDefault();
            event.stopPropagation();
            // Show error on first input if no images
            const firstInput = form.querySelector('input[name="image_file_1"]');
            if (firstInput) {
                firstInput.classList.add('is-invalid');
            }
            alert('Please upload at least one image for your project.');
        } else {
            // Clear any invalid classes
            allFileInputs.forEach(input => input.classList.remove('is-invalid'));
        }
        
        form.classList.add('was-validated');
    });
    
    // Initialize required attributes
    updateRequiredAttributes();
});
