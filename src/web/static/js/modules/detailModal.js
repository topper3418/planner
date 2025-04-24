

export function initDataModal() {
    console.log('Initializing data modal');
    const modal = document.getElementById('data-modal');
    const closeButton = document.getElementById('data-modal-close-button');

    function closeDataModal() {
        modal.classList.add('hidden');
    }

    // Close the modal when the close button is clicked
    closeButton.addEventListener('click', closeDataModal);

    // close the modal when the overlay is clicked
    modal.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeDataModal();
        }
    });

    // close the modal if the escape key is pressed
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            console.log('Escape key pressed');
            closeDataModal();
        }
    });
}
