(()=>{"use strict";var e={372:function(e,t,n){var o=this&&this.__createBinding||(Object.create?function(e,t,n,o){void 0===o&&(o=n);var r=Object.getOwnPropertyDescriptor(t,n);r&&!("get"in r?!t.__esModule:r.writable||r.configurable)||(r={enumerable:!0,get:function(){return t[n]}}),Object.defineProperty(e,o,r)}:function(e,t,n,o){void 0===o&&(o=n),e[o]=t[n]}),r=this&&this.__setModuleDefault||(Object.create?function(e,t){Object.defineProperty(e,"default",{enumerable:!0,value:t})}:function(e,t){e.default=t}),i=this&&this.__importStar||function(e){if(e&&e.__esModule)return e;var t={};if(null!=e)for(var n in e)"default"!==n&&Object.prototype.hasOwnProperty.call(e,n)&&o(t,e,n);return r(t,e),t};Object.defineProperty(t,"__esModule",{value:!0}),t.CodelensProvider=void 0;const s=i(n(304));t.CodelensProvider=class{codeLenses=[];regex;_onDidChangeCodeLenses=new s.EventEmitter;onDidChangeCodeLenses=this._onDidChangeCodeLenses.event;constructor(){this.regex=/func \(s \*([a-zA-Z]*)\) ([a-zA-Z]*)\(/g,s.workspace.onDidChangeConfiguration((e=>{this._onDidChangeCodeLenses.fire()}))}provideCodeLenses(e){if(s.workspace.getConfiguration("codelens-sample").get("enableCodeLens",!0)){this.codeLenses=[];const r=new RegExp(this.regex),i=e.getText();let a;var t;if(!s.window.activeTextEditor)return[];for(t=s.window.activeTextEditor.document.uri.path;null!==(a=r.exec(i));){const r=e.lineAt(e.positionAt(a.index).line),i=r.text.indexOf(a[0]),d=new s.Position(r.lineNumber,i),c=e.getWordRangeAtPosition(d,new RegExp(this.regex));if(c){var n=a[1][0].toUpperCase()+a[1].slice(1),o=new s.CodeLens(c,{title:"Generate UT",tooltip:"Automatic UT generation",command:"codelens-sample.codelensAction",arguments:[t+":::"+n+":::"+a[2]]});this.codeLenses.push(o)}}return this.codeLenses}return[]}resolveCodeLens(e){return s.workspace.getConfiguration("codelens-sample").get("enableCodeLens",!0)?e:null}}},304:e=>{e.exports=require("vscode")},368:e=>{e.exports=require("child_process")}},t={};function n(o){var r=t[o];if(void 0!==r)return r.exports;var i=t[o]={exports:{}};return e[o].call(i.exports,i,i.exports,n),i.exports}var o={};(()=>{var e=o;Object.defineProperty(e,"__esModule",{value:!0}),e.deactivate=e.activate=e.auto_ut_trigger=void 0;const t=n(304),r=n(372);let i=[];function s(e,o){var r=(0,n(368).execSync)('python3 "'+e.extensionUri.path+'/python-scripts/auto_generate.py" "'+o[0]+'" '+o[1]+" "+o[2]).toString().trim();t.window.showInformationMessage(r)}e.auto_ut_trigger=s,e.activate=function(e){const n=new r.CodelensProvider;t.languages.registerCodeLensProvider("*",n),t.commands.registerCommand("codelens-sample.enableCodeLens",(()=>{t.workspace.getConfiguration("codelens-sample").update("enableCodeLens",!0,!0)})),t.commands.registerCommand("codelens-sample.codelensAction",(n=>{var o=n.split(":::");s(e,o),t.window.showInformationMessage("Hello from Niru")}))},e.deactivate=function(){i&&i.forEach((e=>e.dispose())),i=[]}})(),module.exports=o})();