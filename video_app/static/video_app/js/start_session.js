(function() {
    'use strict';
    window.addEventListener('load', function() {
        var forms = document.getElementsByClassName('needs-validation');
        var sectionInput = document.getElementById('id_section');
        var sectionFeedback = document.querySelector('#id_section + .invalid-feedback');
        var submitButton = document.querySelector('button[type="submit"]');

        // Debounce function to limit API calls
        function debounce(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        }

        // Function to check section availability
        const checkSectionAvailability = debounce(function(sectionValue) {
            fetch(`/check-section-availability/?section=${sectionValue}`)
                .then(response => response.json())
                .then(data => {
                    if (data.is_available) {
                        sectionInput.setCustomValidity('');
                        sectionFeedback.textContent = 'Section is available.';
                        sectionFeedback.classList.remove('invalid-feedback');
                        sectionFeedback.classList.add('valid-feedback');
                    } else {
                        sectionInput.setCustomValidity('Section already exists');
                        sectionFeedback.textContent = 'This section already exists. Please choose a different one.';
                        sectionFeedback.classList.remove('valid-feedback');
                        sectionFeedback.classList.add('invalid-feedback');
                    }
                    sectionInput.classList.add('was-validated');
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }, 300);

        // Add event listener for section input
        sectionInput.addEventListener('input', function() {
            checkSectionAvailability(this.value);
        });

        Array.prototype.filter.call(forms, function(form) {
            form.addEventListener('submit', function(event) {
                if (form.checkValidity() === false) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }, false);
})();