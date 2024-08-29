function unzipFile(filePath) {
  if (!filePath) {
      showAlert('Caminho do arquivo inválido.', 'danger');
      return;
  }

  if (confirm('Tem certeza de que deseja descompactar este arquivo?')) {
      fetch(unzipFileUrl, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken
          },
          body: JSON.stringify({ 'path': filePath })
      }).then(response => response.json())
      .then(data => {
          if (data.status === 'success') {
              showAlert('Arquivo descompactado com sucesso!', 'success');
              window.location.reload();
          } else {
              showAlert('Falha ao descompactar: ' + data.message, 'danger');
          }
      }).catch(error => {
          showAlert('Erro: ' + error, 'danger');
          console.error('Error:', error);
      });
  }
}
