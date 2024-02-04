(()=>{"use strict";var e={372:function(e,t,o){var n=this&&this.__createBinding||(Object.create?function(e,t,o,n){void 0===n&&(n=o);var r=Object.getOwnPropertyDescriptor(t,o);r&&!("get"in r?!t.__esModule:r.writable||r.configurable)||(r={enumerable:!0,get:function(){return t[o]}}),Object.defineProperty(e,n,r)}:function(e,t,o,n){void 0===n&&(n=o),e[n]=t[o]}),r=this&&this.__setModuleDefault||(Object.create?function(e,t){Object.defineProperty(e,"default",{enumerable:!0,value:t})}:function(e,t){e.default=t}),i=this&&this.__importStar||function(e){if(e&&e.__esModule)return e;var t={};if(null!=e)for(var o in e)"default"!==o&&Object.prototype.hasOwnProperty.call(e,o)&&n(t,e,o);return r(t,e),t};Object.defineProperty(t,"__esModule",{value:!0}),t.CodelensProvider=void 0;const a=i(o(304));t.CodelensProvider=class{codeLenses=[];regex;_onDidChangeCodeLenses=new a.EventEmitter;onDidChangeCodeLenses=this._onDidChangeCodeLenses.event;constructor(){this.regex=/func \(s \*([a-zA-Z]*)Service\) ([a-zA-Z]*)\(/g,a.workspace.onDidChangeConfiguration((e=>{this._onDidChangeCodeLenses.fire()}))}provideCodeLenses(e){if(a.workspace.getConfiguration("auto-ut").get("enableCodeLens",!0)){this.codeLenses=[];const r=new RegExp(this.regex),i=e.getText();let s;var t;if(!a.window.activeTextEditor)return[];for(t=a.window.activeTextEditor.document.uri.path;null!==(s=r.exec(i));){const r=e.lineAt(e.positionAt(s.index).line),i=r.text.indexOf(s[0]),u=new a.Position(r.lineNumber,i),c=e.getWordRangeAtPosition(u,new RegExp(this.regex));if(c){var o=s[1][0].toUpperCase()+s[1].slice(1)+"Service",n=new a.CodeLens(c,{title:"Generate UT",tooltip:"Automatic UT generation",command:"auto-ut.generateUT",arguments:[t+":::"+o+":::"+s[2]]});this.codeLenses.push(n)}}return this.codeLenses}return[]}resolveCodeLens(e){return a.workspace.getConfiguration("auto-ut").get("enableCodeLens",!0)?e:null}}},172:function(e,t,o){var n=this&&this.__createBinding||(Object.create?function(e,t,o,n){void 0===n&&(n=o);var r=Object.getOwnPropertyDescriptor(t,o);r&&!("get"in r?!t.__esModule:r.writable||r.configurable)||(r={enumerable:!0,get:function(){return t[o]}}),Object.defineProperty(e,n,r)}:function(e,t,o,n){void 0===n&&(n=o),e[n]=t[o]}),r=this&&this.__setModuleDefault||(Object.create?function(e,t){Object.defineProperty(e,"default",{enumerable:!0,value:t})}:function(e,t){e.default=t}),i=this&&this.__importStar||function(e){if(e&&e.__esModule)return e;var t={};if(null!=e)for(var o in e)"default"!==o&&Object.prototype.hasOwnProperty.call(e,o)&&n(t,e,o);return r(t,e),t};Object.defineProperty(t,"__esModule",{value:!0}),t.deactivate=t.activate=t.auto_ut_trigger=void 0;const a=i(o(304)),s=o(304),u=o(372);let c=[];function d(e,t){var n=(0,o(368).execSync)('python3 "'+e.extensionUri.path+'/python-scripts/auto_generate.py" "'+t[0]+'" '+t[1]+" "+t[2]).toString().trim();s.window.showInformationMessage(n)}t.auto_ut_trigger=d,t.activate=function(e){const t=new u.CodelensProvider;s.languages.registerCodeLensProvider("go",t),s.commands.registerCommand("auto-ut.enableAutoUT",(()=>{s.workspace.getConfiguration("auto-ut").update("enableCodeLens",!0,!0),s.window.showInformationMessage("Hello from AmbitiousCoder, Enjoy AutoUT!")})),s.commands.registerCommand("auto-ut.disableAutoUT",(()=>{s.workspace.getConfiguration("auto-ut").update("enableCodeLens",!1,!0),s.window.showInformationMessage("Thanks for using AutoUT!")})),s.commands.registerCommand("auto-ut.generateUT",(t=>{var o=t.split(":::");s.window.showInformationMessage(`Generating UT: ${t[2]}`),d(e,o)})),a.commands.executeCommand("auto-ut.enableAutoUT")},t.deactivate=function(){c&&c.forEach((e=>e.dispose())),c=[]}},304:e=>{e.exports=require("vscode")},368:e=>{e.exports=require("child_process")}},t={},o=function o(n){var r=t[n];if(void 0!==r)return r.exports;var i=t[n]={exports:{}};return e[n].call(i.exports,i,i.exports,o),i.exports}(172);module.exports=o})();