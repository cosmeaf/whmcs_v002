function deleteSelectedFiles() {
  const selectedFiles = [];
  document.querySelectorAll('.fileCheckbox:checked').forEach(checkbox => {
      selectedFiles.push(checkbox.getAttribute('data-path'));
  });

  if (selectedFiles.length === 0) {
      alert('Nenhum arquivo ou pasta selecionado.');
      return;
  }

  if (!confirm('Você tem certeza que deseja excluir os arquivos/pastas selecionados? Esta ação não pode ser desfeita.')) {
      return;
  }

  fetch(deleteFilesUrl, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ 'paths': selectedFiles }),
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          alert('Arquivos/Pastas excluídos com sucesso.');
          location.reload(); // Recarregar a página para atualizar a lista de arquivos
      } else {
          alert('Erro ao excluir arquivos/pastas: ' + data.message);
      }
  })
  .catch(error => {
      console.error('Erro:', error);
      alert('Ocorreu um erro ao tentar excluir os arquivos/pastas.');
  });
}
