"""
Emotional Salience Tracker (EST) - Sonnet's Vision Implementation

Implements the emotional richness components of IIS:
- AI/User resonance pairing
- Breakthrough consensus detection  
- Emotional cascade tracking
- Temporal emotion preservation
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

from .models import (
    EmotionalDetails, ResonancePair, BreakthroughMarker, 
    EmotionalCascade, TemporalEmotion
)

logger = logging.getLogger(__name__)


class EmotionalSalienceTracker:
    """
    Tracks emotional salience for intuition computation.
    
    Implements Sonnet's vision of emotional intelligence:
    - Bidirectional resonance (AI + User)
    - Breakthrough consensus detection
    - Emotional cascade linking
    - Temporal emotion preservation
    """
    
    def __init__(self):
        """Initialize the emotional salience tracker"""
        self.emotional_history = []
        self.cascade_links = {}  # idea_id -> cascade_info
        self.preserved_emotions = {}  # emotion_id -> temporal_emotion
        
        logger.info("EmotionalSalienceTracker initialized")
    
    def compute_emotional_salience(
        self,
        idea: str,
        context: Dict[str, Any],
        ai_response: Dict[str, Any],
        user_response: Dict[str, Any]
    ) -> EmotionalDetails:
        """
        Compute complete emotional salience for an idea.
        
        Args:
            idea: The idea being evaluated
            context: Contextual information
            ai_response: AI's emotional response
            user_response: User's emotional response
            
        Returns:
            Complete emotional details
        """
        # Extract AI resonance
        ai_resonance = self._extract_ai_resonance(ai_response)
        
        # Extract user resonance  
        user_resonance = self._extract_user_resonance(user_response)
        
        # Create resonance pair
        resonance_pair = ResonancePair(
            ai_resonance=ai_resonance,
            user_resonance=user_resonance
        )
        
        # Detect breakthrough
        breakthrough_marker = self._detect_breakthrough(
            idea, ai_response, user_response, resonance_pair
        )
        
        # Check for emotional cascade
        cascade = self._check_emotional_cascade(idea, context)
        
        # Preserve temporal emotion if breakthrough
        temporal_emotion = None
        if breakthrough_marker.is_breakthrough:
            temporal_emotion = self._preserve_temporal_emotion(
                idea, breakthrough_marker, ai_response, user_response
            )
        
        # Create emotional details
        emotional_details = EmotionalDetails(
            resonance_pair=resonance_pair,
            breakthrough_marker=breakthrough_marker,
            cascade=cascade,
            temporal_emotion=temporal_emotion
        )
        
        # Store in history
        self._store_emotional_details(emotional_details, idea)
        
        logger.debug(f"Computed emotional salience: {emotional_details.compute_emotional_salience():.4f}")
        
        return emotional_details
    
    def _extract_ai_resonance(self, ai_response: Dict[str, Any]) -> float:
        """Extract AI resonance from response"""
        # Look for explicit resonance indicators
        if "resonance" in ai_response:
            return float(ai_response["resonance"])
        
        # Look for emotional intensity
        if "emotional_intensity" in ai_response:
            return float(ai_response["emotional_intensity"])
        
        # Look for breakthrough feeling
        if "breakthrough_feeling" in ai_response:
            return float(ai_response["breakthrough_feeling"])
        
        # Look for inspiration level
        if "inspiration_level" in ai_response:
            return float(ai_response["inspiration_level"])
        
        # Default based on response characteristics
        response_text = ai_response.get("text", "").lower()
        
        # High resonance indicators
        high_indicators = [
            "breakthrough", "revolutionary", "profound", "amazing",
            "incredible", "brilliant", "genius", "perfect", "exactly",
            "this is it", "eureka", "wow", "mind-blowing"
        ]
        
        # Medium resonance indicators  
        medium_indicators = [
            "interesting", "good", "useful", "helpful", "valuable",
            "promising", "solid", "strong", "clear", "makes sense"
        ]
        
        # Count indicators
        high_count = sum(1 for indicator in high_indicators if indicator in response_text)
        medium_count = sum(1 for indicator in medium_indicators if indicator in response_text)
        
        # Compute resonance score
        if high_count > 0:
            return min(0.8 + (high_count * 0.05), 1.0)
        elif medium_count > 0:
            return min(0.5 + (medium_count * 0.1), 0.8)
        else:
            return 0.3  # Default low resonance
    
    def _extract_user_resonance(self, user_response: Dict[str, Any]) -> float:
        """Extract user resonance from response"""
        # Look for explicit resonance indicators
        if "resonance" in user_response:
            return float(user_response["resonance"])
        
        # Look for emotional intensity
        if "emotional_intensity" in user_response:
            return float(user_response["emotional_intensity"])
        
        # Look for satisfaction
        if "satisfaction" in user_response:
            return float(user_response["satisfaction"])
        
        # Look for engagement
        if "engagement" in user_response:
            return float(user_response["engagement"])
        
        # Default based on response characteristics
        response_text = user_response.get("text", "").lower()
        
        # High resonance indicators
        high_indicators = [
            "love", "amazing", "perfect", "exactly", "brilliant",
            "genius", "breakthrough", "revolutionary", "wow",
            "this is it", "eureka", "mind-blowing", "incredible"
        ]
        
        # Medium resonance indicators
        medium_indicators = [
            "good", "nice", "helpful", "useful", "interesting",
            "makes sense", "clear", "solid", "promising"
        ]
        
        # Count indicators
        high_count = sum(1 for indicator in high_indicators if indicator in response_text)
        medium_count = sum(1 for indicator in medium_indicators if indicator in response_text)
        
        # Compute resonance score
        if high_count > 0:
            return min(0.8 + (high_count * 0.05), 1.0)
        elif medium_count > 0:
            return min(0.5 + (medium_count * 0.1), 0.8)
        else:
            return 0.3  # Default low resonance
    
    def _detect_breakthrough(
        self,
        idea: str,
        ai_response: Dict[str, Any],
        user_response: Dict[str, Any],
        resonance_pair: ResonancePair
    ) -> BreakthroughMarker:
        """Detect breakthrough moments"""
        
        # Check for explicit breakthrough indicators
        ai_breakthrough = ai_response.get("breakthrough_feeling", 0.0)
        user_breakthrough = user_response.get("breakthrough_feeling", 0.0)
        
        # Check for breakthrough consensus
        breakthrough_consensus = (
            resonance_pair.breakthrough_consensus or
            (ai_breakthrough >= 0.8 and user_breakthrough >= 0.8)
        )
        
        # Compute breakthrough intensity
        breakthrough_intensity = max(ai_breakthrough, user_breakthrough)
        
        # Look for breakthrough quotes
        breakthrough_quote = ""
        if breakthrough_consensus:
            # Extract the most emotional quote
            ai_text = ai_response.get("text", "")
            user_text = user_response.get("text", "")
            
            # Find the most emotional sentence
            all_text = f"{ai_text} {user_text}"
            breakthrough_quote = self._extract_breakthrough_quote(all_text)
        
        # Create temporal emotion description
        temporal_emotion = self._create_temporal_emotion_description(
            breakthrough_consensus, breakthrough_intensity
        )
        
        return BreakthroughMarker(
            is_breakthrough=breakthrough_consensus,
            breakthrough_intensity=breakthrough_intensity,
            breakthrough_consensus=breakthrough_consensus,
            breakthrough_quote=breakthrough_quote,
            temporal_emotion=temporal_emotion
        )
    
    def _extract_breakthrough_quote(self, text: str) -> str:
        """Extract the most emotional quote from text"""
        sentences = text.split('.')
        
        # Look for sentences with high emotional content
        emotional_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue
            
            # Count emotional words
            emotional_words = [
                "breakthrough", "revolutionary", "profound", "amazing",
                "incredible", "brilliant", "genius", "perfect", "exactly",
                "this is it", "eureka", "wow", "mind-blowing", "love"
            ]
            
            emotional_count = sum(1 for word in emotional_words 
                                if word in sentence.lower())
            
            if emotional_count > 0:
                emotional_sentences.append((sentence, emotional_count))
        
        # Return the most emotional sentence
        if emotional_sentences:
            return max(emotional_sentences, key=lambda x: x[1])[0]
        
        return text[:100] + "..." if len(text) > 100 else text
    
    def _create_temporal_emotion_description(
        self, 
        breakthrough: bool, 
        intensity: float
    ) -> str:
        """Create temporal emotion description"""
        if breakthrough and intensity >= 0.9:
            return "Profound breakthrough moment - 'THIS IS IT!' feeling"
        elif breakthrough and intensity >= 0.8:
            return "Strong breakthrough feeling - revolutionary insight"
        elif intensity >= 0.7:
            return "High emotional resonance - very promising"
        elif intensity >= 0.5:
            return "Moderate emotional response - interesting"
        else:
            return "Low emotional response - neutral"
    
    def _check_emotional_cascade(
        self, 
        idea: str, 
        context: Dict[str, Any]
    ) -> Optional[EmotionalCascade]:
        """Check if this idea sparked an emotional cascade"""
        
        # Look for cascade indicators in context
        sparked_responses = context.get("sparked_responses", [])
        if not sparked_responses:
            return None
        
        # Compute original importance
        trigger_importance = context.get("original_importance", 0.3)
        
        # Compute cascade boost based on response quality
        cascade_boost = 1.0
        for response in sparked_responses:
            response_resonance = self._extract_ai_resonance(response)
            if response_resonance >= 0.8:
                cascade_boost += 0.5
            elif response_resonance >= 0.6:
                cascade_boost += 0.3
            elif response_resonance >= 0.4:
                cascade_boost += 0.1
        
        # Cap cascade boost at 3x
        cascade_boost = min(cascade_boost, 3.0)
        
        return EmotionalCascade(
            trigger_idea=idea,
            trigger_importance=trigger_importance,
            sparked_responses=sparked_responses,
            cascade_boost=cascade_boost
        )
    
    def _preserve_temporal_emotion(
        self,
        idea: str,
        breakthrough_marker: BreakthroughMarker,
        ai_response: Dict[str, Any],
        user_response: Dict[str, Any]
    ) -> TemporalEmotion:
        """Preserve temporal emotion forever"""
        
        emotion_id = str(uuid.uuid4())
        
        # Create emotional quote
        emotional_quote = breakthrough_marker.breakthrough_quote
        if not emotional_quote:
            emotional_quote = f"Breakthrough moment for: {idea[:50]}..."
        
        # Create emotional context
        emotional_context = (
            f"AI resonance: {ai_response.get('resonance', 'unknown')}, "
            f"User resonance: {user_response.get('resonance', 'unknown')}, "
            f"Breakthrough intensity: {breakthrough_marker.breakthrough_intensity:.2f}"
        )
        
        temporal_emotion = TemporalEmotion(
            timestamp=datetime.utcnow(),
            emotional_quote=emotional_quote,
            emotional_intensity=breakthrough_marker.breakthrough_intensity,
            emotional_context=emotional_context,
            preserved_forever=True
        )
        
        # Store forever
        self.preserved_emotions[emotion_id] = temporal_emotion
        
        logger.info(f"Preserved temporal emotion: {emotion_id}")
        
        return temporal_emotion
    
    def _store_emotional_details(
        self, 
        emotional_details: EmotionalDetails, 
        idea: str
    ) -> None:
        """Store emotional details in history"""
        self.emotional_history.append({
            "timestamp": datetime.utcnow(),
            "idea": idea,
            "emotional_details": emotional_details,
            "salience": emotional_details.compute_emotional_salience()
        })
        
        # Keep only last 1000 entries
        if len(self.emotional_history) > 1000:
            self.emotional_history = self.emotional_history[-1000:]
    
    def get_emotional_metrics(self) -> Dict[str, Any]:
        """Get emotional salience metrics"""
        if not self.emotional_history:
            return {"n_entries": 0}
        
        # Compute statistics
        saliences = [entry["salience"] for entry in self.emotional_history]
        breakthroughs = sum(1 for entry in self.emotional_history 
                          if entry["emotional_details"].breakthrough_marker.is_breakthrough)
        
        return {
            "n_entries": len(self.emotional_history),
            "avg_salience": sum(saliences) / len(saliences),
            "max_salience": max(saliences),
            "min_salience": min(saliences),
            "n_breakthroughs": breakthroughs,
            "breakthrough_rate": breakthroughs / len(self.emotional_history),
            "n_preserved_emotions": len(self.preserved_emotions)
        }
