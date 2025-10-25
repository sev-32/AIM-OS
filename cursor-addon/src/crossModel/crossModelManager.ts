import { MCPClient } from '../mcp/mcpClient';

export class CrossModelManager {
    private crossModelEnabled: boolean = true;
    private currentTask: string | null = null;
    private currentConfidence: number = 0.0;

    constructor(private mcpClient: MCPClient) {}

    isCrossModelEnabled(): boolean {
        return this.crossModelEnabled;
    }

    toggleCrossModel(): boolean {
        this.crossModelEnabled = !this.crossModelEnabled;
        return this.crossModelEnabled;
    }

    async createPlan(goal: string, priority: string = 'medium'): Promise<any> {
        try {
            const plan = await this.mcpClient.createPlan(goal, priority);
            this.currentTask = goal;
            return plan;
        } catch (error) {
            console.error('Failed to create plan:', error);
            throw error;
        }
    }

    async trackConfidence(task: string, confidence: number, reasoning: string): Promise<any> {
        try {
            const result = await this.mcpClient.trackConfidence(task, confidence, reasoning);
            this.currentTask = task;
            this.currentConfidence = confidence;
            return result;
        } catch (error) {
            console.error('Failed to track confidence:', error);
            throw error;
        }
    }

    async synthesizeKnowledge(topics: string[]): Promise<any> {
        try {
            return await this.mcpClient.synthesizeKnowledge(topics);
        } catch (error) {
            console.error('Failed to synthesize knowledge:', error);
            throw error;
        }
    }

    getCurrentTask(): string | null {
        return this.currentTask;
    }

    getCurrentConfidence(): number {
        return this.currentConfidence;
    }

    async getCrossModelStats(): Promise<any> {
        try {
            const stats = await this.mcpClient.getMemoryStats();
            return {
                cross_model_enabled: this.crossModelEnabled,
                current_task: this.currentTask,
                current_confidence: this.currentConfidence,
                total_operations: stats.cross_model_operations || 0,
                cost_savings: stats.cost_savings || '0%',
                quality_score: stats.quality_score || 'N/A'
            };
        } catch (error) {
            console.error('Failed to get cross-model stats:', error);
            return {
                cross_model_enabled: this.crossModelEnabled,
                current_task: this.currentTask,
                current_confidence: this.currentConfidence,
                total_operations: 0,
                cost_savings: '0%',
                quality_score: 'N/A'
            };
        }
    }
}
