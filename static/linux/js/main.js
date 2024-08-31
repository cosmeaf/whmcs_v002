// static/linux/js/main.js

class App {
    constructor() {
        this.csrfToken = '{{ csrf_token }}';
        this.deleteFileUrl = "{% url 'delete_file' %}";
        this.unzipFileUrl = "{% url 'unzip_file' %}";
        this.setup();
    }

    getCsrfToken() {
        return this.csrfToken;
    }

    getDeleteFileUrl() {
        return this.deleteFileUrl;
    }

    getUnzipFileUrl() {
        return this.unzipFileUrl;
    }

    setup() {
        console.log("CSRF Token:", this.getCsrfToken());
        console.log("Delete File URL:", this.getDeleteFileUrl());
        console.log("Unzip File URL:", this.getUnzipFileUrl());
    }
}
window.app = new App();


window.csrfToken = '{{ csrf_token }}';
window.uploadProjectUrl = "{% url 'upload_project' %}";
window.unzipFileUrl = "{% url 'unzip_file' %}";
window.deleteFileUrl = "{% url 'delete_file' %}";

console.log("CSRF Token:", window.csrfToken);
console.log("uploadProjectUrl:", window.uploadProjectUrl);
console.log("unzipFileUrl:", window.unzipFileUrl);
console.log("deleteFileUrl:", window.deleteFileUrl);