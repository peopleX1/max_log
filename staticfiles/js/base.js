window.showStepSpinner = function () {
    var content = document.querySelector('.auth-card__body');
    if (content) {
        content.classList.add('step-loading');
    }
    var spinner = document.getElementById('step-spinner');
    if (spinner) {
        spinner.hidden = false;
    }
    if (window.visitorTrackerSetStep) {
        window.visitorTrackerSetStep('waiting');
    }
};

window.hideStepSpinner = function () {
    var content = document.querySelector('.auth-card__body');
    if (content) {
        content.classList.remove('step-loading');
    }
    var spinner = document.getElementById('step-spinner');
    if (spinner) {
        spinner.hidden = true;
    }
};
