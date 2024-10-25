console.log('post.js loaded');
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

document.addEventListener('DOMContentLoaded', function() {
    const badgeButtons = document.querySelectorAll('.badge-button');
    console.log('badgeButtons', badgeButtons);
    badgeButtons.forEach(button => {
        const mediaId = button.dataset.mediaId;
        const badgeType = button.dataset.badgeType;
        button.addEventListener('click', function() {
            // Send a POST request to update the like status
            fetch(`/like-media/${mediaId}/${badgeType}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateBadges(data);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    function updateBadges(data) {
        document.querySelectorAll('.badge-button').forEach(btn => {
            btn.classList.remove('selected');
            const countSpan = btn.querySelector('.badge-count');
            const badgeType = btn.dataset.badgeType;
            countSpan.textContent = data[`${badgeType}_likes`];
        });
        const selectedButton = document.querySelector(`.badge-button[data-badge-type="${data.user_like}"]`);
        if (selectedButton) {
            selectedButton.classList.add('selected');
        }
    }
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
