document.addEventListener('DOMContentLoaded', function() {
    const postForm = document.getElementById('post-form');

    postForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        // Collect form data
        const formData = new FormData(postForm);

        // Make a fetch POST request
        fetch('/post', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token }}', // Include CSRF token
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json(); // Parse response as JSON
        })
        .then(data => {
            // Handle success response
            console.log('Post submitted successfully:', data);
            // Optionally, update UI or display a success message
            location.reload(); // Refresh the page to see the new post
        })
        .catch(error => {
            // Handle error
            console.error('Error submitting post:', error);
            // Optionally, display an error message to the user
        });
    });
});
