const newsletterForms = document.querySelectorAll('.subscriber-form');

newsletterForms.forEach(form => {
  form.addEventListener('submit', newsletterFormAuthentication);
});

async function newsletterFormAuthentication(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const formUrl = form.action;
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;

        // const newsletterMessage = document.querySelector('.subscriber-message') || document.parentElement.querySelector('.subscriber-message') || document.nextElementSibling.querySelector('.subscriber-message');

        const messageId = form.getAttribute('data-message-target');
        const newsletterMessage = messageId ? document.getElementById(messageId) : null;

        try {
          const response = await fetch(formUrl, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': csrfToken,
              },
              body: formData,
          });

          const result = await response.json();
          newsletterMessage.style.display = 'block';
          newsletterMessage.innerHTML = result.message;
          
          if (response.ok) {
              newsletterMessage.style.color = 'green';
              form.reset();
          } else {
              newsletterMessage.style.color = 'red';
          }

          setTimeout(() => {
            newsletterMessage.style.display = 'none';
          }, 2000);
        } catch (error) {
          console.error('Error submitting form:', error);
          newsletterMessage.style.display = 'block';
          newsletterMessage.style.color = 'red';
          newsletterMessage.innerHTML = 'An error occurred. Please try again.';

          setTimeout(() => {
            newsletterMessage.style.display = 'none';
          }, 2000);
        }
}