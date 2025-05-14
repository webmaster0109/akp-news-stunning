let toastBox = document.getElementById('toastBox');

function createToast(message, type) {
    const toast = document.createElement('div');
    toast.classList.add('toastInbox', `toast${type}`);
    toast.innerHTML = `<i class="bi bi-${type === 'Success' ? 'patch-check-fill' : type === 'Warning' ? 'info-circle-fill' : 'x-circle-fill'}"></i> ${message}`;
    toastBox.appendChild(toast);

    // playToastSound(type);
  
    setTimeout(() => {
      toast.remove();
    }, 2000);
}

function playToastSound(type) {
    let soundUrl;

    switch (type) {
        case 'Success':
            soundUrl = '/media/sounds/success.mp3';
            break;
        case 'Warning':
            soundUrl = '/media/sounds/warning.mp3';
            break;
        case 'Error':
            soundUrl = '/media/sounds/error.mp3';
            break;
    }

    const audio = new Audio(soundUrl);
    audio.play().catch(error => console.error('An error occurred:', error));
}