function showAlert(message, type) {
  const alertModalBody = document.getElementById('alertModalBody');
  alertModalBody.textContent = message;
  $('#alertModal').modal('show');
}
