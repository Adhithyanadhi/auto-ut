import * as vscode from 'vscode';

export class CodelensProvider implements vscode.CodeLensProvider {

	private codeLenses: vscode.CodeLens[] = [];
	private regex: RegExp;
	private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
	public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;

	constructor() {
		this.regex = /func \(s \*([a-zA-Z]*)Service\) ([a-zA-Z]*)\(/g;

		vscode.workspace.onDidChangeConfiguration((_) => {
			this._onDidChangeCodeLenses.fire();
		});
	}

	public provideCodeLenses(document: vscode.TextDocument): vscode.CodeLens[] | Thenable<vscode.CodeLens[]> {
		if (vscode.workspace.getConfiguration("auto-ut").get("enableCodeLens", true)) {
			this.codeLenses = [];
			const regex = new RegExp(this.regex);
			const text = document.getText();
			let matches;
			var current_file = "";
			if (vscode.window.activeTextEditor){
				current_file = vscode.window.activeTextEditor.document.uri.path;
			} else {
				return [];
			}

			while ((matches = regex.exec(text)) !== null) {
				const line = document.lineAt(document.positionAt(matches.index).line);
				const indexOf = line.text.indexOf(matches[0]);
				const position = new vscode.Position(line.lineNumber, indexOf);
				const range = document.getWordRangeAtPosition(position, new RegExp(this.regex));
				if (range) {
					var interface_name :string = matches[1][0].toUpperCase() + matches[1].slice(1) + "Service";
					var codeLens = new vscode.CodeLens(
						range, 
						{
							title: "Generate UT",
							tooltip: "Automatic UT generation",
							command: "auto-ut.generateUT",
							arguments: [current_file + ":::" + interface_name + ":::" + matches[2]]
						}
					);
					this.codeLenses.push(codeLens);
				}
			}
			return this.codeLenses;
		}
		return [];
	}

	public resolveCodeLens(codeLens: vscode.CodeLens,) {
		if (vscode.workspace.getConfiguration("auto-ut").get("enableCodeLens", true)) {
			return codeLens;
		}
		return null;
	}
}

