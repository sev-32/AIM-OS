import { MCPClient } from '../mcp/mcpClient';

export interface ModelInfo {
    id: string;
    name: string;
    description: string;
    cost: string;
    quality: string;
    capabilities: string[];
    provider: string;
    context_window: number;
    max_tokens: number;
}

export class ModelSelector {
    private currentModel: ModelInfo | null = null;
    private availableModels: ModelInfo[] = [];

    constructor(private mcpClient: MCPClient) {
        this.initializeModels();
    }

    private initializeModels(): void {
        // Initialize with common AI models
        this.availableModels = [
            {
                id: 'claude-3.5-sonnet',
                name: 'Claude 3.5 Sonnet',
                description: 'High-quality reasoning and analysis model',
                cost: 'High',
                quality: 'Excellent',
                capabilities: ['reasoning', 'analysis', 'writing', 'coding'],
                provider: 'Anthropic',
                context_window: 200000,
                max_tokens: 8192
            },
            {
                id: 'gpt-4o',
                name: 'GPT-4o',
                description: 'Advanced reasoning and multimodal capabilities',
                cost: 'High',
                quality: 'Excellent',
                capabilities: ['reasoning', 'analysis', 'writing', 'coding', 'vision'],
                provider: 'OpenAI',
                context_window: 128000,
                max_tokens: 4096
            },
            {
                id: 'gpt-4o-mini',
                name: 'GPT-4o Mini',
                description: 'Cost-effective model for most tasks',
                cost: 'Low',
                quality: 'Good',
                capabilities: ['reasoning', 'analysis', 'writing', 'coding'],
                provider: 'OpenAI',
                context_window: 128000,
                max_tokens: 16384
            },
            {
                id: 'claude-3-haiku',
                name: 'Claude 3 Haiku',
                description: 'Fast and efficient model for simple tasks',
                cost: 'Low',
                quality: 'Good',
                capabilities: ['reasoning', 'analysis', 'writing', 'coding'],
                provider: 'Anthropic',
                context_window: 200000,
                max_tokens: 4096
            },
            {
                id: 'gemini-pro',
                name: 'Gemini Pro',
                description: 'Google\'s advanced AI model',
                cost: 'Medium',
                quality: 'Good',
                capabilities: ['reasoning', 'analysis', 'writing', 'coding'],
                provider: 'Google',
                context_window: 1000000,
                max_tokens: 8192
            },
            {
                id: 'cerebras-llm',
                name: 'Cerebras LLM',
                description: 'High-performance model for complex tasks',
                cost: 'Medium',
                quality: 'Excellent',
                capabilities: ['reasoning', 'analysis', 'writing', 'coding'],
                provider: 'Cerebras',
                context_window: 2048,
                max_tokens: 2048
            }
        ];
    }

    async getAvailableModels(): Promise<ModelInfo[]> {
        return this.availableModels;
    }

    async getCurrentModel(): Promise<ModelInfo | null> {
        return this.currentModel;
    }

    async selectModel(model: ModelInfo): Promise<boolean> {
        try {
            this.currentModel = model;
            return true;
        } catch (error) {
            console.error('Failed to select model:', error);
            return false;
        }
    }

    async selectModelById(modelId: string): Promise<boolean> {
        const model = this.availableModels.find(m => m.id === modelId);
        if (model) {
            return await this.selectModel(model);
        }
        return false;
    }

    async getRecommendedModel(taskComplexity: number, budget: string = 'medium'): Promise<ModelInfo> {
        // Simple recommendation logic based on task complexity and budget
        if (taskComplexity > 0.8) {
            // High complexity tasks - recommend high-quality models
            if (budget === 'low') {
                return this.availableModels.find(m => m.id === 'gpt-4o-mini') || this.availableModels[0];
            } else if (budget === 'medium') {
                return this.availableModels.find(m => m.id === 'claude-3.5-sonnet') || this.availableModels[0];
            } else {
                return this.availableModels.find(m => m.id === 'gpt-4o') || this.availableModels[0];
            }
        } else if (taskComplexity > 0.5) {
            // Medium complexity tasks - recommend balanced models
            if (budget === 'low') {
                return this.availableModels.find(m => m.id === 'claude-3-haiku') || this.availableModels[0];
            } else if (budget === 'medium') {
                return this.availableModels.find(m => m.id === 'gemini-pro') || this.availableModels[0];
            } else {
                return this.availableModels.find(m => m.id === 'claude-3.5-sonnet') || this.availableModels[0];
            }
        } else {
            // Low complexity tasks - recommend cost-effective models
            if (budget === 'low') {
                return this.availableModels.find(m => m.id === 'claude-3-haiku') || this.availableModels[0];
            } else {
                return this.availableModels.find(m => m.id === 'gpt-4o-mini') || this.availableModels[0];
            }
        }
    }

    async getModelForTask(taskDescription: string, budget: string = 'medium'): Promise<ModelInfo> {
        // Analyze task complexity based on description
        const complexity = this.analyzeTaskComplexity(taskDescription);
        return await this.getRecommendedModel(complexity, budget);
    }

    private analyzeTaskComplexity(taskDescription: string): number {
        const description = taskDescription.toLowerCase();
        
        // High complexity indicators
        const highComplexityKeywords = [
            'complex', 'advanced', 'sophisticated', 'intricate', 'comprehensive',
            'architecture', 'system design', 'algorithm', 'optimization', 'performance',
            'security', 'authentication', 'authorization', 'encryption', 'cryptography'
        ];
        
        // Medium complexity indicators
        const mediumComplexityKeywords = [
            'implement', 'create', 'build', 'develop', 'integrate', 'connect',
            'database', 'api', 'service', 'component', 'module', 'feature'
        ];
        
        // Low complexity indicators
        const lowComplexityKeywords = [
            'simple', 'basic', 'easy', 'quick', 'fix', 'update', 'modify',
            'text', 'format', 'style', 'ui', 'button', 'form'
        ];
        
        let complexity = 0.5; // Default medium complexity
        
        // Check for high complexity keywords
        if (highComplexityKeywords.some(keyword => description.includes(keyword))) {
            complexity = 0.8;
        }
        // Check for medium complexity keywords
        else if (mediumComplexityKeywords.some(keyword => description.includes(keyword))) {
            complexity = 0.6;
        }
        // Check for low complexity keywords
        else if (lowComplexityKeywords.some(keyword => description.includes(keyword))) {
            complexity = 0.3;
        }
        
        return complexity;
    }

    async getModelComparison(): Promise<any[]> {
        return this.availableModels.map(model => ({
            name: model.name,
            cost: model.cost,
            quality: model.quality,
            capabilities: model.capabilities,
            provider: model.provider,
            context_window: model.context_window,
            max_tokens: model.max_tokens
        }));
    }

    async getModelStats(): Promise<any> {
        return {
            total_models: this.availableModels.length,
            current_model: this.currentModel?.name || 'None',
            providers: [...new Set(this.availableModels.map(m => m.provider))],
            cost_distribution: {
                low: this.availableModels.filter(m => m.cost === 'Low').length,
                medium: this.availableModels.filter(m => m.cost === 'Medium').length,
                high: this.availableModels.filter(m => m.cost === 'High').length
            }
        };
    }
}
