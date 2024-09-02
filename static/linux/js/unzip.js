function unzipFile(filePath) {
    if (!filePath) {
        showAlert('Caminho do arquivo inválido.', 'danger');
        return;
    }
  
    showConfirm('Tem certeza de que deseja descompactar este arquivo?', function() {
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
                setTimeout(() => {
                    window.location.reload();
                }, 2000);  // Adiciona um pequeno atraso para que o alerta seja visível
            } else {
                showAlert('Falha ao descompactar: ' + data.message, 'danger');
            }
        }).catch(error => {
            showAlert('Erro: ' + error, 'danger');
            console.error('Error:', error);
        });
    });
}
