import { MCPClient } from '../mcp/mcpClient';

export interface MemoryItem {
    id: string;
    content: string;
    tags: string[];
    timestamp: string;
    quality_score?: number;
    confidence_score?: number;
}

export class MemoryManager {
    private memoryCache: MemoryItem[] = [];
    private lastUpdate: Date = new Date();

    constructor(private mcpClient: MCPClient) {}

    async storeMemory(content: string, tags: string[]): Promise<any> {
        try {
            const result = await this.mcpClient.storeMemory(content, tags);
            
            // Add to cache
            const memoryItem: MemoryItem = {
                id: result.atom_id || `memory_${Date.now()}`,
                content,
                tags,
                timestamp: new Date().toISOString(),
                quality_score: 0.8, // Default quality score
                confidence_score: 0.8 // Default confidence score
            };
            
            this.memoryCache.unshift(memoryItem);
            this.lastUpdate = new Date();
            
            return result;
        } catch (error) {
            console.error('Failed to store memory:', error);
            throw error;
        }
    }

    async retrieveMemory(query: string, limit: number = 10): Promise<MemoryItem[]> {
        try {
            const results = await this.mcpClient.retrieveMemory(query, limit);
            
            // Convert results to MemoryItem format
            const memoryItems: MemoryItem[] = results.map((result: any, index: number) => ({
                id: result.atom_id || `result_${index}`,
                content: result.content || result.text || 'No content available',
                tags: result.tags ? Object.keys(result.tags) : [],
                timestamp: result.timestamp || new Date().toISOString(),
                quality_score: result.quality_score || 0.8,
                confidence_score: result.confidence_score || 0.8
            }));
            
            return memoryItems;
        } catch (error) {
            console.error('Failed to retrieve memory:', error);
            throw error;
        }
    }

    async getMemoryStats(): Promise<any> {
        try {
            const stats = await this.mcpClient.getMemoryStats();
            return {
                total_atoms: stats.total_atoms || this.memoryCache.length,
                memory_usage: stats.memory_usage || 'N/A',
                last_updated: this.lastUpdate.toISOString(),
                cache_size: this.memoryCache.length,
                cross_model_operations: stats.cross_model_operations || 0,
                cost_savings: stats.cost_savings || '0%',
                quality_score: stats.quality_score || 'N/A'
            };
        } catch (error) {
            console.error('Failed to get memory stats:', error);
            return {
                total_atoms: this.memoryCache.length,
                memory_usage: 'N/A',
                last_updated: this.lastUpdate.toISOString(),
                cache_size: this.memoryCache.length,
                cross_model_operations: 0,
                cost_savings: '0%',
                quality_score: 'N/A'
            };
        }
    }

    getCachedMemories(): MemoryItem[] {
        return this.memoryCache;
    }

    clearCache(): void {
        this.memoryCache = [];
        this.lastUpdate = new Date();
    }

    async searchMemories(query: string, limit: number = 10): Promise<MemoryItem[]> {
        // First try the MCP server
        try {
            return await this.retrieveMemory(query, limit);
        } catch (error) {
            // Fallback to local cache search
            console.warn('MCP server unavailable, searching local cache:', error);
            return this.searchLocalCache(query, limit);
        }
    }

    private searchLocalCache(query: string, limit: number): MemoryItem[] {
        const queryLower = query.toLowerCase();
        const results = this.memoryCache.filter(item => 
            item.content.toLowerCase().includes(queryLower) ||
            item.tags.some(tag => tag.toLowerCase().includes(queryLower))
        );
        
        return results.slice(0, limit);
    }

    async getMemoryById(id: string): Promise<MemoryItem | null> {
        // First check cache
        const cached = this.memoryCache.find(item => item.id === id);
        if (cached) {
            return cached;
        }
        
        // If not in cache, try to retrieve from server
        try {
            const results = await this.retrieveMemory(id, 1);
            return results.length > 0 ? results[0] : null;
        } catch (error) {
            console.error('Failed to get memory by ID:', error);
            return null;
        }
    }

    async updateMemory(id: string, content: string, tags: string[]): Promise<boolean> {
        try {
            // For now, we'll store as a new memory since the MCP server doesn't have update functionality
            await this.storeMemory(content, tags);
            
            // Update cache
            const index = this.memoryCache.findIndex(item => item.id === id);
            if (index !== -1) {
                this.memoryCache[index].content = content;
                this.memoryCache[index].tags = tags;
                this.memoryCache[index].timestamp = new Date().toISOString();
            }
            
            return true;
        } catch (error) {
            console.error('Failed to update memory:', error);
            return false;
        }
    }

    async deleteMemory(id: string): Promise<boolean> {
        try {
            // Remove from cache
            const index = this.memoryCache.findIndex(item => item.id === id);
            if (index !== -1) {
                this.memoryCache.splice(index, 1);
                return true;
            }
            return false;
        } catch (error) {
            console.error('Failed to delete memory:', error);
            return false;
        }
    }
}
