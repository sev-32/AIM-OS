import * as vscode from 'vscode';
import { CrossModelManager } from '../crossModel/crossModelManager';
import { MemoryManager } from '../memory/memoryManager';
import { ModelSelector } from '../models/modelSelector';

export class AIMOSDashboardProvider implements vscode.TreeDataProvider<DashboardItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<DashboardItem | undefined | null | void> = new vscode.EventEmitter<DashboardItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<DashboardItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(
        private crossModelManager: CrossModelManager,
        private memoryManager: MemoryManager,
        private modelSelector: ModelSelector
    ) {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: DashboardItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: DashboardItem): Thenable<DashboardItem[]> {
        if (!element) {
            return Promise.resolve(this.getRootItems());
        }
        return Promise.resolve(this.getChildItems(element));
    }

    private getRootItems(): DashboardItem[] {
        return [
            new DashboardItem(
                '🧠 Cross-Model Consciousness',
                vscode.TreeItemCollapsibleState.Collapsed,
                'crossModel',
                'Cross-model consciousness status and controls'
            ),
            new DashboardItem(
                '💾 Memory System',
                vscode.TreeItemCollapsibleState.Collapsed,
                'memory',
                'Memory statistics and operations'
            ),
            new DashboardItem(
                '🤖 Model Selection',
                vscode.TreeItemCollapsibleState.Collapsed,
                'models',
                'AI model selection and configuration'
            ),
            new DashboardItem(
                '📊 Statistics',
                vscode.TreeItemCollapsibleState.Collapsed,
                'stats',
                'System statistics and performance metrics'
            )
        ];
    }

    private async getChildItems(element: DashboardItem): Promise<DashboardItem[]> {
        switch (element.contextValue) {
            case 'crossModel':
                return this.getCrossModelItems();
            case 'memory':
                return this.getMemoryItems();
            case 'models':
                return this.getModelItems();
            case 'stats':
                return this.getStatsItems();
            default:
                return [];
        }
    }

    private async getCrossModelItems(): Promise<DashboardItem[]> {
        const isEnabled = this.crossModelManager.isCrossModelEnabled();
        return [
            new DashboardItem(
                `Status: ${isEnabled ? '✅ Enabled' : '❌ Disabled'}`,
                vscode.TreeItemCollapsibleState.None,
                'crossModelStatus',
                `Cross-model consciousness is ${isEnabled ? 'enabled' : 'disabled'}`
            ),
            new DashboardItem(
                'Toggle Cross-Model',
                vscode.TreeItemCollapsibleState.None,
                'toggleCrossModel',
                'Toggle cross-model consciousness on/off'
            ),
            new DashboardItem(
                'Create Execution Plan',
                vscode.TreeItemCollapsibleState.None,
                'createPlan',
                'Create a new execution plan'
            ),
            new DashboardItem(
                'Track Confidence',
                vscode.TreeItemCollapsibleState.None,
                'trackConfidence',
                'Track confidence for current task'
            )
        ];
    }

    private async getMemoryItems(): Promise<DashboardItem[]> {
        try {
            const stats = await this.memoryManager.getMemoryStats();
            return [
                new DashboardItem(
                    `Total Atoms: ${stats.total_atoms || 0}`,
                    vscode.TreeItemCollapsibleState.None,
                    'memoryStats',
                    'Total number of memory atoms'
                ),
                new DashboardItem(
                    `Memory Usage: ${stats.memory_usage || 'N/A'}`,
                    vscode.TreeItemCollapsibleState.None,
                    'memoryUsage',
                    'Current memory usage'
                ),
                new DashboardItem(
                    'Store Memory',
                    vscode.TreeItemCollapsibleState.None,
                    'storeMemory',
                    'Store selected text in memory'
                ),
                new DashboardItem(
                    'Retrieve Memory',
                    vscode.TreeItemCollapsibleState.None,
                    'retrieveMemory',
                    'Search and retrieve memories'
                ),
                new DashboardItem(
                    'View Memory Stats',
                    vscode.TreeItemCollapsibleState.None,
                    'viewMemoryStats',
                    'View detailed memory statistics'
                )
            ];
        } catch (error) {
            return [
                new DashboardItem(
                    '❌ Memory System Error',
                    vscode.TreeItemCollapsibleState.None,
                    'memoryError',
                    `Error: ${error}`
                )
            ];
        }
    }

    private async getModelItems(): Promise<DashboardItem[]> {
        try {
            const models = await this.modelSelector.getAvailableModels();
            const currentModel = await this.modelSelector.getCurrentModel();
            
            const items: DashboardItem[] = [
                new DashboardItem(
                    `Current Model: ${currentModel?.name || 'None'}`,
                    vscode.TreeItemCollapsibleState.None,
                    'currentModel',
                    `Currently selected model: ${currentModel?.name || 'None'}`
                ),
                new DashboardItem(
                    'Select Model',
                    vscode.TreeItemCollapsibleState.None,
                    'selectModel',
                    'Select a different AI model'
                )
            ];

            // Add available models
            models.forEach(model => {
                items.push(new DashboardItem(
                    `${model.name} (${model.cost})`,
                    vscode.TreeItemCollapsibleState.None,
                    'availableModel',
                    `Model: ${model.name}, Cost: ${model.cost}, Quality: ${model.quality}`
                ));
            });

            return items;
        } catch (error) {
            return [
                new DashboardItem(
                    '❌ Model Selection Error',
                    vscode.TreeItemCollapsibleState.None,
                    'modelError',
                    `Error: ${error}`
                )
            ];
        }
    }

    private async getStatsItems(): Promise<DashboardItem[]> {
        try {
            const stats = await this.memoryManager.getMemoryStats();
            return [
                new DashboardItem(
                    `Memory Atoms: ${stats.total_atoms || 0}`,
                    vscode.TreeItemCollapsibleState.None,
                    'statMemoryAtoms',
                    'Total memory atoms stored'
                ),
                new DashboardItem(
                    `Cross-Model Operations: ${stats.cross_model_operations || 0}`,
                    vscode.TreeItemCollapsibleState.None,
                    'statCrossModelOps',
                    'Total cross-model operations performed'
                ),
                new DashboardItem(
                    `Cost Savings: ${stats.cost_savings || '0%'}`,
                    vscode.TreeItemCollapsibleState.None,
                    'statCostSavings',
                    'Cost savings from cross-model consciousness'
                ),
                new DashboardItem(
                    `Quality Score: ${stats.quality_score || 'N/A'}`,
                    vscode.TreeItemCollapsibleState.None,
                    'statQualityScore',
                    'Current quality score'
                )
            ];
        } catch (error) {
            return [
                new DashboardItem(
                    '❌ Statistics Error',
                    vscode.TreeItemCollapsibleState.None,
                    'statsError',
                    `Error: ${error}`
                )
            ];
        }
    }
}

