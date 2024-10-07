// Get the elements
var mainImage = document.getElementById('mainImage');
var lightbox = document.getElementById('lightbox');
var lightboxImage = document.getElementById('lightboxImage');
var closeBtn = document.getElementsByClassName('close')[0];

// When the user clicks on the image, open the lightbox
mainImage.onclick = function(){
    lightbox.style.display = "block";
    lightboxImage.src = this.src;
}

// When the user clicks on the close button, close the lightbox
closeBtn.onclick = function() {
    lightbox.style.display = "none";
}

// Close the lightbox when clicking outside the image
lightbox.onclick = function(event) {
    if (event.target == lightbox) {
        lightbox.style.display = "none";
    }
}

document.getElementById('device_id').value = localStorage.getItem('deviceID'); // Set the device ID in the hidden field