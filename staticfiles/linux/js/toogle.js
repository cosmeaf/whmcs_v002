// static/linux/js/toggle.js

function toggleActionButtons() {
  const selectedFiles = [];
  const checkboxes = document.querySelectorAll('.fileCheckbox:checked');

  checkboxes.forEach(checkbox => {
      const filePath = checkbox.getAttribute('data-path');
      selectedFiles.push(filePath);
      console.log("Checkbox selecionado:", filePath);
  });

  console.log("Arquivos atualmente selecionados:", selectedFiles);

  const hasZipFile = selectedFiles.some(filePath => filePath.endsWith('.zip'));
  const deleteButton = document.getElementById('deleteSelected');
  const unzipButton = document.getElementById('unzipSelected');

  deleteButton.style.display = selectedFiles.length > 0 ? 'inline-block' : 'none';
  unzipButton.style.display = hasZipFile ? 'inline-block' : 'none';

  // Passar o array de arquivos selecionados como parâmetro para a função de exclusão
  deleteButton.onclick = function() {
      delete_file(selectedFiles);
  };
}
