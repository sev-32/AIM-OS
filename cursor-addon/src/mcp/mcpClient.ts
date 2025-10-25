import * as vscode from 'vscode';
import { spawn } from 'child_process';
import { EventEmitter } from 'events';

export interface MCPMessage {
    jsonrpc: string;
    id?: number;
    method?: string;
    params?: any;
    result?: any;
    error?: any;
}

export class MCPClient extends EventEmitter {
    private process: any = null;
    private messageId = 0;
    private pendingRequests = new Map<number, { resolve: Function; reject: Function }>();

    constructor() {
        super();
    }

    async initialize(): Promise<void> {
        return new Promise((resolve, reject) => {
            const config = vscode.workspace.getConfiguration('aimos');
            const mcpServerPath = config.get<string>('mcpServerPath') || 'run_mcp_cross_model.py';
            
            // Start the MCP server process
            this.process = spawn('python', ['-u', mcpServerPath], {
                cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath || process.cwd(),
                stdio: ['pipe', 'pipe', 'pipe']
            });

            this.process.stdout.on('data', (data: Buffer) => {
                const lines = data.toString().split('\n');
                for (const line of lines) {
                    if (line.trim()) {
                        try {
                            const message: MCPMessage = JSON.parse(line);
                            this.handleMessage(message);
                        } catch (error) {
                            console.error('Failed to parse MCP message:', error);
                        }
                    }
                }
            });

            this.process.stderr.on('data', (data: Buffer) => {
                console.error('MCP Server Error:', data.toString());
            });

            this.process.on('close', (code: number) => {
                console.log(`MCP Server process exited with code ${code}`);
                this.emit('disconnected');
            });

            this.process.on('error', (error: Error) => {
                console.error('MCP Server process error:', error);
                reject(error);
            });

            // Initialize the MCP connection
            this.sendRequest('initialize', {
                protocolVersion: '2024-11-05',
                capabilities: {
                    tools: {}
                },
                clientInfo: {
                    name: 'aimos-cursor-addon',
                    version: '1.0.0'
                }
            }).then(() => {
                resolve();
            }).catch(reject);
        });
    }

    private handleMessage(message: MCPMessage): void {
        if (message.id !== undefined) {
            const pending = this.pendingRequests.get(message.id);
            if (pending) {
                this.pendingRequests.delete(message.id);
                if (message.error) {
                    pending.reject(new Error(message.error.message || 'MCP Error'));
                } else {
                    pending.resolve(message.result);
                }
            }
        } else if (message.method) {
            this.emit('notification', message);
        }
    }

    async sendRequest(method: string, params?: any): Promise<any> {
        return new Promise((resolve, reject) => {
            const id = ++this.messageId;
            const message: MCPMessage = {
                jsonrpc: '2.0',
                id,
                method,
                params
            };

            this.pendingRequests.set(id, { resolve, reject });

            if (this.process && this.process.stdin) {
                this.process.stdin.write(JSON.stringify(message) + '\n');
            } else {
                reject(new Error('MCP Server not connected'));
            }

            // Timeout after 30 seconds
            setTimeout(() => {
                if (this.pendingRequests.has(id)) {
                    this.pendingRequests.delete(id);
                    reject(new Error('Request timeout'));
                }
            }, 30000);
        });
    }

    async listTools(): Promise<any[]> {
        try {
            const response = await this.sendRequest('tools/list');
            return response.tools || [];
        } catch (error) {
            console.error('Failed to list tools:', error);
            return [];
        }
    }

    async callTool(name: string, arguments_: any): Promise<any> {
        try {
            const response = await this.sendRequest('tools/call', {
                name,
                arguments: arguments_
            });
            return response;
        } catch (error) {
            console.error(`Failed to call tool ${name}:`, error);
            throw error;
        }
    }

    async storeMemory(content: string, tags: string[]): Promise<any> {
        return this.callTool('store_memory', {
            content,
            tags: tags.reduce((acc, tag, index) => {
                acc[tag] = 0.5 + (index * 0.1); // Simple tag weighting
                return acc;
            }, {} as Record<string, number>)
        });
    }

    async retrieveMemory(query: string, limit: number = 10): Promise<any[]> {
        const response = await this.callTool('retrieve_memory', {
            query,
            limit
        });
        return response.result || [];
    }

    async getMemoryStats(): Promise<any> {
        const response = await this.callTool('get_memory_stats', {});
        return response.result || {};
    }

    async createPlan(goal: string, priority: string = 'medium'): Promise<any> {
        const response = await this.callTool('create_plan', {
            goal,
            priority
        });
        return response.result || {};
    }

    async trackConfidence(task: string, confidence: number, reasoning: string): Promise<any> {
        const response = await this.callTool('track_confidence', {
            task,
            confidence,
            reasoning
        });
        return response.result || {};
    }

    async synthesizeKnowledge(topics: string[]): Promise<any> {
        const response = await this.callTool('synthesize_knowledge', {
            topics
        });
        return response.result || {};
    }

    disconnect(): void {
        if (this.process) {
            this.process.kill();
            this.process = null;
        }
        this.pendingRequests.clear();
    }
}
