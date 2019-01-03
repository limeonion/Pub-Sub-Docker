'use strict';

const DIV_IDS = {
    CODE_TEXT_AREA: 'code-text-area',
    STDOUT_DISPLAY_AREA: 'stdout-display-area',
    STDERR_DISPLAY_AREA: 'stderr-display-area',
    LANGUAGE_SELECTION: 'language-selection'
};

const LANGUAGE_OPTIONS = {
    PYTHON: 'python',
    CPP: 'cpp',
    C: 'c',
    JAVASCRIPT: 'js'
};

let codeMirror;

function bodyOnLoad() {
    const config = {
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        value: '# Write some code here!\n\nprint("Hello World")'
    };
    const codeTextArea = document.getElementById(DIV_IDS.CODE_TEXT_AREA);
    codeMirror = CodeMirror(codeTextArea, config);
}

function submitCode() {
    clearDisplayAreas();
    const url = 'http://localhost:4000/run';
    // const code = encodeURI(codeTextArea.value);
    const code = codeMirror.getValue();
    const language = getLanguageSelection();
    console.log(code);
    $.post(
        url,
        {code, language},
        handleResponse
    );
}

function handleResponse(data, status) {
    const stdoutDisplayArea = document.getElementById(DIV_IDS.STDOUT_DISPLAY_AREA);
    const stderrDisplayArea = document.getElementById(DIV_IDS.STDERR_DISPLAY_AREA);
    console.log('AJAX Response', status, data);
    if (data) {
        if (data.stdout) {
            stdoutDisplayArea.innerText = data.stdout;
        }
        if (data.stderr) {
            stderrDisplayArea.innerText = data.stderr;
        }
    }
}

function clearDisplayAreas() {
    const stdoutDisplayArea = document.getElementById(DIV_IDS.STDOUT_DISPLAY_AREA);
    const stderrDisplayArea = document.getElementById(DIV_IDS.STDERR_DISPLAY_AREA);
    stdoutDisplayArea.innerHTML = '';
    stderrDisplayArea.innerHTML = '';
}

function getLanguageSelection() {
    return document.getElementById(DIV_IDS.LANGUAGE_SELECTION).value;
}

