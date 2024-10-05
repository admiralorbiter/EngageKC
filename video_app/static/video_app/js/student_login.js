function confirmDelete() {
    return confirm("Are you sure you want to delete this session?");
}
function generateDeviceID() {
    let deviceID = localStorage.getItem('deviceID');
    if (!deviceID) {
        deviceID = 'device-' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('deviceID', deviceID);
    }
    document.cookie = "deviceID=" + deviceID;
}
// Call the function to generate the device ID when the page loads
window.onload = function() {
    generateDeviceID();
};
(function() {
    'use strict';
    window.addEventListener('load', function() {
        var forms = document.getElementsByClassName('needs-validation');
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