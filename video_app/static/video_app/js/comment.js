document.querySelectorAll('.reply').forEach(function(replyLink) {
    replyLink.addEventListener('click', function(event) {
        event.preventDefault();
        var commentId = this.dataset.id;
        var replyForm = this.closest('.comment').querySelector('.reply-form');
        replyForm.style.display = 'block';
    });
});

document.querySelectorAll('.delete-comment').forEach(function(deleteLink) {
    deleteLink.addEventListener('click', function(event) {
        event.preventDefault();
        var commentId = this.dataset.id;
        if (confirm('Are you sure you want to delete this comment?')) {
            fetch(`/delete-comment/${commentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.closest('.comment').remove();
                } else {
                    alert('Failed to delete comment');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while deleting the comment');
            });
        }
    });
});