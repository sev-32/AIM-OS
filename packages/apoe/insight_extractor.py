"""
InsightExtractor Component for Cross-Model Consciousness

This component extracts structured insights from smart model outputs and prepares them
for transfer to execution models. It handles context preparation, insight parsing,
confidence calculation, and quality validation.
"""

from __future__ import annotations

import logging
import re
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import uuid
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of insights"""
    PROBLEM_ANALYSIS = "problem_analysis"
    SOLUTION_APPROACH = "solution_approach"
    IMPLEMENTATION_GUIDANCE = "implementation_guidance"
    QUALITY_ASSURANCE = "quality_assurance"


class ParsingStrategy(Enum):
    """Insight parsing strategies"""
    STRUCTURED = "structured"
    FREEFORM = "freeform"
    HYBRID = "hybrid"


@dataclass
class InsightExtractionConfig:
    """Configuration for insight extraction"""
    # Parsing configuration
    parsing_strategy: ParsingStrategy = ParsingStrategy.STRUCTURED
    confidence_threshold: float = 0.7
    quality_threshold: float = 0.8
    
    # Context preparation
    max_context_length: int = 3000
    context_compression_ratio: float = 0.1
    
    # Validation rules
    required_fields: List[str] = field(default_factory=lambda: [
        "problem_analysis", "recommended_approach", "key_considerations", "success_criteria"
    ])
    
    # Quality metrics
    quality_weights: Dict[str, float] = field(default_factory=lambda: {
        "completeness": 0.3,
        "specificity": 0.25,
        "consistency": 0.25,
        "clarity": 0.2
    })


@dataclass
class CrossModelInsight:
    """Structured insight from smart model"""
    # Identity
    insight_id: str = field(default_factory=lambda: f"insight_{uuid.uuid4().hex}")
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "1.0.0"
    
    # Source Information
    source_model: str = ""
    source_confidence: float = 0.0
    source_reasoning: str = ""
    
    # Insight Content
    problem_analysis: str = ""
    recommended_approach: str = ""
    key_considerations: List[str] = field(default_factory=list)
    potential_risks: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Context Information
    minimal_context_used: str = ""
    context_summary: str = ""
    
    # Transfer Metadata
    transfer_confidence: float = 0.0
    complexity_score: float = 0.0
    estimated_effort: str = "medium"
    
    # Quality Assurance
    validation_checks: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    completeness_score: float = 0.0
    
    # Raw data
    raw_output: str = ""
    parsing_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of insight validation"""
    is_valid: bool = False
    quality_score: float = 0.0
    completeness_score: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextPreparer:
    """Prepare minimal context for smart model"""
    
    def __init__(self, config: InsightExtractionConfig):
        self.config = config
    
    def prepare_minimal_context(self, full_context: str, task_input: Any) -> str:
        """
        Prepare minimal context for smart model
        
        Args:
            full_context: Full context available
            task_input: Task input with problem description, constraints, goal
            
        Returns:
            Minimal context optimized for smart model
        """
        try:
            # Extract key information
            key_info = self._extract_key_information(full_context, task_input)
            
            # Compress context if needed
            if len(key_info) > self.config.max_context_length:
                key_info = self._compress_context(key_info)
            
            # Create minimal context template
            minimal_context = f"""
Problem: {task_input.problem_description}
Context: {key_info}
Constraints: {', '.join(task_input.constraints) if hasattr(task_input, 'constraints') else 'None'}
Goal: {task_input.goal if hasattr(task_input, 'goal') else 'Not specified'}
"""
            
            logger.info(f"Prepared minimal context: {len(minimal_context)} characters")
            return minimal_context.strip()
            
        except Exception as e:
            logger.error(f"Error preparing minimal context: {e}")
            return f"Problem: {task_input.problem_description if hasattr(task_input, 'problem_description') else 'Unknown'}"
    
    def _extract_key_information(self, full_context: str, task_input: Any) -> str:
        """Extract key information from full context"""
        try:
            # Simple keyword-based extraction
            keywords = []
            if hasattr(task_input, 'problem_description'):
                keywords.extend(task_input.problem_description.lower().split())
            if hasattr(task_input, 'constraints'):
                for constraint in task_input.constraints:
                    keywords.extend(constraint.lower().split())
            
            # Find sentences containing keywords
            sentences = full_context.split('.')
            relevant_sentences = []
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in keywords if len(keyword) > 3):
                    relevant_sentences.append(sentence.strip())
            
            # Return top relevant sentences
            max_sentences = 10
            return '. '.join(relevant_sentences[:max_sentences])
            
        except Exception as e:
            logger.error(f"Error extracting key information: {e}")
            return full_context[:1000]  # Fallback to first 1000 characters
    
    def _compress_context(self, context: str) -> str:
        """Compress context while preserving key information"""
        try:
            # Simple compression by taking first part and last part
            target_length = int(len(context) * self.config.context_compression_ratio)
            if len(context) <= target_length:
                return context
            
            # Take first 70% and last 30% of target length
            first_part = context[:int(target_length * 0.7)]
            last_part = context[-int(target_length * 0.3):]
            
            return first_part + "..." + last_part
            
        except Exception as e:
            logger.error(f"Error compressing context: {e}")
            return context[:self.config.max_context_length]


