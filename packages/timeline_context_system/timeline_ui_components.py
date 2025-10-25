"""
Timeline UI Components - Amazing UI for Timeline Context System

This module provides React/TypeScript components for the Timeline Context System UI,
including interactive timeline visualization, context exploration, and AI-aided search.
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ZoomLevel(Enum):
    """Timeline zoom levels"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class ContextBubbleSize(Enum):
    """Context bubble sizes based on complexity"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


@dataclass
class TimelineEntry:
    """Timeline entry for UI display"""
    id: str
    timestamp: datetime
    summary: str
    task: str
    confidence_level: float
    context_complexity: int
    files_read: List[str]
    insights_gained: List[str]
    decisions_made: List[Dict]


@dataclass
class ContextDetail:
    """Context detail for UI display"""
    prompt_id: str
    timestamp: datetime
    user_input: str
    context_state: Dict[str, Any]
    files_read: List[str]
    conversation_history: List[Dict]
    mental_model: Dict[str, Any]
    confidence_levels: Dict[str, float]
    current_task: str
    context_budget_used: int
    tools_used: List[str]
    decisions_made: List[Dict]
    insights_gained: List[str]


# React/TypeScript Component Definitions
TIMELINE_UI_COMPONENTS = """
// Timeline UI Components for Timeline Context System

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Timeline, 
  TimelineItem, 
  TimelineSeparator, 
  TimelineConnector, 
  TimelineContent, 
  TimelineDot,
  TimelineOppositeContent
} from '@mui/lab';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Zoom,
  Fade,
  LinearProgress,
  CircularProgress,
  Button,
  TextField,
  Autocomplete,
  Slider,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Paper,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  ExpandMore as ExpandMoreIcon,
  Insights as InsightsIcon,
  Psychology as PsychologyIcon,
  Code as CodeIcon,
  Description as DescriptionIcon,
  Chat as ChatIcon,
  TrendingUp as TrendingUpIcon,
  Compare as CompareIcon,
  Timeline as TimelineViewIcon
} from '@mui/icons-material';

