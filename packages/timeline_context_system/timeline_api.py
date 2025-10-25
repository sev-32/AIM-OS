"""
Timeline API - REST API for Timeline Context System

This module provides a FastAPI-based REST API for the Timeline Context System,
enabling programmatic access to timeline data and context information.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from enum import Enum

from .prompt_context_tracker import PromptContextTracker, ContextSnapshot, TimelineEntry


class TimelineAPI:
    """
    FastAPI application for Timeline Context System
    """
    
    def __init__(self, context_tracker: PromptContextTracker):
        self.context_tracker = context_tracker
        self.app = FastAPI(
            title="Timeline Context System API",
            description="API for accessing timeline context data and AI consciousness evolution",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "message": "Timeline Context System API",
                "version": "1.0.0",
                "status": "running"
            }
        
        @self.app.get("/timeline/summary")
        async def get_timeline_summary(
            start_date: Optional[datetime] = Query(None, description="Start date for summary"),
            end_date: Optional[datetime] = Query(None, description="End date for summary")
        ):
            """Get timeline summary for date range"""
            try:
                summary = self.context_tracker.get_timeline_summary(start_date, end_date)
                return {"success": True, "data": summary}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/entries")
        async def get_timeline_entries(
            start_date: Optional[datetime] = Query(None, description="Start date for entries"),
            end_date: Optional[datetime] = Query(None, description="End date for entries"),
            task: Optional[str] = Query(None, description="Filter by task"),
            limit: int = Query(100, description="Maximum number of entries to return")
        ):
            """Get timeline entries with optional filtering"""
            try:
                entries = self.context_tracker.timeline_entries
                
                # Filter by date range
                if start_date and end_date:
                    entries = [
                        entry for entry in entries
                        if start_date <= entry.timestamp <= end_date
                    ]
                
                # Filter by task
                if task:
                    entries = [
                        entry for entry in entries
                        if task.lower() in entry.context_index.get('active_tasks', '').lower()
                    ]
                
                # Limit results
                entries = entries[-limit:] if limit else entries
                
                # Convert to serializable format
                serialized_entries = [
                    {
                        "id": entry.prompt_id,
                        "timestamp": entry.timestamp.isoformat(),
                        "summary": entry.summary,
                        "task": entry.context_index.get('active_tasks', ''),
                        "confidence_level": entry.confidence_metrics.get('average_confidence', 0.0),
                        "context_complexity": len(entry.context_index.get('files_read', [])),
                        "files_read": entry.context_index.get('files_read', []),
                        "insights_gained": entry.context_index.get('insights_gained', []),
                        "decisions_made": entry.context_index.get('decisions_made', [])
                    }
                    for entry in entries
                ]
                
                return {"success": True, "data": serialized_entries, "count": len(serialized_entries)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/entry/{prompt_id}")
        async def get_timeline_entry(prompt_id: str = Path(..., description="Prompt ID")):
            """Get specific timeline entry by prompt ID"""
            try:
                if prompt_id not in self.context_tracker.context_snapshots:
                    raise HTTPException(status_code=404, detail="Timeline entry not found")
                
                snapshot = self.context_tracker.context_snapshots[prompt_id]
                
                # Convert to serializable format
                serialized_snapshot = {
                    "prompt_id": snapshot.prompt_id,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "user_input": snapshot.user_input,
                    "current_task": snapshot.current_task,
                    "context_budget_used": snapshot.context_budget_used,
                    "files_read": snapshot.files_read,
                    "conversation_history": snapshot.conversation_history,
                    "mental_model": snapshot.mental_model,
                    "confidence_levels": {k: v.value for k, v in snapshot.confidence_levels.items()},
                    "tools_used": snapshot.tools_used,
                    "decisions_made": snapshot.decisions_made,
                    "insights_gained": snapshot.insights_gained,
                    "context_evolution": snapshot.context_evolution
                }
                
                return {"success": True, "data": serialized_snapshot}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/context/{prompt_id}")
        async def get_context_detail(prompt_id: str = Path(..., description="Prompt ID")):
            """Get detailed context information for specific prompt"""
            try:
                if prompt_id not in self.context_tracker.context_snapshots:
                    raise HTTPException(status_code=404, detail="Context not found")
                
                snapshot = self.context_tracker.context_snapshots[prompt_id]
                
                # Create context detail response
                context_detail = {
                    "prompt_id": snapshot.prompt_id,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "user_input": snapshot.user_input,
                    "context_state": snapshot.context_state,
                    "files_read": snapshot.files_read,
                    "conversation_history": snapshot.conversation_history,
                    "mental_model": snapshot.mental_model,
                    "confidence_levels": {k: v.value for k, v in snapshot.confidence_levels.items()},
                    "current_task": snapshot.current_task,
                    "context_budget_used": snapshot.context_budget_used,
                    "tools_used": snapshot.tools_used,
                    "decisions_made": snapshot.decisions_made,
                    "insights_gained": snapshot.insights_gained
                }
                
                return {"success": True, "data": context_detail}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/search")
        async def search_timeline(
            query: str = Query(..., description="Search query"),
            start_date: Optional[datetime] = Query(None, description="Start date for search"),
            end_date: Optional[datetime] = Query(None, description="End date for search"),
            limit: int = Query(50, description="Maximum number of results")
        ):
            """Search timeline entries"""
            try:
                # Simple search implementation (can be enhanced with AI)
                results = []
                
                for entry in self.context_tracker.timeline_entries:
                    # Filter by date range
                    if start_date and end_date:
                        if not (start_date <= entry.timestamp <= end_date):
                            continue
                    
                    # Simple text search
                    if (query.lower() in entry.summary.lower() or
                        query.lower() in entry.context_index.get('active_tasks', '').lower() or
                        any(query.lower() in insight.lower() for insight in entry.context_index.get('insights_gained', []))):
                        results.append({
                            "id": entry.prompt_id,
                            "timestamp": entry.timestamp.isoformat(),
                            "summary": entry.summary,
                            "task": entry.context_index.get('active_tasks', ''),
                            "confidence_level": entry.confidence_metrics.get('average_confidence', 0.0),
                            "relevance_score": entry.relevance_score
                        })
                
                # Sort by relevance score
                results.sort(key=lambda x: x['relevance_score'], reverse=True)
                
                # Limit results
                results = results[:limit]
                
                return {"success": True, "data": results, "count": len(results)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/task/{task_name}")
        async def get_task_context(task_name: str = Path(..., description="Task name")):
            """Get all context snapshots for specific task"""
            try:
                task_contexts = self.context_tracker.find_task_context(task_name)
                
                # Convert to serializable format
                serialized_contexts = [
                    {
                        "prompt_id": snapshot.prompt_id,
                        "timestamp": snapshot.timestamp.isoformat(),
                        "user_input": snapshot.user_input,
                        "current_task": snapshot.current_task,
                        "context_budget_used": snapshot.context_budget_used,
                        "files_read": snapshot.files_read,
                        "insights_gained": snapshot.insights_gained,
                        "decisions_made": snapshot.decisions_made,
                        "confidence_levels": {k: v.value for k, v in snapshot.confidence_levels.items()}
                    }
                    for snapshot in task_contexts
                ]
                
                return {"success": True, "data": serialized_contexts, "count": len(serialized_contexts)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/file/{file_path:path}")
        async def get_file_context(file_path: str = Path(..., description="File path")):
            """Get all context snapshots when specific file was read"""
            try:
                file_contexts = self.context_tracker.find_file_context(file_path)
                
                # Convert to serializable format
                serialized_contexts = [
                    {
                        "prompt_id": snapshot.prompt_id,
                        "timestamp": snapshot.timestamp.isoformat(),
                        "user_input": snapshot.user_input,
                        "current_task": snapshot.current_task,
                        "context_budget_used": snapshot.context_budget_used,
                        "insights_gained": snapshot.insights_gained,
                        "decisions_made": snapshot.decisions_made
                    }
                    for snapshot in file_contexts
                ]
                
                return {"success": True, "data": serialized_contexts, "count": len(serialized_contexts)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/insight/{insight}")
        async def get_insight_context(insight: str = Path(..., description="Insight text")):
            """Get all context snapshots related to specific insight"""
            try:
                insight_contexts = self.context_tracker.find_insight_context(insight)
                
                # Convert to serializable format
                serialized_contexts = [
                    {
                        "prompt_id": snapshot.prompt_id,
                        "timestamp": snapshot.timestamp.isoformat(),
                        "user_input": snapshot.user_input,
                        "current_task": snapshot.current_task,
                        "context_budget_used": snapshot.context_budget_used,
                        "files_read": snapshot.files_read,
                        "decisions_made": snapshot.decisions_made
                    }
                    for snapshot in insight_contexts
                ]
                
                return {"success": True, "data": serialized_contexts, "count": len(serialized_contexts)}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/evolution/{task_name}")
        async def get_task_evolution(task_name: str = Path(..., description="Task name")):
            """Get context evolution for specific task"""
            try:
                task_contexts = self.context_tracker.find_task_context(task_name)
                
                if not task_contexts:
                    return {"success": True, "data": {"task": task_name, "evolution": []}}
                
                # Create evolution data
                evolution = {
                    "task": task_name,
                    "timeline": [
                        {
                            "timestamp": snapshot.timestamp.isoformat(),
                            "context_growth": len(snapshot.files_read),
                            "insights_gained": snapshot.insights_gained,
                            "confidence_levels": {k: v.value for k, v in snapshot.confidence_levels.items()}
                        }
                        for snapshot in task_contexts
                    ],
                    "context_growth": [
                        {
                            "timestamp": snapshot.timestamp.isoformat(),
                            "files_count": len(snapshot.files_read),
                            "context_budget": snapshot.context_budget_used
                        }
                        for snapshot in task_contexts
                    ],
                    "insight_development": [
                        {
                            "timestamp": snapshot.timestamp.isoformat(),
                            "insights": snapshot.insights_gained
                        }
                        for snapshot in task_contexts
                    ],
                    "confidence_evolution": [
                        {
                            "timestamp": snapshot.timestamp.isoformat(),
                            "confidence": {k: v.value for k, v in snapshot.confidence_levels.items()}
                        }
                        for snapshot in task_contexts
                    ]
                }
                
                return {"success": True, "data": evolution}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/timeline/statistics")
        async def get_timeline_statistics():
            """Get timeline statistics"""
            try:
                total_entries = len(self.context_tracker.timeline_entries)
                total_snapshots = len(self.context_tracker.context_snapshots)
                
                # Calculate statistics
                if total_entries > 0:
                    avg_confidence = sum(
                        entry.confidence_metrics.get('average_confidence', 0.0)
                        for entry in self.context_tracker.timeline_entries
                    ) / total_entries
                    
                    total_files = sum(
                        len(entry.context_index.get('files_read', []))
                        for entry in self.context_tracker.timeline_entries
                    )
                    
                    total_insights = sum(
                        len(entry.context_index.get('insights_gained', []))
                        for entry in self.context_tracker.timeline_entries
                    )
                    
                    total_decisions = sum(
                        len(entry.context_index.get('decisions_made', []))
                        for entry in self.context_tracker.timeline_entries
                    )
                else:
                    avg_confidence = 0.0
                    total_files = 0
                    total_insights = 0
                    total_decisions = 0
                
                statistics = {
                    "total_entries": total_entries,
                    "total_snapshots": total_snapshots,
                    "average_confidence": avg_confidence,
                    "total_files_read": total_files,
                    "total_insights_gained": total_insights,
                    "total_decisions_made": total_decisions,
                    "unique_tasks": len(set(
                        entry.context_index.get('active_tasks', '')
                        for entry in self.context_tracker.timeline_entries
                        if entry.context_index.get('active_tasks', '')
                    )),
                    "timeline_span": {
                        "start": min(
                            entry.timestamp for entry in self.context_tracker.timeline_entries
                        ).isoformat() if total_entries > 0 else None,
                        "end": max(
                            entry.timestamp for entry in self.context_tracker.timeline_entries
                        ).isoformat() if total_entries > 0 else None
                    }
                }
                
                return {"success": True, "data": statistics}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


# Pydantic models for request/response validation
class TimelineEntryResponse(BaseModel):
    """Response model for timeline entry"""
    id: str
    timestamp: str
    summary: str
    task: str
    confidence_level: float
    context_complexity: int
    files_read: List[str]
    insights_gained: List[str]
    decisions_made: List[Dict]


class ContextDetailResponse(BaseModel):
    """Response model for context detail"""
    prompt_id: str
    timestamp: str
    user_input: str
    context_state: Dict[str, Any]
    files_read: List[str]
    conversation_history: List[Dict]
    mental_model: Dict[str, Any]
    confidence_levels: Dict[str, str]
    current_task: str
    context_budget_used: int
    tools_used: List[str]
    decisions_made: List[Dict]
    insights_gained: List[str]


class TimelineSummaryResponse(BaseModel):
    """Response model for timeline summary"""
    total_prompts: int
    tasks_worked_on: List[str]
    files_read: List[str]
    insights_gained: List[str]
    total_context_used: int
    timeline_span: str
    average_confidence: float
    high_confidence_moments: int


# Example usage
if __name__ == "__main__":
    # Create context tracker
    from .prompt_context_tracker import PromptContextTracker
    
    context_tracker = PromptContextTracker()
    
    # Create API
    api = TimelineAPI(context_tracker)
    
    print("Timeline API created successfully!")
    print("Available endpoints:")
    print("- GET /timeline/summary")
    print("- GET /timeline/entries")
    print("- GET /timeline/entry/{prompt_id}")
    print("- GET /timeline/context/{prompt_id}")
    print("- GET /timeline/search")
    print("- GET /timeline/task/{task_name}")
    print("- GET /timeline/file/{file_path}")
    print("- GET /timeline/insight/{insight}")
    print("- GET /timeline/evolution/{task_name}")
    print("- GET /timeline/statistics")
