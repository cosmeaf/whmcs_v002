function deleteFile(filePath) {
    if (confirm('Tem certeza de que deseja excluir este arquivo?')) {
        fetch(deleteFilesUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ 'path': filePath })  // Enviando como string para um único arquivo
        }).then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Arquivo excluído com sucesso!');
                window.location.reload();
            } else {
                alert('Falha ao excluir: ' + data.message);
            }
        }).catch(error => console.error('Erro:', error));
    }
}

function deleteSelectedFiles() {
    const selectedFiles = [];
    document.querySelectorAll('.fileCheckbox:checked').forEach(checkbox => {
        selectedFiles.push(checkbox.getAttribute('data-path'));
    });

    if (selectedFiles.length === 0) {
        showAlert('Nenhum arquivo selecionado para exclusão.', 'danger');
        return;
    }

    if (confirm('Tem certeza de que deseja excluir os arquivos selecionados?')) {
        fetch(deleteFilesUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ 'paths': selectedFiles })  // Enviando como lista para múltiplos arquivos
        }).then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showAlert('Arquivos excluídos com sucesso!', 'success');
                window.location.reload();
            } else {
                showAlert('Falha ao excluir: ' + data.message, 'danger');
            }
        }).catch(error => {
            showAlert('Erro: ' + error, 'danger');
            console.error('Erro:', error);
        });
    }
}
