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
        """Detect breakthrough moments with enhanced consensus detection"""
        
        # Check for explicit breakthrough indicators
        ai_breakthrough = ai_response.get("breakthrough_feeling", 0.0)
        user_breakthrough = user_response.get("breakthrough_feeling", 0.0)
        
        # Enhanced breakthrough consensus detection
        breakthrough_consensus = (
            resonance_pair.breakthrough_consensus or
            (ai_breakthrough >= 0.8 and user_breakthrough >= 0.8) or
            self._detect_implicit_breakthrough_consensus(ai_response, user_response)
        )
        
        # Compute breakthrough intensity with weighted average
        breakthrough_intensity = (
            ai_breakthrough * 0.4 + 
            user_breakthrough * 0.4 + 
            resonance_pair.consensus_strength * 0.2
        )
        
        # Look for breakthrough quotes with enhanced extraction
        breakthrough_quote = ""
        if breakthrough_consensus:
            # Extract the most emotional quote from both AI and user
            ai_text = ai_response.get("text", "")
            user_text = user_response.get("text", "")
            
            # Find the most emotional sentence from both
            all_quotes = []
            for text, source in [(ai_text, "AI"), (user_text, "User")]:
                if text:
                    sentences = text.split('.')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > 10:
                            # Count emotional words
                            emotional_words = [
                                "breakthrough", "revolutionary", "profound", "amazing",
                                "incredible", "brilliant", "genius", "perfect", "exactly",
                                "this is it", "eureka", "wow", "mind-blowing", "love",
                                "stunning", "remarkable", "extraordinary", "unprecedented"
                            ]
                            emotional_count = sum(1 for word in emotional_words 
                                                if word in sentence.lower())
                            if emotional_count > 0:
                                all_quotes.append((sentence, emotional_count, source))
            
            # Use the most emotional quote
            if all_quotes:
                best_quote = max(all_quotes, key=lambda x: x[1])
                breakthrough_quote = f"[{best_quote[2]}]: {best_quote[0]}"
            else:
                breakthrough_quote = f"Breakthrough moment for: {idea[:50]}..."
        
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
    
    def _detect_implicit_breakthrough_consensus(
        self,
        ai_response: Dict[str, Any],
        user_response: Dict[str, Any]
    ) -> bool:
        """Detect implicit breakthrough consensus from text analysis"""
        
        ai_text = ai_response.get("text", "").lower()
        user_text = user_response.get("text", "").lower()
        
        # Breakthrough indicators
        breakthrough_indicators = [
            "this is it", "breakthrough", "revolutionary", "profound",
            "amazing", "incredible", "brilliant", "genius", "perfect",
            "eureka", "wow", "mind-blowing", "unprecedented", "extraordinary"
        ]
        
        # Count breakthrough indicators in both responses
        ai_indicators = sum(1 for indicator in breakthrough_indicators 
                          if indicator in ai_text)
        user_indicators = sum(1 for indicator in breakthrough_indicators 
                            if indicator in user_text)
        
        # Both must have breakthrough indicators
        if ai_indicators == 0 or user_indicators == 0:
            return False
        
        # Both must have multiple indicators or strong single indicators
        strong_indicators = ["this is it", "breakthrough", "revolutionary", "profound"]
        ai_strong = sum(1 for indicator in strong_indicators if indicator in ai_text)
        user_strong = sum(1 for indicator in strong_indicators if indicator in user_text)
        
        # Consensus if both have strong indicators or multiple regular indicators
        return (
            (ai_strong > 0 and user_strong > 0) or
            (ai_indicators >= 2 and user_indicators >= 2)
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
        """Check if this idea sparked an emotional cascade with sophisticated analysis"""
        
        # Look for cascade indicators in context
        sparked_responses = context.get("sparked_responses", [])
        if not sparked_responses:
            return None
        
        # Compute original importance with context awareness
        trigger_importance = context.get("original_importance", 0.3)
        
        # Enhanced cascade boost computation
        cascade_boost = 1.0
        breakthrough_responses = 0
        high_resonance_responses = 0
        total_responses = len(sparked_responses)
        
        for response in sparked_responses:
            # Extract AI resonance from response
            ai_resonance = self._extract_ai_resonance(response)
            
            # Extract user resonance if available
            user_resonance = self._extract_user_resonance(response)
            
            # Compute combined resonance
            combined_resonance = (ai_resonance + user_resonance) / 2
            
            # Count breakthrough responses (both AI and user high resonance)
            if ai_resonance >= 0.8 and user_resonance >= 0.8:
                breakthrough_responses += 1
                cascade_boost += 0.8  # Strong breakthrough boost
            elif combined_resonance >= 0.8:
                high_resonance_responses += 1
                cascade_boost += 0.6  # High resonance boost
            elif combined_resonance >= 0.6:
                cascade_boost += 0.4  # Medium resonance boost
            elif combined_resonance >= 0.4:
                cascade_boost += 0.2  # Low resonance boost
        
        # Apply cascade quality multipliers
        if breakthrough_responses > 0:
            # Breakthrough consensus multiplier
            breakthrough_ratio = breakthrough_responses / total_responses
            cascade_boost *= (1.0 + breakthrough_ratio * 0.5)
        
        if high_resonance_responses > 0:
            # High resonance multiplier
            high_resonance_ratio = high_resonance_responses / total_responses
            cascade_boost *= (1.0 + high_resonance_ratio * 0.3)
        
        # Apply response volume multiplier (more responses = more impact)
        if total_responses > 3:
            volume_multiplier = 1.0 + (total_responses - 3) * 0.1
            cascade_boost *= volume_multiplier
        
        # Cap cascade boost at 5x (increased from 3x for more dramatic effects)
        cascade_boost = min(cascade_boost, 5.0)
        
        # Log cascade for analysis
        logger.info(f"Emotional cascade detected: {idea[:50]}... -> {total_responses} responses, boost: {cascade_boost:.2f}x")
        
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
        """Preserve temporal emotion forever with rich qualitative data"""
        
        emotion_id = str(uuid.uuid4())
        
        # Create emotional quote with enhanced extraction
        emotional_quote = breakthrough_marker.breakthrough_quote
        if not emotional_quote:
            # Extract the most emotional quote from AI and user responses
            ai_text = ai_response.get("text", "")
            user_text = user_response.get("text", "")
            
            # Find the most emotional sentence from both
            all_quotes = []
            for text in [ai_text, user_text]:
                if text:
                    sentences = text.split('.')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if len(sentence) > 10:  # Skip very short sentences
                            # Count emotional words
                            emotional_words = [
                                "breakthrough", "revolutionary", "profound", "amazing",
                                "incredible", "brilliant", "genius", "perfect", "exactly",
                                "this is it", "eureka", "wow", "mind-blowing", "love",
                                "incredible", "stunning", "remarkable", "extraordinary"
                            ]
                            emotional_count = sum(1 for word in emotional_words 
                                                if word in sentence.lower())
                            if emotional_count > 0:
                                all_quotes.append((sentence, emotional_count))
            
            # Use the most emotional quote
            if all_quotes:
                emotional_quote = max(all_quotes, key=lambda x: x[1])[0]
            else:
                emotional_quote = f"Breakthrough moment for: {idea[:50]}..."
        
        # Create rich emotional context
        ai_resonance = ai_response.get('resonance', 0.0)
        user_resonance = user_response.get('resonance', 0.0)
        ai_breakthrough = ai_response.get('breakthrough_feeling', 0.0)
        user_breakthrough = user_response.get('breakthrough_feeling', 0.0)
        
        emotional_context = (
            f"AI Resonance: {ai_resonance:.2f}, User Resonance: {user_resonance:.2f}, "
            f"AI Breakthrough: {ai_breakthrough:.2f}, User Breakthrough: {user_breakthrough:.2f}, "
            f"Breakthrough Intensity: {breakthrough_marker.breakthrough_intensity:.2f}, "
            f"Consensus: {breakthrough_marker.breakthrough_consensus}, "
            f"Idea: {idea[:100]}..."
        )
        
        # Create temporal emotion with enhanced data
        temporal_emotion = TemporalEmotion(
            timestamp=datetime.utcnow(),
            emotional_quote=emotional_quote,
            emotional_intensity=breakthrough_marker.breakthrough_intensity,
            emotional_context=emotional_context,
            preserved_forever=True
        )
        
        # Store forever with metadata
        self.preserved_emotions[emotion_id] = {
            'temporal_emotion': temporal_emotion,
            'metadata': {
                'idea': idea,
                'ai_response': ai_response,
                'user_response': user_response,
                'breakthrough_marker': breakthrough_marker,
                'preserved_at': datetime.utcnow().isoformat(),
                'emotion_id': emotion_id
            }
        }
        
        logger.info(f"Preserved temporal emotion: {emotion_id} - '{emotional_quote[:50]}...'")
        
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
        """Get comprehensive emotional salience metrics"""
        if not self.emotional_history:
            return {"n_entries": 0}
        
        # Compute statistics
        saliences = [entry["salience"] for entry in self.emotional_history]
        breakthroughs = sum(1 for entry in self.emotional_history 
                          if entry["emotional_details"].breakthrough_marker.is_breakthrough)
        
        # Compute cascade statistics
        cascades = sum(1 for entry in self.emotional_history 
                      if entry["emotional_details"].cascade is not None)
        
        # Compute resonance statistics
        ai_resonances = [entry["emotional_details"].resonance_pair.ai_resonance 
                        for entry in self.emotional_history]
        user_resonances = [entry["emotional_details"].resonance_pair.user_resonance 
                          for entry in self.emotional_history]
        consensus_strengths = [entry["emotional_details"].resonance_pair.consensus_strength 
                              for entry in self.emotional_history]
        
        # Compute breakthrough consensus statistics
        breakthrough_consensus = sum(1 for entry in self.emotional_history 
                                   if entry["emotional_details"].breakthrough_marker.breakthrough_consensus)
        
        return {
            "n_entries": len(self.emotional_history),
            "avg_salience": sum(saliences) / len(saliences),
            "max_salience": max(saliences),
            "min_salience": min(saliences),
            "n_breakthroughs": breakthroughs,
            "breakthrough_rate": breakthroughs / len(self.emotional_history),
            "n_breakthrough_consensus": breakthrough_consensus,
            "breakthrough_consensus_rate": breakthrough_consensus / len(self.emotional_history),
            "n_cascades": cascades,
            "cascade_rate": cascades / len(self.emotional_history),
            "avg_ai_resonance": sum(ai_resonances) / len(ai_resonances),
            "avg_user_resonance": sum(user_resonances) / len(user_resonances),
            "avg_consensus_strength": sum(consensus_strengths) / len(consensus_strengths),
            "n_preserved_emotions": len(self.preserved_emotions)
        }
    
    def get_preserved_emotions(self) -> Dict[str, Any]:
        """Get all preserved temporal emotions with metadata"""
        return {
            "n_preserved": len(self.preserved_emotions),
            "emotions": self.preserved_emotions
        }
    
    def get_breakthrough_quotes(self) -> List[str]:
        """Get all breakthrough quotes from preserved emotions"""
        quotes = []
        for emotion_data in self.preserved_emotions.values():
            if isinstance(emotion_data, dict) and 'temporal_emotion' in emotion_data:
                quote = emotion_data['temporal_emotion'].emotional_quote
                if quote:
                    quotes.append(quote)
        return quotes
