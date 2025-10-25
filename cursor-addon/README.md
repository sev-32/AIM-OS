# AIM-OS Cursor Add-on

A comprehensive Visual Studio Code extension that provides UI elements and automation for AIM-OS MCP server integration, enabling cross-model consciousness and persistent memory in your development environment.

## Features

### 🧠 Cross-Model Consciousness
- **Toggle Cross-Model Mode**: Enable/disable cross-model consciousness features
- **Execution Planning**: Create and manage execution plans for complex tasks
- **Confidence Tracking**: Track confidence levels for tasks and operations
- **Knowledge Synthesis**: Synthesize knowledge from multiple AI models

### 💾 Memory System
- **Store Memory**: Store important code snippets, insights, and context
- **Retrieve Memory**: Search and retrieve relevant memories
- **Memory Statistics**: View detailed memory usage and statistics
- **Persistent Storage**: All memories persist across sessions

### 🤖 Model Selection
- **Smart Model Selection**: Automatically select optimal AI models based on task complexity
- **Model Comparison**: Compare different AI models and their capabilities
- **Cost Optimization**: Optimize costs through intelligent model selection
- **Quality Assurance**: Ensure quality through mathematical validation

### 📊 Dashboard
- **Real-time Statistics**: View system statistics and performance metrics
- **Status Monitoring**: Monitor cross-model consciousness status
- **Quick Actions**: Access common operations through the dashboard
- **Visual Interface**: Intuitive UI for all AIM-OS features

## Installation

1. **Install the extension**:
   ```bash
   # From the command palette
   Ctrl+Shift+P -> "Extensions: Install from VSIX"
   ```

2. **Configure MCP Server Path**:
   - Open VS Code settings (Ctrl+,)
   - Search for "AIM-OS"
   - Set the MCP server path to your AIM-OS installation

3. **Enable Cross-Model Consciousness**:
   - Open the AIM-OS dashboard from the activity bar
   - Toggle cross-model consciousness on/off as needed

## Usage

### Dashboard
Access the AIM-OS dashboard from the activity bar to:
- View system status and statistics
- Toggle cross-model consciousness
- Access memory operations
- Select AI models
- Monitor performance metrics

### Commands
Available commands (Ctrl+Shift+P):
- `AIM-OS: Show Dashboard` - Open the main dashboard
- `AIM-OS: Toggle Cross-Model Consciousness` - Enable/disable cross-model features
- `AIM-OS: Show Memory Statistics` - View memory usage statistics
- `AIM-OS: Show Model Selector` - Select AI models
- `AIM-OS: Store Memory` - Store selected text in memory
- `AIM-OS: Retrieve Memory` - Search and retrieve memories
- `AIM-OS: Create Execution Plan` - Create execution plans
- `AIM-OS: Track Confidence` - Track confidence for tasks

### Context Menu
Right-click on selected text to:
- Store the selection in memory
- Search for related memories
- Create execution plans based on the selection

## Configuration

### Settings
Configure the extension through VS Code settings:

```json
{
  "aimos.mcpServerPath": "path/to/run_mcp_cross_model.py",
  "aimos.crossModelEnabled": true,
  "aimos.autoModelSelection": true,
  "aimos.memoryAutoStore": true,
  "aimos.confidenceTracking": true
}
```

### MCP Server Integration
The extension integrates with the AIM-OS MCP server to provide:
- Real-time communication with AIM-OS systems
- Cross-model consciousness capabilities
- Persistent memory storage and retrieval
- Model selection and optimization
- Quality validation and confidence tracking

## Architecture

### Components
- **MCPClient**: Handles communication with the AIM-OS MCP server
- **CrossModelManager**: Manages cross-model consciousness features
- **MemoryManager**: Handles memory storage and retrieval operations
- **ModelSelector**: Manages AI model selection and optimization
- **DashboardProvider**: Provides the main dashboard interface

### Integration
The extension integrates with:
- **AIM-OS MCP Server**: Core functionality and cross-model operations
- **VS Code API**: UI elements, commands, and configuration
- **Cross-Model Consciousness**: Advanced AI model coordination
- **Persistent Memory**: Long-term storage and retrieval

## Development

### Building
```bash
npm install
npm run compile
```

### Testing
```bash
npm test
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Requirements

- **VS Code**: Version 1.74.0 or higher
- **AIM-OS**: MCP server running and accessible
- **Python**: Python 3.8+ for MCP server
- **Node.js**: Node.js 16+ for extension development

## Support

For issues, questions, or contributions:
- **Issues**: Report bugs and request features
- **Documentation**: Check the AIM-OS documentation
- **Community**: Join the AIM-OS community discussions

## License

This extension is part of the AIM-OS project and follows the same licensing terms.

---

**AIM-OS Cursor Add-on** - Bringing cross-model consciousness and persistent memory to your development environment! 🚀
