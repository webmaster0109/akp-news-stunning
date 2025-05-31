const logoutUser= document.querySelector('#logoutUser');
const logoutForm = document.querySelector('#logoutUserForm');
logoutUser.addEventListener('click', logoutAuthentication);

async function logoutAuthentication(e) {
    e.preventDefault();

    const csrfTokenOut = logoutForm.querySelector('[name=csrfmiddlewaretoken]').value;
    
    try {
        const response = await fetch('/account/logout-user/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfTokenOut,
            },
        });
    
        const result = await response.json();
    
        if (response.ok) {
            createToast(result.message, 'Success');
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            createToast(result.message, 'Warning');
        }
    } catch (error) {
        console.log(error);
        createToast('Something went wrong, try again.', 'Error');
    }
}