class InsightParser:
    """Parse insights from raw model output"""
    
    def __init__(self, config: InsightExtractionConfig):
        self.config = config
    
    def parse(self, raw_output: str, context: str) -> CrossModelInsight:
        """
        Parse raw output into structured insight
        
        Args:
            raw_output: Raw output from smart model
            context: Context used for the model
            
        Returns:
            Structured insight object
        """
        try:
            logger.info(f"Parsing insight from raw output: {len(raw_output)} characters")
            
            # Choose parsing strategy
            if self.config.parsing_strategy == ParsingStrategy.STRUCTURED:
                return self._parse_structured(raw_output, context)
            elif self.config.parsing_strategy == ParsingStrategy.FREEFORM:
                return self._parse_freeform(raw_output, context)
            else:  # HYBRID
                return self._parse_hybrid(raw_output, context)
                
        except Exception as e:
            logger.error(f"Error parsing insight: {e}")
            return self._create_fallback_insight(raw_output, context)
    
    def _parse_structured(self, raw_output: str, context: str) -> CrossModelInsight:
        """Parse structured output"""
        try:
            # Look for structured sections
            sections = self._extract_sections(raw_output)
            
            insight = CrossModelInsight(
                problem_analysis=sections.get("problem_analysis", ""),
                recommended_approach=sections.get("recommended_approach", ""),
                key_considerations=sections.get("key_considerations", []),
                potential_risks=sections.get("potential_risks", []),
                success_criteria=sections.get("success_criteria", []),
                minimal_context_used=context,
                raw_output=raw_output,
                parsing_metadata={"strategy": "structured", "sections_found": list(sections.keys())}
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Error in structured parsing: {e}")
            return self._create_fallback_insight(raw_output, context)
    
    def _parse_freeform(self, raw_output: str, context: str) -> CrossModelInsight:
        """Parse freeform output"""
        try:
            # Use NLP-like parsing for freeform text
            sentences = raw_output.split('.')
            
            # Identify problem analysis (usually first few sentences)
            problem_analysis = '. '.join(sentences[:3])
            
            # Identify recommended approach (sentences with action words)
            action_words = ["implement", "create", "build", "develop", "design", "use", "apply"]
            approach_sentences = []
            for sentence in sentences:
                if any(word in sentence.lower() for word in action_words):
                    approach_sentences.append(sentence)
            recommended_approach = '. '.join(approach_sentences[:2])
            
            # Extract considerations (sentences with "should", "must", "consider")
            consideration_words = ["should", "must", "consider", "important", "note"]
            considerations = []
            for sentence in sentences:
                if any(word in sentence.lower() for word in consideration_words):
                    considerations.append(sentence.strip())
            key_considerations = considerations[:5]
            
            # Extract risks (sentences with "beta", "risk", "potential", "might")
            risk_words = ["risk", "potential", "might", "could", "challenge"]
            risks = []
            for sentence in sentences:
                if any(word in sentence.lower() for word in risk_words):
                    risks.append(sentence.strip())
            potential_risks = risks[:3]
            
            # Extract success criteria (sentences with "success", "complete", "achieve")
            success_words = ["success", "complete", "achieve", "goal", "objective"]
            criteria = []
            for sentence in sentences:
                if any(word in sentence.lower() for word in success_words):
                    criteria.append(sentence.strip())
            success_criteria = criteria[:3]
            
            insight = CrossModelInsight(
                problem_analysis=problem_analysis,
                recommended_approach=recommended_approach,
                key_considerations=key_considerations,
                potential_risks=potential_risks,
                success_criteria=success_criteria,
                minimal_context_used=context,
                raw_output=raw_output,
                parsing_metadata={"strategy": "freeform", "sentences_processed": len(sentences)}
            )
            
            return insight
            
        except Exception as e:
            logger.error(f"Error in freeform parsing: {e}")
            return self._create_fallback_insight(raw_output, context)
    
    def _parse_hybrid(self, raw_output: str, context: str) -> CrossModelInsight:
        """Parse using hybrid approach"""
        try:
            # Try structured first, fallback to freeform
            structured_insight = self._parse_structured(raw_output, context)
            
            # If structured parsing didn't extract much, enhance with freeform
            if (len(structured_insight.problem_analysis) < 50 or 
                len(structured_insight.recommended_approach) < 50):
                
                freeform_insight = self._parse_freeform(raw_output, context)
                
                # Merge insights
                structured_insight.problem_analysis = (
                    structured_insight.problem_analysis or freeform_insight.problem_analysis
                )
                structured_insight.recommended_approach = (
                    structured_insight.recommended_approach or freeform_insight.recommended_approach
                )
                if not structured_insight.key_considerations:
                    structured_insight.key_considerations = freeform_insight.key_considerations
                if not structured_insight.potential_risks:
                    structured_insight.potential_risks = freeform_insight.potential_risks
                if not structured_insight.success_criteria:
                    structured_insight.success_criteria = freeform_insight.success_criteria
                
                structured_insight.parsing_metadata["strategy"] = "hybrid"
                structured_insight.parsing_metadata["enhanced"] = True
            
            return structured_insight
            
        except Exception as e:
            logger.error(f"Error in hybrid parsing: {e}")
            return self._create_fallback_insight(raw_output, context)
    
    def _extract_sections(self, raw_output: str) -> Dict[str, Any]:
        """Extract structured sections from raw output"""
        sections = {}
        
        # Common section headers
        section_patterns = {
            "problem_analysis": r"(?:problem|analysis|issue|challenge)[\s\S]*?(?=\n\n|\n[A-Z]|$)",
            "recommended_approach": r"(?:approach|solution|recommend|suggest)[\s\S]*?(?=\n\n|\n[A-Z]|$)",
            "key_considerations": r"(?:consider|factor|important|note)[\s\S]*?(?=\n\n|\n[A-Z]|$)",
            "potential_risks": r"(?:risk|challenge|concern|issue)[\s\S]*?(?=\n\n|\n[A-Z]|$)",
            "success_criteria": r"(?:success|criteria|goal|objective)[\s\S]*?(?=\n\n|\n[A-Z]|$)"
        }
        
        for section_name, pattern in section_patterns.items():
            matches = re.findall(pattern, raw_output, re.IGNORECASE)
            if matches:
                sections[section_name] = matches[0].strip()
        
        # Try to extract lists
        list_patterns = {
            "key_considerations": r"(?:consider|factor|important|note)[\s\S]*?(-|\*|\d+\.)[\s\S]*?(?=\n\n|\n[A-Z]|$)",
            "potential_risks": r"(?:risk|challenge|concern)[\s\S]*?(-|\*|\d+\.)[\s\S]*?(?=\n\n|\n[A-Z]|$)",
            "success_criteria": r"(?:success|criteria|goal)[\s\S]*?(-|\*|\d+\.)[\s\S]*?(?=\n\n|\n[A-Z]|$)"
        }
        
        for section_name, pattern in list_patterns.items():
            matches = re.findall(pattern, raw_output, re.IGNORECASE)
            if matches:
                # Extract list items
                list_text = matches[0]
                items = re.findall(r'[-*]\s*([^\n]+)', list_text)
                if items:
                    sections[section_name] = [item.strip() for item in items]
        
        return sections
    
    def _create_fallback_insight(self, raw_output: str, context: str) -> CrossModelInsight:
        """Create fallback insight when parsing fails"""
        return CrossModelInsight(
            problem_analysis=raw_output[:200] + "..." if len(raw_output) > 200 else raw_output,
            recommended_approach="See problem analysis above",
            key_considerations=["Review the analysis carefully"],
            potential_risks=["Parsing failed - manual review required"],
            success_criteria=["Manual validation required"],
            minimal_context_used=context,
            raw_output=raw_output,
            parsing_metadata={"strategy": "fallback", "error": "parsing_failed"}
        )


class ConfidenceCalculator:
    """Calculate confidence in insight quality"""
    
    def __init__(self, config: InsightExtractionConfig):
        self.config = config
    
    def calculate(self, raw_output: str, context: str) -> float:
        """
        Calculate confidence in insight quality
        
        Args:
            raw_output: Raw output from smart model
            context: Context used for the model
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            factors = []
            
            # Completeness factor
            completeness = self._assess_completeness(raw_output)
            factors.append(completeness * 0.3)
            
            # Specificity factor
            specificity = self._assess_specificity(raw_output)
            factors.append(specificity * 0.25)
            
            # Consistency factor
            consistency = self._assess_consistency(raw_output, context)
            factors.append(consistency * 0.25)
            
            # Clarity factor
            clarity = self._assess_clarity(raw_output)
            factors.append(clarity * 0.2)
            
            confidence = sum(factors)
            
            logger.info(f"Confidence calculation: completeness={completeness:.2f}, "
                       f"specificity={specificity:.2f}, consistency={consistency:.2f}, "
                       f"clarity={clarity:.2f}, total={confidence:.2f}")
            
            return min(max(confidence, 0.0), 1.0)  # Clamp to [0.0, 1.0]
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5  # Default confidence
    
    def _assess_completeness(self, raw_output: str) -> float:
        """Assess completeness of the output"""
        try:
            # Check for key elements
            key_elements = ["problem", "solution", "approach", "consider", "risk", "success"]
            found_elements = sum(1 for element in key_elements if element in raw_output.lower())
            
            completeness = found_elements / len(key_elements)
            
            # Check length (not too short, not too long)
            length_score = min(len(raw_output) / 500, 1.0)  # Optimal around 500 chars
            if len(raw_output) > 2000:
                length_score = max(0.5, 1.0 - (len(raw_output) - 2000) / 3000)
            
            return (completeness + length_score) / 2
            
        except Exception as e:
            logger.error(f"Error assessing completeness: {e}")
            return 0.5
    
    def _assess_specificity(self, raw_output: str) -> float:
        """Assess specificity of the output"""
        try:
            # Check for specific technical terms
            technical_terms = ["api", "database", "authentication", "security", "performance", 
                             "scalability", "architecture", "implementation", "deployment"]
            found_terms = sum(1 for term in technical_terms if term in raw_output.lower())
            
            # Check for specific numbers or metrics
            numbers = re.findall(r'\d+', raw_output)
            has_metrics = len(numbers) > 0
            
            # Check for specific examples
            examples = ["for example", "such as", "like", "instance"]
            has_examples = any(example in raw_output.lower() for example in examples)
            
            specificity = (found_terms / len(technical_terms) + 
                          (1.0 if has_metrics else 0.0) + 
                          (1.0 if has_examples else 0.0)) / 3
            
            return min(max(specificity, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error assessing specificity: {e}")
            return 0.5
    
    def _assess_consistency(self, raw_output: str, context: str) -> float:
        """Assess consistency with context"""
        try:
            # Extract keywords from context
            context_words = set(context.lower().split())
            output_words = set(raw_output.lower().split())
            
            # Check overlap
            overlap = len(context_words.intersection(output_words))
            total_context_words = len(context_words)
            
            if total_context_words > 0:
                consistency = overlap / total_context_words
            else:
                consistency = 0.5
            
            # Check for contradictions (simple heuristic)
            contradiction_words = ["but", "however", "although", "despite", "contradict"]
            contradictions = sum(1 for word in contradiction_words if word in raw_output.lower())
            
            # Reduce consistency if too many contradictions
            if contradictions > 2:
                consistency *= 0.8
            
            return min(max(consistency, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error assessing consistency: {e}")
            return 0.5
    
    def _assess_clarity(self, raw_output: str) -> float:
        """Assess clarity of the output"""
        try:
            # Check sentence structure
            sentences = raw_output.split('.')
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
            
            # Optimal sentence length is 10-20 words
            if 10 <= avg_sentence_length <= 20:
                length_score = 1.0
            elif avg_sentence_length < 10:
                length_score = avg_sentence_length / 10
            else:
                length_score = max(0.5, 1.0 - (avg_sentence_length - 20) / 20)
            
            # Check for clear structure
            structure_words = ["first", "second", "next", "then", "finally", "therefore", "thus"]
            structure_score = sum(1 for word in structure_words if word in raw_output.lower()) / 10
            structure_score = min(structure_score, 1.0)
            
            # Check for jargon vs. plain language
            jargon_words = ["utilize", "facilitate", "implement", "optimize", "leverage"]
            plain_words = ["use", "help", "build", "improve", "use"]
            jargon_count = sum(1 for word in jargon_words if word in raw_output.lower())
            plain_count = sum(1 for word in plain_words if word in raw_output.lower())
            
            if jargon_count + plain_count > 0:
                clarity_score = plain_count / (jargon_count + plain_count)
            else:
                clarity_score = 0.5
            
            return (length_score + structure_score + clarity_score) / 3
            
        except Exception as e:
            logger.error(f"Error assessing clarity: {e}")
            return 0.5


class InsightValidator:
    """Validate insight quality and completeness"""
    
    def __init__(self, config: InsightExtractionConfig):
        self.config = config
    
    def validate(self, insight: CrossModelInsight) -> ValidationResult:
        """
        Validate insight quality and completeness
        
        Args:
            insight: Insight to validate
            
        Returns:
            Validation result with quality scores and errors
        """
        try:
            errors = []
            warnings = []
            
            # Check completeness
            completeness_score = self._check_completeness(insight)
            if completeness_score < 0.8:
                errors.append(f"Completeness score too low: {completeness_score:.2f}")
            
            # Check quality
            quality_score = self._check_quality(insight)
            if quality_score < self.config.quality_threshold:
                errors.append(f"Quality score too low: {quality_score:.2f}")
            
            # Check required fields
            missing_fields = []
            for field in self.config.required_fields:
                if not getattr(insight, field, None):
                    missing_fields.append(field)
            
            if missing_fields:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Check field quality
            if len(insight.problem_analysis) < 50:
                warnings.append("Problem analysis is too short")
            
            if len(insight.recommended_approach) < 50:
                warnings.append("Recommended approach is too short")
            
            if len(insight.key_considerations) < 2:
                warnings.append("Too few key considerations")
            
            # Calculate overall validation result
            is_valid = len(errors) == 0 and completeness_score >= 0.8 and quality_score >= self.config.quality_threshold
            
            result = ValidationResult(
                is_valid=is_valid,
                quality_score=quality_score,
                completeness_score=completeness_score,
                errors=errors,
                warnings=warnings,
                metadata={
                    "validation_checks": len(self.config.required_fields),
                    "errors_count": len(errors),
                    "warnings_count": len(warnings)
                }
            )
            
            logger.info(f"Insight validation: valid={is_valid}, quality={quality_score:.2f}, "
                       f"completeness={completeness_score:.2f}, errors={len(errors)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating insight: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
    
    def _check_completeness(self, insight: CrossModelInsight) -> float:
        """Check completeness of insight"""
        try:
            fields_to_check = [
                ("problem_analysis", insight.problem_analysis),
                ("recommended_approach", insight.recommended_approach),
                ("key_considerations", insight.key_considerations),
                ("potential_risks", insight.potential_risks),
                ("success_criteria", insight.success_criteria)
            ]
            
            completed_fields = 0
            for field_name, field_value in fields_to_check:
                if field_value:
                    if isinstance(field_value, list):
                        if len(field_value) > 0:
                            completed_fields += 1
                    else:
                        if len(str(field_value).strip()) > 10:
                            completed_fields += 1
            
            completeness = completed_fields / len(fields_to_check)
            
            # Update insight completeness score
            insight.completeness_score = completeness
            
            return completeness
            
        except Exception as e:
            logger.error(f"Error checking completeness: {e}")
            return 0.0
    
    def _check_quality(self, insight: CrossModelInsight) -> float:
        """Check quality of insight"""
        try:
            quality_factors = []
            
            # Check problem analysis quality
            if insight.problem_analysis:
                problem_quality = self._assess_text_quality(insight.problem_analysis)
                quality_factors.append(problem_quality * self.config.quality_weights["completeness"])
            
            # Check recommended approach quality
            if insight.recommended_approach:
                approach_quality = self._assess_text_quality(insight.recommended_approach)
                quality_factors.append(approach_quality * self.config.quality_weights["specificity"])
            
            # Check considerations quality
            if insight.key_considerations:
                considerations_quality = self._assess_list_quality(insight.key_considerations)
                quality_factors.append(considerations_quality * self.config.quality_weights["consistency"])
            
            # Check risks quality
            if insight.potential_risks:
                risks_quality = self._assess_list_quality(insight.potential_risks)
                quality_factors.append(risks_quality * self.config.quality_weights["clarity"])
            
            # Check success criteria quality
            if insight.success_criteria:
                criteria_quality = self._assess_list_quality(insight.success_criteria)
                quality_factors.append(criteria_quality * self.config.quality_weights["completeness"])
            
            if quality_factors:
                overall_quality = sum(quality_factors) / len(quality_factors)
            else:
                overall_quality = 0.0
            
            # Update insight quality score
            insight.quality_score = overall_quality
            
            return overall_quality
            
        except Exception as e:
            logger.error(f"Error checking quality: {e}")
            return 0.0
    
    def _assess_text_quality(self, text: str) -> float:
        """Assess quality of text content"""
        try:
            if not text or len(text.strip()) < 10:
                return 0.0
            
            # Check length (not too short, not too long)
            length_score = min(len(text) / 200, 1.0)  # Optimal around 200 chars
            if len(text) > 1000:
                length_score = max(0.5, 1.0 - (len(text) - 1000) / 2000)
            
            # Check for specific terms
            specific_terms = ["because", "therefore", "specifically", "for example", "such as"]
            specificity_score = sum(1 for term in specific_terms if term in text.lower()) / len(specific_terms)
            
            # Check for action words
            action_words = ["implement", "create", "build", "develop", "design", "use", "apply"]
            action_score = sum(1 for word in action_words if word in text.lower()) / len(action_words)
            
            return (length_score + specificity_score + action_score) / 3
            
        except Exception as e:
            logger.error(f"Error assessing text quality: {e}")
            return 0.5
    
    def _assess_list_quality(self, items: List[str]) -> float:
        """Assess quality of list items"""
        try:
            if not items:
                return 0.0
            
            quality_scores = []
            for item in items:
                if isinstance(item, str) and len(item.strip()) > 5:
                    quality_scores.append(self._assess_text_quality(item))
                else:
                    quality_scores.append(0.0)
            
            return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error assessing list quality: {e}")
            return 0.5


class InsightExtractor:
    """Extract structured insights from smart model outputs"""
    
    def __init__(self, config: InsightExtractionConfig):
        self.config = config
        self.context_preparer = ContextPreparer(config)
        self.parser = InsightParser(config)
        self.validator = InsightValidator(config)
        self.confidence_calculator = ConfidenceCalculator(config)
        
        logger.info("InsightExtractor initialized with configuration")
    
    def extract_insight(self, raw_output: str, context: str, source_model: str = "") -> CrossModelInsight:
        """
        Extract structured insight from raw output
        
        Args:
            raw_output: Raw output from smart model
            context: Context used for the model
            source_model: Source model identifier
            
        Returns:
            Structured insight object
        """
        try:
            logger.info(f"Extracting insight from {len(raw_output)} character output")
            
            # Parse the output
            parsed_insight = self.parser.parse(raw_output, context)
            
            # Calculate confidence
            confidence = self.confidence_calculator.calculate(raw_output, context)
            
            # Validate insight
            validation_result = self.validator.validate(parsed_insight)
            
            # Update insight with metadata
            parsed_insight.source_model = source_model
            parsed_insight.source_confidence = confidence
            parsed_insight.source_reasoning = f"Confidence calculated based on completeness, specificity, consistency, and clarity"
            parsed_insight.validation_checks = ["completeness_check", "quality_check", "field_validation"]
            
            # Set complexity and effort estimates
            parsed_insight.complexity_score = self._estimate_complexity(parsed_insight)
            parsed_insight.estimated_effort = self._estimate_effort(parsed_insight)
            
            logger.info(f"Insight extraction completed: quality={parsed_insight.quality_score:.2f}, "
                       f"confidence={confidence:.2f}, valid={validation_result.is_valid}")
            
            return parsed_insight
            
        except Exception as e:
            logger.error(f"Error extracting insight: {e}")
            return self._create_error_insight(raw_output, context, source_model, str(e))
    
    def prepare_minimal_context(self, full_context: str, task_input: Any) -> str:
        """Prepare minimal context for smart model"""
        return self.context_preparer.prepare_minimal_context(full_context, task_input)
    
    def _estimate_complexity(self, insight: CrossModelInsight) -> float:
        """Estimate complexity of the insight"""
        try:
            # Simple complexity estimation based on content
            complexity_factors = []
            
            # Length factor
            total_length = (len(insight.problem_analysis) + len(insight.recommended_approach) + 
                          sum(len(item) for item in insight.key_considerations))
            length_factor = min(total_length / 1000, 1.0)
            complexity_factors.append(length_factor)
            
            # Technical terms factor
            technical_terms = ["api", "database", "authentication", "security", "performance", 
                             "scalability", "architecture", "implementation", "deployment"]
            tech_term_count = sum(1 for term in technical_terms 
                                if term in insight.problem_analysis.lower() or 
                                term in insight.recommended_approach.lower())
            tech_factor = min(tech_term_count / 5, 1.0)
            complexity_factors.append(tech_factor)
            
            # Considerations factor
            considerations_factor = min(len(insight.key_considerations) / 5, 1.0)
            complexity_factors.append(considerations_factor)
            
            return sum(complexity_factors) / len(complexity_factors)
            
        except Exception as e:
            logger.error(f"Error estimating complexity: {e}")
            return 0.5
    
    def _estimate_effort(self, insight: CrossModelInsight) -> str:
        """Estimate effort required for implementation"""
        try:
            complexity = self._estimate_complexity(insight)
            
            if complexity < 0.3:
                return "low"
            elif complexity < 0.7:
                return "medium"
            else:
                return "high"
                
        except Exception as e:
            logger.error(f"Error estimating effort: {e}")
            return "medium"
    
    def _create_error_insight(self, raw_output: str, context: str, source_model: str, error: str) -> CrossModelInsight:
        """Create error insight when extraction fails"""
        return CrossModelInsight(
            problem_analysis=f"Error during insight extraction: {error}",
            recommended_approach="Manual review required",
            key_considerations=["Extraction failed - manual analysis needed"],
            potential_risks=["Quality cannot be guaranteed"],
            success_criteria=["Manual validation required"],
            minimal_context_used=context,
            source_model=source_model,
            source_confidence=0.0,
            source_reasoning=f"Extraction failed with error: {error}",
            raw_output=raw_output,
            parsing_metadata={"strategy": "error_fallback", "error": error}
        )


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create insight extractor
    config = InsightExtractionConfig()
    extractor = InsightExtractor(config)
    
    # Test raw output
    raw_output = """
    Problem Analysis: The authentication system has JWT token validation issues in the middleware layer.
    The current implementation doesn't properly handle token expiration and refresh logic.
    
    Recommended Approach: Implement proper JWT validation middleware with the following components:
    1. Token validation service
    2. Refresh token mechanism
    3. Error handling and logging
    
    Key Considerations:
    - Token expiration handling
    - Secret key management
    - Error logging and monitoring
    - Performance impact of additional validation steps
    
    Potential Risks:
    - Security vulnerabilities if validation is incomplete
    - Performance impact of additional validation steps
    - Backward compatibility with existing tokens
    
    Success Criteria:
    - All authentication requests properly validated
    - Error rates below 1%
    - Response time impact under 50ms
    """
    
    context = "JWT authentication system with middleware validation"
    
    # Extract insight
    insight = extractor.extract_insight(raw_output, context, "claude-4")
    
    print(f"Insight Extraction Result:")
    print(f"Problem Analysis: {insight.problem_analysis[:100]}...")
    print(f"Recommended Approach: {insight.recommended_approach[:100]}...")
    print(f"Key Considerations: {len(insight.key_considerations)} items")
    print(f"Quality Score: {insight.quality_score:.2f}")
    print(f"Confidence: {insight.source_confidence:.2f}")
    print(f"Complexity: {insight.complexity_score:.2f}")
    print(f"Effort: {insight.estimated_effort}")
