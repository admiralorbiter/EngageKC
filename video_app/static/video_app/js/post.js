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

    // Image gallery functionality
    const mainImage = document.getElementById('mainImage');
    const thumbnailContainer = document.querySelector('.thumbnail-scroll');
    const lightbox = document.getElementById('lightbox');
    const lightboxImage = document.getElementById('lightboxImage');
    
    let currentImageIndex = 0;
    let images = [];

    // Initialize images array with main image and project images
    function initializeImages() {
        images = [mainImage.src];
        const projectImages = mainImage.dataset.projectImages;
        if (projectImages) {
            images = images.concat(JSON.parse(projectImages));
        }
        
        if (images.length > 1) {
            createThumbnails();
            setupScrollButtons();
        }
    }

    function createThumbnails() {
        const thumbnailScroll = document.createElement('div');
        thumbnailScroll.className = 'thumbnail-scroll';

        images.forEach((src, index) => {
            const thumb = document.createElement('img');
            thumb.src = src;
            thumb.className = `thumbnail ${index === 0 ? 'active' : ''}`;
            thumb.onclick = () => switchImage(index);
            thumbnailScroll.appendChild(thumb);
        });

        const container = document.createElement('div');
        container.className = 'thumbnail-container';
        
        // Add scroll buttons
        const leftButton = document.createElement('button');
        leftButton.className = 'scroll-button scroll-left';
        leftButton.innerHTML = '←';
        leftButton.onclick = () => scrollThumbnails('left');

        const rightButton = document.createElement('button');
        rightButton.className = 'scroll-button scroll-right';
        rightButton.innerHTML = '→';
        rightButton.onclick = () => scrollThumbnails('right');

        container.appendChild(leftButton);
        container.appendChild(thumbnailScroll);
        container.appendChild(rightButton);

        mainImage.parentElement.appendChild(container);
    }

    function switchImage(index) {
        if (mainImage && images[index]) {
            currentImageIndex = index;
            mainImage.src = images[index];
            
            // Update lightbox image if it's open
            if (lightbox.style.display === "block") {
                lightboxImage.src = images[index];
            }
            
            // Update active thumbnail
            document.querySelectorAll('.thumbnail').forEach((thumb, i) => {
                thumb.classList.toggle('active', i === index);
            });
            
            // Scroll thumbnail into view
            const activeThumb = document.querySelector('.thumbnail.active');
            if (activeThumb) {
                activeThumb.scrollIntoView({
                    behavior: 'smooth',
                    block: 'nearest',
                    inline: 'center'
                });
            }
        }
    }

    function scrollThumbnails(direction) {
        const scrollAmount = 110; // thumbnail width + gap
        const container = document.querySelector('.thumbnail-scroll');
        
        if (direction === 'left') {
            container.scrollLeft -= scrollAmount;
        } else {
            container.scrollLeft += scrollAmount;
        }
    }

    // Lightbox functionality
    mainImage.onclick = function() {
        lightbox.style.display = "block";
        lightboxImage.src = images[currentImageIndex];
    }

    // Add keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (lightbox.style.display === 'block') {
            if (e.key === 'ArrowLeft' && currentImageIndex > 0) {
                switchImage(currentImageIndex - 1);
                lightboxImage.src = images[currentImageIndex];
            } else if (e.key === 'ArrowRight' && currentImageIndex < images.length - 1) {
                switchImage(currentImageIndex + 1);
                lightboxImage.src = images[currentImageIndex];
            } else if (e.key === 'Escape') {
                lightbox.style.display = 'none';
            }
        }
    });

    // Initialize the gallery
    initializeImages();

    function setupThumbnailNavigation() {
        const scrollLeftBtn = document.querySelector('.scroll-left');
        const scrollRightBtn = document.querySelector('.scroll-right');
        const thumbnailScroll = document.querySelector('.thumbnail-scroll');
        
        if (scrollLeftBtn && scrollRightBtn && thumbnailScroll) {
            const scrollAmount = 100; // Adjust based on thumbnail width + gap
            
            scrollLeftBtn.addEventListener('click', () => {
                thumbnailScroll.scrollBy({
                    left: -scrollAmount,
                    behavior: 'smooth'
                });
            });
            
            scrollRightBtn.addEventListener('click', () => {
                thumbnailScroll.scrollBy({
                    left: scrollAmount,
                    behavior: 'smooth'
                });
            });
        }
    }

    setupThumbnailNavigation();

    // Add arrow navigation for main view (not just lightbox)
    function setupArrowNavigation() {
        document.addEventListener('keydown', function(e) {
            // Handle arrow keys for both main view and lightbox
            if (e.key === 'ArrowLeft') {
                if (currentImageIndex > 0) {
                    switchImage(currentImageIndex - 1);
                }
            } else if (e.key === 'ArrowRight') {
                if (currentImageIndex < images.length - 1) {
                    switchImage(currentImageIndex + 1);
                }
            }
        });

        // Add click handlers for arrow buttons
        const leftButton = document.querySelector('.scroll-left');
        const rightButton = document.querySelector('.scroll-right');

        if (leftButton) {
            leftButton.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent default scroll behavior
                if (currentImageIndex > 0) {
                    switchImage(currentImageIndex - 1);
                }
            });
        }

        if (rightButton) {
            rightButton.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent default scroll behavior
                if (currentImageIndex < images.length - 1) {
                    switchImage(currentImageIndex + 1);
                }
            });
        }
    }

    // Initialize everything
    function init() {
        initializeImages();
        setupArrowNavigation();
        setupThumbnailNavigation();
    }

    init();
});
