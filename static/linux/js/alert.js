// static/linux/js/alert.js

function showAlert(message, type) {
    const alertModalBody = document.getElementById('alertModalBody');
    let alertClass;

    switch (type) {
        case 'success':
            alertClass = 'alert-success';
            break;
        case 'danger':
            alertClass = 'alert-danger';
            break;
        case 'warning':
            alertClass = 'alert-warning';
            break;
        case 'info':
            alertClass = 'alert-info';
            break;
        default:
            alertClass = 'alert-secondary';
    }

    alertModalBody.innerHTML = `
        <div class="alert ${alertClass} d-flex align-items-center" role="alert">
            <div style="font-size: 2rem; margin-right: 15px;">
                <i class="fas ${getIconForType(type)}"></i>
            </div>
            <div>
                ${message}
            </div>
        </div>
    `;
    $('#alertModal').modal('show');
}

function getIconForType(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle';
        case 'danger':
            return 'fa-times-circle';
        case 'warning':
            return 'fa-exclamation-triangle';
        case 'info':
            return 'fa-info-circle';
        default:
            return 'fa-info-circle';
    }
}

function showConfirm(message, onConfirm, onCancel) {
    const alertModalBody = document.getElementById('alertModalBody');

    alertModalBody.innerHTML = `
        <div class="alert alert-warning d-flex flex-column align-items-center" role="alert">
            <div style="font-size: 2rem; margin-bottom: 15px;">
                <i class="fas fa-exclamation-triangle"></i>
            </div>
            <div style="text-align: center;">
                ${message}
            </div>
            <div class="mt-4">
                <button id="confirmBtn" class="btn btn-primary mr-2">OK</button>
                <button id="cancelBtn" class="btn btn-secondary">Cancelar</button>
            </div>
        </div>
    `;

    $('#alertModal').modal('show');

    document.getElementById('confirmBtn').onclick = function () {
        $('#alertModal').modal('hide');
        onConfirm();
    };

    document.getElementById('cancelBtn').onclick = function () {
        $('#alertModal').modal('hide');
        if (onCancel) onCancel();
    };
}
