document.addEventListener('DOMContentLoaded', function() {
    const badgeButtons = document.querySelectorAll('.badge-button');
    // Parse the liked media JSON, defaulting to an empty object if not provided
    const likedMedia = JSON.parse('{{ liked_media|default:"{}" | escapejs }}');
    
    badgeButtons.forEach(button => {
        const mediaId = button.dataset.mediaId;
        const badgeType = button.dataset.badgeType;
        const card = button.closest('.card');
        
        // Pre-select the badge if it's in the likedMedia object
        if (likedMedia[mediaId] === badgeType) {
            selectBadge(button);
        }
        
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
                    updateBadges(card, data);
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
    
    function updateBadges(card, data) {
        card.querySelectorAll('.badge-button').forEach(btn => {
            btn.classList.remove('selected');
            const countSpan = btn.querySelector('.badge-count');
            const badgeType = btn.dataset.badgeType;
            countSpan.textContent = data[`${badgeType}_likes`];
        });
        const selectedButton = card.querySelector(`.badge-button[data-badge-type="${data.user_like}"]`);
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

// Add this function definition
function selectBadge(button) {
    button.classList.add('selected');
}