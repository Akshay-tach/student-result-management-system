document.querySelectorAll('form[data-confirm]').forEach(form => form.addEventListener('submit', event => {
  if (!window.confirm(form.dataset.confirm)) event.preventDefault();
}));
document.querySelectorAll('.alert').forEach(alert => setTimeout(() => alert.classList.add('fade'), 5000));
