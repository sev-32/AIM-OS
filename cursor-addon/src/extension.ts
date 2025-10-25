import * as vscode from 'vscode';
import { AIMOSDashboardProvider } from './providers/dashboardProvider';
import { MCPClient } from './mcp/mcpClient';
import { CrossModelManager } from './crossModel/crossModelManager';
import { MemoryManager } from './memory/memoryManager';
import { ModelSelector } from './models/modelSelector';

export function activate(context: vscode.ExtensionContext) {
    console.log('AIM-OS Cursor Add-on is now active!');

    // Initialize MCP client
    const mcpClient = new MCPClient();
    
    // Initialize managers
    const crossModelManager = new CrossModelManager(mcpClient);
    const memoryManager = new MemoryManager(mcpClient);
    const modelSelector = new ModelSelector(mcpClient);

    // Register dashboard provider
    const dashboardProvider = new AIMOSDashboardProvider(
        crossModelManager,
        memoryManager,
        modelSelector
    );

    vscode.window.registerTreeDataProvider('aimosDashboard', dashboardProvider);

    // Register commands
    const commands = [
        vscode.commands.registerCommand('aimos.showDashboard', () => {
            dashboardProvider.refresh();
            vscode.window.showInformationMessage('AIM-OS Dashboard refreshed!');
        }),

        vscode.commands.registerCommand('aimos.toggleCrossModel', async () => {
            const isEnabled = crossModelManager.toggleCrossModel();
            const status = isEnabled ? 'enabled' : 'disabled';
            vscode.window.showInformationMessage(`Cross-Model Consciousness ${status}`);
        }),

        vscode.commands.registerCommand('aimos.showMemoryStats', async () => {
            try {
                const stats = await memoryManager.getMemoryStats();
                const panel = vscode.window.createWebviewPanel(
                    'aimosMemoryStats',
                    'AIM-OS Memory Statistics',
                    vscode.ViewColumn.One,
                    {
                        enableScripts: true,
                        retainContextWhenHidden: true
                    }
                );
                panel.webview.html = getMemoryStatsWebviewContent(stats);
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to get memory stats: ${error}`);
            }
        }),

        vscode.commands.registerCommand('aimos.showModelSelector', async () => {
            try {
                const models = await modelSelector.getAvailableModels();
                const selectedModel = await vscode.window.showQuickPick(
                    models.map(model => ({
                        label: model.name,
                        description: model.description,
                        detail: `Cost: ${model.cost}, Quality: ${model.quality}`,
                        model: model
                    })),
                    {
                        placeHolder: 'Select AI model for current task',
                        matchOnDescription: true,
                        matchOnDetail: true
                    }
                );

                if (selectedModel) {
                    await modelSelector.selectModel(selectedModel.model);
                    vscode.window.showInformationMessage(`Selected model: ${selectedModel.label}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to select model: ${error}`);
            }
        }),

        vscode.commands.registerCommand('aimos.storeMemory', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor found');
                return;
            }

            const selection = editor.selection;
            const text = editor.document.getText(selection);
            
            if (!text) {
                vscode.window.showWarningMessage('No text selected');
                return;
            }

            const tags = await vscode.window.showInputBox({
                prompt: 'Enter tags for this memory (comma-separated)',
                placeHolder: 'e.g., code, implementation, feature'
            });

            if (tags) {
                try {
                    await memoryManager.storeMemory(text, tags.split(',').map(t => t.trim()));
                    vscode.window.showInformationMessage('Memory stored successfully!');
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to store memory: ${error}`);
                }
            }
        }),

        vscode.commands.registerCommand('aimos.retrieveMemory', async () => {
            const query = await vscode.window.showInputBox({
                prompt: 'Enter search query for memory retrieval',
                placeHolder: 'e.g., authentication, database, API'
            });

            if (query) {
                try {
                    const memories = await memoryManager.retrieveMemory(query);
                    const panel = vscode.window.createWebviewPanel(
                        'aimosMemoryResults',
                        'Memory Search Results',
                        vscode.ViewColumn.One,
                        {
                            enableScripts: true,
                            retainContextWhenHidden: true
                        }
                    );
                    panel.webview.html = getMemoryResultsWebviewContent(memories);
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to retrieve memory: ${error}`);
                }
            }
        }),

        vscode.commands.registerCommand('aimos.createPlan', async () => {
            const goal = await vscode.window.showInputBox({
                prompt: 'Enter goal for execution plan',
                placeHolder: 'e.g., Implement user authentication system'
            });

            if (goal) {
                try {
                    const plan = await crossModelManager.createPlan(goal);
                    const panel = vscode.window.createWebviewPanel(
                        'aimosExecutionPlan',
                        'Execution Plan',
                        vscode.ViewColumn.One,
                        {
                            enableScripts: true,
                            retainContextWhenHidden: true
                        }
                    );
                    panel.webview.html = getExecutionPlanWebviewContent(plan);
                } catch (error) {
                    vscode.window.showErrorMessage(`Failed to create plan: ${error}`);
                }
            }
        }),

        vscode.commands.registerCommand('aimos.trackConfidence', async () => {
            const task = await vscode.window.showInputBox({
                prompt: 'Enter task name for confidence tracking',
                placeHolder: 'e.g., Authentication implementation'
            });

            if (task) {
                const confidence = await vscode.window.showInputBox({
                    prompt: 'Enter confidence level (0.0 - 1.0)',
                    placeHolder: '0.85'
                });

                if (confidence) {
                    try {
                        await crossModelManager.trackConfidence(
                            task,
                            parseFloat(confidence),
                            'User input via Cursor add-on'
                        );
                        vscode.window.showInformationMessage(`Confidence tracked for: ${task}`);
                    } catch (error) {
                        vscode.window.showErrorMessage(`Failed to track confidence: ${error}`);
                    }
                }
            }
        })
    ];

    // Add commands to context
    context.subscriptions.push(...commands);

    // Initialize MCP connection
    mcpClient.initialize().then(() => {
        vscode.window.showInformationMessage('AIM-OS MCP server connected successfully!');
    }).catch((error) => {
        vscode.window.showErrorMessage(`Failed to connect to MCP server: ${error}`);
    });

    // Auto-refresh dashboard every 30 seconds
    setInterval(() => {
        dashboardProvider.refresh();
    }, 30000);
}

function getMemoryStatsWebviewContent(stats: any): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIM-OS Memory Statistics</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .stat-item { margin: 10px 0; padding: 10px; background: var(--vscode-editor-background); border-radius: 5px; }
            .stat-label { font-weight: bold; color: var(--vscode-foreground); }
            .stat-value { color: var(--vscode-textLink-foreground); }
        </style>
    </head>
    <body>
        <h1>AIM-OS Memory Statistics</h1>
        <div class="stat-item">
            <div class="stat-label">Total Atoms:</div>
            <div class="stat-value">${stats.total_atoms || 0}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Memory Usage:</div>
            <div class="stat-value">${stats.memory_usage || 'N/A'}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Last Updated:</div>
            <div class="stat-value">${new Date().toLocaleString()}</div>
        </div>
    </body>
    </html>
    `;
}

function getMemoryResultsWebviewContent(memories: any[]): string {
    const memoryItems = memories.map(memory => `
        <div class="memory-item">
            <h3>${memory.title || 'Memory Item'}</h3>
            <p>${memory.content}</p>
            <small>Tags: ${memory.tags ? memory.tags.join(', ') : 'None'}</small>
        </div>
    `).join('');

    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Memory Search Results</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .memory-item { margin: 15px 0; padding: 15px; background: var(--vscode-editor-background); border-radius: 5px; }
            .memory-item h3 { color: var(--vscode-foreground); margin-top: 0; }
            .memory-item p { color: var(--vscode-foreground); }
            .memory-item small { color: var(--vscode-descriptionForeground); }
        </style>
    </head>
    <body>
        <h1>Memory Search Results</h1>
        ${memoryItems || '<p>No memories found</p>'}
    </body>
    </html>
    `;
}

function getExecutionPlanWebviewContent(plan: any): string {
    return `
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Execution Plan</title>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .plan-step { margin: 10px 0; padding: 10px; background: var(--vscode-editor-background); border-radius: 5px; }
            .plan-step h3 { color: var(--vscode-foreground); margin-top: 0; }
            .plan-step p { color: var(--vscode-foreground); }
        </style>
    </head>
    <body>
        <h1>Execution Plan</h1>
        <div class="plan-step">
            <h3>Goal:</h3>
            <p>${plan.goal || 'No goal specified'}</p>
        </div>
        <div class="plan-step">
            <h3>Steps:</h3>
            <p>${plan.steps ? plan.steps.join('<br>') : 'No steps available'}</p>
        </div>
        <div class="plan-step">
            <h3>Estimated Duration:</h3>
            <p>${plan.estimated_duration || 'N/A'}</p>
        </div>
    </body>
    </html>
    `;
}

export function deactivate() {
    console.log('AIM-OS Cursor Add-on is now deactivated!');
}
