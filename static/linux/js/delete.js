// static/linux/js/delete.js

function deleteFiles(selectedFiles) {
    if (selectedFiles.length === 0) {
        showAlert('Nenhum arquivo selecionado para exclusão.', 'warning');
        return;
    }

    if (confirm('Tem certeza de que deseja excluir os arquivos selecionados?')) {
        fetch(deleteFilesUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ 'paths': selectedFiles })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Arquivos deletados com sucesso!', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                showAlert('Falha ao deletar: ' + data.message, 'danger');
            }
        })
        .catch(error => {
            showAlert('Erro: ' + error, 'danger');
            console.error('Error:', error);
        });
    }
}