export class DashboardItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue: string,
        public readonly tooltip: string
    ) {
        super(label, collapsibleState);
        this.tooltip = tooltip;
        this.contextValue = contextValue;
        
        // Set icons based on context
        switch (contextValue) {
            case 'crossModel':
                this.iconPath = new vscode.ThemeIcon('brain');
                break;
            case 'memory':
                this.iconPath = new vscode.ThemeIcon('database');
                break;
            case 'models':
                this.iconPath = new vscode.ThemeIcon('robot');
                break;
            case 'stats':
                this.iconPath = new vscode.ThemeIcon('graph');
                break;
            case 'crossModelStatus':
                this.iconPath = new vscode.ThemeIcon('check');
                break;
            case 'toggleCrossModel':
                this.iconPath = new vscode.ThemeIcon('toggle-switch');
                break;
            case 'createPlan':
                this.iconPath = new vscode.ThemeIcon('list-ordered');
                break;
            case 'trackConfidence':
                this.iconPath = new vscode.ThemeIcon('target');
                break;
            case 'storeMemory':
                this.iconPath = new vscode.ThemeIcon('save');
                break;
            case 'retrieveMemory':
                this.iconPath = new vscode.ThemeIcon('search');
                break;
            case 'viewMemoryStats':
                this.iconPath = new vscode.ThemeIcon('bar-chart');
                break;
            case 'selectModel':
                this.iconPath = new vscode.ThemeIcon('arrow-swap');
                break;
            case 'currentModel':
                this.iconPath = new vscode.ThemeIcon('check-circle');
                break;
            case 'availableModel':
                this.iconPath = new vscode.ThemeIcon('circle');
                break;
            default:
                this.iconPath = new vscode.ThemeIcon('info');
        }

        // Set command based on context
        switch (contextValue) {
            case 'toggleCrossModel':
                this.command = {
                    command: 'aimos.toggleCrossModel',
                    title: 'Toggle Cross-Model'
                };
                break;
            case 'createPlan':
                this.command = {
                    command: 'aimos.createPlan',
                    title: 'Create Plan'
                };
                break;
            case 'trackConfidence':
                this.command = {
                    command: 'aimos.trackConfidence',
                    title: 'Track Confidence'
                };
                break;
            case 'storeMemory':
                this.command = {
                    command: 'aimos.storeMemory',
                    title: 'Store Memory'
                };
                break;
            case 'retrieveMemory':
                this.command = {
                    command: 'aimos.retrieveMemory',
                    title: 'Retrieve Memory'
                };
                break;
            case 'viewMemoryStats':
                this.command = {
                    command: 'aimos.showMemoryStats',
                    title: 'View Memory Stats'
                };
                break;
            case 'selectModel':
                this.command = {
                    command: 'aimos.showModelSelector',
                    title: 'Select Model'
                };
                break;
        }
    }
}
