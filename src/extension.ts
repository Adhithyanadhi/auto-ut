import * as vscode from 'vscode';
// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import { ExtensionContext, languages, commands, Disposable, workspace, window } from 'vscode';
import { CodelensProvider } from './CodelensProvider';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed

let disposables: Disposable[] = [];

export function auto_ut_trigger(context: ExtensionContext, args: string[]) {
	const execSync = require("child_process").execSync; 
	var output = execSync('python3 ' + '"' + context.extensionUri.path + '/python-scripts/auto_generate.py' + '" ' + '"'  + args[0] + '" ' + args[1] + ' ' + args[2]).toString().trim();
	window.showInformationMessage(output);
}



export function activate(context: ExtensionContext) {
	const codelensProvider = new CodelensProvider();

	languages.registerCodeLensProvider("go", codelensProvider);

	commands.registerCommand("auto-ut.enableAutoUT", () => {
		workspace.getConfiguration("auto-ut").update("enableCodeLens", true, true);
		window.showInformationMessage(`Hello from AmbitiousCoder, Enjoy AutoUT!`);
	});

	commands.registerCommand("auto-ut.disableAutoUT", () => {
		workspace.getConfiguration("auto-ut").update("enableCodeLens", false, true);
		window.showInformationMessage(`Thanks for using AutoUT!`);
	});

	commands.registerCommand("auto-ut.generateUT", (arg: string) => {
		var args :string[]= arg.split(":::");
		window.showInformationMessage(`Generating UT: ${args[2]}`);
		auto_ut_trigger(context, args);
	});
	vscode.commands.executeCommand("auto-ut.enableAutoUT");
}



// this method is called when your extension is deactivated
export function deactivate() {
	if (disposables) {
		disposables.forEach(item => item.dispose());
	}
	disposables = [];
}
