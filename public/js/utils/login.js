const form = document.querySelector('.login-form');

    form.addEventListener('submit', loginFormAuthentication);

    async function loginFormAuthentication(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        const response = await fetch('/account/login/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            body: formData,
        });

        const result = await response.json();

        if (response.ok) {
            createToast(result.message, 'Success');
            setTimeout(() => {
                window.location.replace('/');
            }, 2000);
        } else if (response.status === 400) {
            createToast(result.message, 'Warning');
        } else {
            createToast(result.message, 'Error');
        }
    }