/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ([
/* 0 */
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {


var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.deactivate = exports.activate = exports.auto_ut_trigger = void 0;
const vscode = __importStar(__webpack_require__(1));
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode_1 = __webpack_require__(1);
const CodelensProvider_1 = __webpack_require__(2);
// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
let disposables = [];
function auto_ut_trigger(context, args) {
    const execSync = (__webpack_require__(3).execSync);
    var output = execSync('python3 ' + '"' + context.extensionUri.path + '/python-scripts/auto_generate.py' + '" ' + '"' + args[0] + '" ' + args[1] + ' ' + args[2]).toString().trim();
    vscode_1.window.showInformationMessage(output);
}
exports.auto_ut_trigger = auto_ut_trigger;
function activate(context) {
    const codelensProvider = new CodelensProvider_1.CodelensProvider();
    vscode_1.languages.registerCodeLensProvider("go", codelensProvider);
    vscode_1.commands.registerCommand("auto-ut.enableAutoUT", () => {
        vscode_1.workspace.getConfiguration("auto-ut").update("enableCodeLens", true, true);
        vscode_1.window.showInformationMessage(`Hello from AmbitiousCoder, Enjoy AutoUT!`);
    });
    vscode_1.commands.registerCommand("auto-ut.disableAutoUT", () => {
        vscode_1.workspace.getConfiguration("auto-ut").update("enableCodeLens", false, true);
        vscode_1.window.showInformationMessage(`Thanks for using AutoUT!`);
    });
    vscode_1.commands.registerCommand("auto-ut.generateUT", (arg) => {
        vscode_1.window.showInformationMessage(`Generating ${arg}`);
        var args = arg.split(":::");
        auto_ut_trigger(context, args);
    });
    vscode.commands.executeCommand("auto-ut.enableAutoUT");
}
exports.activate = activate;
// this method is called when your extension is deactivated
function deactivate() {
    if (disposables) {
        disposables.forEach(item => item.dispose());
    }
    disposables = [];
}
exports.deactivate = deactivate;


/***/ }),
/* 1 */
/***/ ((module) => {

module.exports = require("vscode");

/***/ }),
/* 2 */
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {


var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.CodelensProvider = void 0;
const vscode = __importStar(__webpack_require__(1));
/**
 * CodelensProvider
 */
class CodelensProvider {
    codeLenses = [];
    regex;
    _onDidChangeCodeLenses = new vscode.EventEmitter();
    onDidChangeCodeLenses = this._onDidChangeCodeLenses.event;
    constructor() {
        this.regex = /func \(s \*([a-zA-Z]*)Service\) ([a-zA-Z]*)\(/g;
        vscode.workspace.onDidChangeConfiguration((_) => {
            this._onDidChangeCodeLenses.fire();
        });
    }
    provideCodeLenses(document) {
        if (vscode.workspace.getConfiguration("auto-ut").get("enableCodeLens", true)) {
            this.codeLenses = [];
            const regex = new RegExp(this.regex);
            const text = document.getText();
            let matches;
            var current_file = "";
            if (vscode.window.activeTextEditor) {
                current_file = vscode.window.activeTextEditor.document.uri.path;
            }
            else {
                return [];
            }
            while ((matches = regex.exec(text)) !== null) {
                const line = document.lineAt(document.positionAt(matches.index).line);
                const indexOf = line.text.indexOf(matches[0]);
                const position = new vscode.Position(line.lineNumber, indexOf);
                const range = document.getWordRangeAtPosition(position, new RegExp(this.regex));
                if (range) {
                    var interface_name = matches[1][0].toUpperCase() + matches[1].slice(1) + "Sevice";
                    var codeLens = new vscode.CodeLens(range, {
                        title: "Generate UT",
                        tooltip: "Automatic UT generation",
                        command: "auto-ut.generateUT",
                        arguments: [current_file + ":::" + interface_name + ":::" + matches[2]]
                    });
                    this.codeLenses.push(codeLens);
                }
            }
            return this.codeLenses;
        }
        return [];
    }
    resolveCodeLens(codeLens) {
        if (vscode.workspace.getConfiguration("auto-ut").get("enableCodeLens", true)) {
            return codeLens;
        }
        return null;
    }
}
exports.CodelensProvider = CodelensProvider;


/***/ }),
/* 3 */
/***/ ((module) => {

module.exports = require("child_process");

/***/ })
/******/ 	]);
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module is referenced by other modules so it can't be inlined
/******/ 	var __webpack_exports__ = __webpack_require__(0);
/******/ 	module.exports = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=extension.js.map