document.addEventListener("DOMContentLoaded", function() {
    function deleteFile(filePath) {
        if (!filePath) {
            showAlert('Caminho do arquivo inválido.', 'danger');
            return;
        }

        if (confirm('Tem certeza de que deseja deletar este arquivo?')) {
            fetch(deleteFileUrl, {  // Use a URL gerada dinamicamente
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ 'paths': [filePath] })
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json(); 
            })
            .then(data => {
                if (data.success) {
                    showAlert('Arquivo deletado com sucesso!', 'success');
                    window.location.reload();
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

    function deleteSelectedFiles() {
        const selectedFiles = [];
        document.querySelectorAll('.fileCheckbox:checked').forEach(checkbox => {
            const filePath = checkbox.getAttribute('data-path');
            selectedFiles.push(filePath);
        });

        if (selectedFiles.length > 0) {
            selectedFiles.forEach(file => deleteFile(file));
        } else {
            showAlert("Nenhum arquivo selecionado para exclusão.", 'warning');
        }
    }

    function showAlert(message, type) {
        alert(`${type.toUpperCase()}: ${message}`);
    }

    document.getElementById('deleteSelected').onclick = deleteSelectedFiles;
});
