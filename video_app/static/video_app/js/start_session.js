(function() {
    'use strict';
    window.addEventListener('load', function() {
        var form = document.querySelector('form.needs-validation');
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

        // Form submission handler
        form.addEventListener('submit', function(event) {
            console.log('Form submitted');
            event.preventDefault();
            event.stopPropagation();
            
            if (form.checkValidity()) {
                console.log('Form is valid, submitting');
                
                // Use fetch to submit the form
                fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                })
                .then(response => response.text())
                .then(html => {
                    console.log('Server response:', html);
                    // Check if the response is a redirect
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const redirectMeta = doc.querySelector('meta[http-equiv="refresh"]');
                    if (redirectMeta) {
                        const content = redirectMeta.getAttribute('content');
                        const url = content.substring(content.indexOf('=') + 1);
                        window.location.href = url;
                    } else {
                        // If not a redirect, update the page content
                        document.body.innerHTML = html;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            } else {
                console.log('Form is invalid');
                form.classList.add('was-validated');
            }
        }, false);

        // Validate all fields on input
        form.querySelectorAll('input, select, textarea').forEach(input => {
            input.addEventListener('input', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    }, false);
})();
