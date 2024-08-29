document.getElementById('uploadForm').addEventListener('submit', function(event) {
  event.preventDefault();
  const formData = new FormData();
  const fileField = document.querySelector('input[type="file"]');

  formData.append('file', fileField.files[0]);

  fetch(uploadProjectUrl, {
      method: 'POST',
      body: formData,
      headers: {
          'X-CSRFToken': csrfToken
      }
  }).then(response => response.json())
  .then(data => {
      if (data.status === 'success') {
          showAlert('Upload realizado com sucesso!', 'success');
          window.location.reload(); 
      } else {
          showAlert('Falha no upload: ' + data.message, 'danger');
      }
  }).catch(error => {
      showAlert('Erro: ' + error, 'danger');
      console.error('Error:', error);
  });
});