// Main Timeline View Component
const TimelineView: React.FC<{
  timelineData: TimelineEntry[];
  onEntryClick: (entry: TimelineEntry) => void;
  onEntryHover: (entry: TimelineEntry) => void;
}> = ({ timelineData, onEntryClick, onEntryHover }) => {
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>(ZoomLevel.DAY);
  const [selectedEntry, setSelectedEntry] = useState<TimelineEntry | null>(null);
  const [hoveredEntry, setHoveredEntry] = useState<TimelineEntry | null>(null);

  const handleEntryClick = (entry: TimelineEntry) => {
    setSelectedEntry(entry);
    onEntryClick(entry);
  };

  const handleEntryHover = (entry: TimelineEntry) => {
    setHoveredEntry(entry);
    onEntryHover(entry);
  };

  return (
    <Box sx={{ width: '100%', height: '100vh', overflow: 'auto' }}>
      {/* Timeline Header */}
      <TimelineHeader 
        zoomLevel={zoomLevel}
        onZoomChange={setZoomLevel}
        totalEntries={timelineData.length}
      />
      
      {/* Interactive Timeline */}
      <Timeline position="alternate">
        {timelineData.map((entry, index) => (
          <TimelineItem key={entry.id}>
            <TimelineOppositeContent>
              <Typography variant="caption" color="text.secondary">
                {formatTimestamp(entry.timestamp, zoomLevel)}
              </Typography>
            </TimelineOppositeContent>
            
            <TimelineSeparator>
              <TimelineDot 
                color={getConfidenceColor(entry.confidence_level)}
                variant={selectedEntry?.id === entry.id ? "filled" : "outlined"}
              >
                <ContextBubbleIcon complexity={entry.context_complexity} />
              </TimelineDot>
              {index < timelineData.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            
            <TimelineContent>
              <ContextBubble
                entry={entry}
                isSelected={selectedEntry?.id === entry.id}
                isHovered={hoveredEntry?.id === entry.id}
                onClick={() => handleEntryClick(entry)}
                onHover={() => handleEntryHover(entry)}
              />
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Box>
  );
};

// Context Bubble Component
const ContextBubble: React.FC<{
  entry: TimelineEntry;
  isSelected: boolean;
  isHovered: boolean;
  onClick: () => void;
  onHover: () => void;
}> = ({ entry, isSelected, isHovered, onClick, onHover }) => {
  const bubbleSize = getBubbleSize(entry.context_complexity);
  
  return (
    <Card
      sx={{
        maxWidth: bubbleSize,
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        transform: isHovered ? 'scale(1.05)' : 'scale(1)',
        boxShadow: isSelected ? 4 : 1,
        border: isSelected ? '2px solid #1976d2' : '1px solid #e0e0e0'
      }}
      onClick={onClick}
      onMouseEnter={onHover}
      onMouseLeave={() => {}}
    >
      <CardContent sx={{ p: 2 }}>
        {/* Task Badge */}
        <Chip 
          label={entry.task} 
          size="small" 
          color="primary" 
          sx={{ mb: 1 }}
        />
        
        {/* Summary */}
        <Typography variant="body2" sx={{ mb: 1 }}>
          {entry.summary}
        </Typography>
        
        {/* Context Complexity Indicator */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="caption" sx={{ mr: 1 }}>
            Complexity:
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={entry.context_complexity} 
            sx={{ flexGrow: 1, mr: 1 }}
          />
          <Typography variant="caption">
            {entry.context_complexity}%
          </Typography>
        </Box>
        
        {/* Confidence Level */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="caption" sx={{ mr: 1 }}>
            Confidence:
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={entry.confidence_level * 100} 
            color={getConfidenceColor(entry.confidence_level)}
            sx={{ flexGrow: 1, mr: 1 }}
          />
          <Typography variant="caption">
            {(entry.confidence_level * 100).toFixed(0)}%
          </Typography>
        </Box>
        
        {/* Quick Stats */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            {entry.files_read.length} files
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {entry.insights_gained.length} insights
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {entry.decisions_made.length} decisions
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

// Context Detail View Component
const ContextDetailView: React.FC<{
  contextDetail: ContextDetail;
  onClose: () => void;
}> = ({ contextDetail, onClose }) => {
  const [activeTab, setActiveTab] = useState(0);

  const tabData = [
    { label: 'Files Read', icon: <DescriptionIcon />, content: <FilesReadTab files={contextDetail.files_read} /> },
    { label: 'Conversation', icon: <ChatIcon />, content: <ConversationTab history={contextDetail.conversation_history} /> },
    { label: 'Mental Model', icon: <PsychologyIcon />, content: <MentalModelTab model={contextDetail.mental_model} /> },
    { label: 'Decisions', icon: <InsightsIcon />, content: <DecisionsTab decisions={contextDetail.decisions_made} /> },
    { label: 'Insights', icon: <TrendingUpIcon />, content: <InsightsTab insights={contextDetail.insights_gained} /> }
  ];

  return (
    <Paper sx={{ p: 3, maxWidth: 800, mx: 'auto', mt: 2 }}>
      {/* Context Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">
          Context Detail - {formatTimestamp(contextDetail.timestamp)}
        </Typography>
        <IconButton onClick={onClose}>
          <ExpandMoreIcon />
        </IconButton>
      </Box>
      
      {/* Context Summary */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            {contextDetail.current_task}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {contextDetail.user_input}
          </Typography>
          
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">
                Context Budget Used: {contextDetail.context_budget_used} tokens
              </Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="caption" color="text.secondary">
                Tools Used: {contextDetail.tools_used.join(', ')}
              </Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {/* Context Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          {tabData.map((tab, index) => (
            <Tab 
              key={index}
              label={tab.label}
              icon={tab.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Box>
      
      {/* Tab Content */}
      <Box sx={{ mt: 2 }}>
        {tabData[activeTab].content}
      </Box>
    </Paper>
  );
};

// AI-Aided Search Component
const AIAidedSearch: React.FC<{
  onSearch: (query: string) => void;
  onSuggestionClick: (suggestion: string) => void;
}> = ({ onSearch, onSuggestionClick }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    await onSearch(query);
    setIsSearching(false);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    onSuggestionClick(suggestion);
  };

  return (
    <Box sx={{ p: 2 }}>
      {/* Search Bar */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <TextField
          fullWidth
          placeholder="What was AI thinking when working on VIF?"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch(searchQuery)}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
            endAdornment: isSearching ? <CircularProgress size={20} /> : null
          }}
        />
        <Button 
          variant="contained" 
          onClick={() => handleSearch(searchQuery)}
          sx={{ ml: 1 }}
        >
          Search
        </Button>
      </Box>
      
      {/* AI Suggestions */}
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          AI Suggestions:
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {suggestions.map((suggestion, index) => (
            <Chip
              key={index}
              label={suggestion}
              onClick={() => handleSuggestionClick(suggestion)}
              variant="outlined"
              size="small"
            />
          ))}
        </Box>
      </Box>
      
      {/* Search Filters */}
      <SearchFilters />
    </Box>
  );
};

// Context Evolution Visualization Component
const ContextEvolutionChart: React.FC<{
  evolutionData: any[];
}> = ({ evolutionData }) => {
  return (
    <Card sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Context Evolution
      </Typography>
      
      {/* Context Growth Chart */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Context Growth Over Time
        </Typography>
        <ContextGrowthLine data={evolutionData} />
      </Box>
      
      {/* Insight Development Chart */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Insight Development
        </Typography>
        <InsightDevelopmentBars data={evolutionData} />
      </Box>
      
      {/* Confidence Evolution Chart */}
      <Box>
        <Typography variant="subtitle2" gutterBottom>
          Confidence Evolution
        </Typography>
        <ConfidenceEvolutionArea data={evolutionData} />
      </Box>
    </Card>
  );
};

// Timeline Comparison Tool Component
const TimelineComparison: React.FC<{
  timeline1: TimelineEntry[];
  timeline2: TimelineEntry[];
  onCompare: (comparison: any) => void;
}> = ({ timeline1, timeline2, onCompare }) => {
  const [comparisonResult, setComparisonResult] = useState<any>(null);

  const handleCompare = () => {
    const comparison = {
      timeline1: {
        totalEntries: timeline1.length,
        totalFiles: timeline1.reduce((sum, entry) => sum + entry.files_read.length, 0),
        totalInsights: timeline1.reduce((sum, entry) => sum + entry.insights_gained.length, 0),
        averageConfidence: timeline1.reduce((sum, entry) => sum + entry.confidence_level, 0) / timeline1.length
      },
      timeline2: {
        totalEntries: timeline2.length,
        totalFiles: timeline2.reduce((sum, entry) => sum + entry.files_read.length, 0),
        totalInsights: timeline2.reduce((sum, entry) => sum + entry.insights_gained.length, 0),
        averageConfidence: timeline2.reduce((sum, entry) => sum + entry.confidence_level, 0) / timeline2.length
      },
      differences: {
        entryDifference: timeline1.length - timeline2.length,
        fileDifference: timeline1.reduce((sum, entry) => sum + entry.files_read.length, 0) - 
                       timeline2.reduce((sum, entry) => sum + entry.files_read.length, 0),
        insightDifference: timeline1.reduce((sum, entry) => sum + entry.insights_gained.length, 0) - 
                          timeline2.reduce((sum, entry) => sum + entry.insights_gained.length, 0)
      }
    };
    
    setComparisonResult(comparison);
    onCompare(comparison);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Timeline Comparison
      </Typography>
      
      <Button 
        variant="contained" 
        startIcon={<CompareIcon />}
        onClick={handleCompare}
        sx={{ mb: 2 }}
      >
        Compare Timelines
      </Button>
      
      {comparisonResult && (
        <ComparisonResult result={comparisonResult} />
      )}
    </Box>
  );
};

// Helper Functions
const formatTimestamp = (timestamp: datetime, zoomLevel: ZoomLevel): string => {
  // Format timestamp based on zoom level
  switch (zoomLevel) {
    case ZoomLevel.HOUR:
      return timestamp.strftime('%H:%M');
    case ZoomLevel.DAY:
      return timestamp.strftime('%m/%d %H:%M');
    case ZoomLevel.WEEK:
      return timestamp.strftime('%m/%d');
    case ZoomLevel.MONTH:
      return timestamp.strftime('%b %d');
    case ZoomLevel.YEAR:
      return timestamp.strftime('%b %Y');
    default:
      return timestamp.strftime('%m/%d/%Y %H:%M');
  }
};

const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return '#4caf50'; // Green
  if (confidence >= 0.6) return '#ff9800'; // Orange
  if (confidence >= 0.4) return '#ff5722'; // Red
  return '#9e9e9e'; // Gray
};

const getBubbleSize = (complexity: number): string => {
  if (complexity >= 80) return '400px';
  if (complexity >= 60) return '350px';
  if (complexity >= 40) return '300px';
  return '250px';
};

const getConfidenceColor = (confidence: number): 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info' => {
  if (confidence >= 0.8) return 'success';
  if (confidence >= 0.6) return 'warning';
  if (confidence >= 0.4) return 'error';
  return 'info';
};

// Export components
export {
  TimelineView,
  ContextBubble,
  ContextDetailView,
  AIAidedSearch,
  ContextEvolutionChart,
  TimelineComparison
};
"""

# Python wrapper for React components
class TimelineUIComponents:
    """
    Python wrapper for Timeline UI Components
    """
    
    def __init__(self):
        self.components = TIMELINE_UI_COMPONENTS
    
    def get_timeline_view_component(self) -> str:
        """
        Get TimelineView React component
        """
        return self.components
    
    def get_context_detail_component(self) -> str:
        """
        Get ContextDetailView React component
        """
        return self.components
    
    def get_ai_search_component(self) -> str:
        """
        Get AIAidedSearch React component
        """
        return self.components
    
    def get_evolution_chart_component(self) -> str:
        """
        Get ContextEvolutionChart React component
        """
        return self.components
    
    def get_comparison_tool_component(self) -> str:
        """
        Get TimelineComparison React component
        """
        return self.components


# Example usage
if __name__ == "__main__":
    # Create UI components
    ui_components = TimelineUIComponents()
    
    # Get timeline view component
    timeline_component = ui_components.get_timeline_view_component()
    
    print("Timeline UI Components created successfully!")
    print(f"Component length: {len(timeline_component)} characters")
