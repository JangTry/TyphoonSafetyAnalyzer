# engine/validators/output_validator.py
from typing import Dict, Any, List
import json

class OutputValidator:
    def __init__(self):
        self.required_fields = [
            'overall_risk_level',
            'hazards_by_category',
            'risk_summary',
            'urgent_actions',
            'summary',
            'confidence_score'
        ]
        
        self.valid_risk_levels = ['low', 'medium', 'high', 'critical', 'unknown']
        self.hazard_categories = ['flying_objects', 'structural_damage', 'elevated_objects', 'tree_hazards']
    
    def validate(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the analysis result
        
        Args:
            analysis_result: Raw analysis result from LLM
            
        Returns:
            Validated and cleaned result
        """
        validated = analysis_result.copy()
        validation_errors = []
        
        # Check required fields
        for field in self.required_fields:
            if field not in validated:
                validation_errors.append(f"Missing required field: {field}")
                validated[field] = self._get_default_value(field)
        
        # Validate risk levels
        if validated.get('overall_risk_level') not in self.valid_risk_levels:
            validation_errors.append(f"Invalid overall_risk_level: {validated.get('overall_risk_level')}")
            validated['overall_risk_level'] = 'unknown'
        
        # Validate hazards_by_category
        if not isinstance(validated.get('hazards_by_category'), dict):
            validation_errors.append("hazards_by_category must be a dictionary")
            validated['hazards_by_category'] = {}
        else:
            validated['hazards_by_category'] = self._validate_hazard_categories(
                validated['hazards_by_category']
            )
        
        # Validate risk_summary
        if not isinstance(validated.get('risk_summary'), dict):
            validation_errors.append("risk_summary must be a dictionary")
            validated['risk_summary'] = self._get_default_risk_summary()
        else:
            validated['risk_summary'] = self._validate_risk_summary(
                validated['risk_summary']
            )
        
        # Validate confidence_score
        confidence = validated.get('confidence_score', 0.0)
        if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
            validation_errors.append(f"Invalid confidence_score: {confidence}")
            validated['confidence_score'] = 0.0
        
        # Validate urgent_actions
        if not isinstance(validated.get('urgent_actions'), list):
            validation_errors.append("urgent_actions must be a list")
            validated['urgent_actions'] = []
        
        # Add validation metadata
        validated['validation'] = {
            'errors': validation_errors,
            'is_valid': len(validation_errors) == 0
        }
        
        return validated
    
    def _validate_hazard_categories(self, hazards: Dict[str, Any]) -> Dict[str, Any]:
        """Validate hazard categories structure"""
        validated_hazards = {}
        
        for category in self.hazard_categories:
            category_data = hazards.get(category, [])
            if not isinstance(category_data, list):
                category_data = []
            
            if category == 'flying_objects':
                validated_hazards[category] = [
                    self._validate_flying_object(item) for item in category_data
                ]
            elif category == 'structural_damage':
                validated_hazards[category] = [
                    self._validate_structural_damage(item) for item in category_data
                ]
            elif category == 'elevated_objects':
                validated_hazards[category] = [
                    self._validate_elevated_object(item) for item in category_data
                ]
            elif category == 'tree_hazards':
                validated_hazards[category] = [
                    self._validate_tree_hazard(item) for item in category_data
                ]
        
        return validated_hazards
    
    def _validate_flying_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Validate flying object entry"""
        return {
            'item': obj.get('item', 'Unknown object'),
            'description': obj.get('description', 'No description'),
            'movement_risk': obj.get('movement_risk', 'unknown') if obj.get('movement_risk') in ['high', 'medium', 'low'] else 'unknown',
            'impact_severity': obj.get('impact_severity', 'unknown') if obj.get('impact_severity') in self.valid_risk_levels else 'unknown',
            'overall_risk': obj.get('overall_risk', 'unknown') if obj.get('overall_risk') in self.valid_risk_levels else 'unknown',
            'location': obj.get('location', 'Location not specified'),
            'recommendation': obj.get('recommendation', 'No recommendation')
        }
    
    def _validate_structural_damage(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Validate structural damage entry"""
        return {
            'item': obj.get('item', 'Unknown structure'),
            'description': obj.get('description', 'No description'),
            'risk_level': obj.get('risk_level', 'unknown') if obj.get('risk_level') in self.valid_risk_levels else 'unknown',
            'location': obj.get('location', 'Location not specified'),
            'recommendation': obj.get('recommendation', 'No recommendation')
        }
    
    def _validate_elevated_object(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Validate elevated object entry"""
        return {
            'item': obj.get('item', 'Unknown object'),
            'description': obj.get('description', 'No description'),
            'fall_risk': obj.get('fall_risk', 'unknown') if obj.get('fall_risk') in ['high', 'medium', 'low'] else 'unknown',
            'impact_severity': obj.get('impact_severity', 'unknown') if obj.get('impact_severity') in self.valid_risk_levels else 'unknown',
            'overall_risk': obj.get('overall_risk', 'unknown') if obj.get('overall_risk') in self.valid_risk_levels else 'unknown',
            'location': obj.get('location', 'Location not specified'),
            'recommendation': obj.get('recommendation', 'No recommendation')
        }
    
    def _validate_tree_hazard(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tree hazard entry"""
        return {
            'description': obj.get('description', 'No description'),
            'risk_level': obj.get('risk_level', 'unknown') if obj.get('risk_level') in self.valid_risk_levels else 'unknown',
            'location': obj.get('location', 'Location not specified'),
            'recommendation': obj.get('recommendation', 'No recommendation')
        }
    
    def _validate_risk_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Validate risk summary structure"""
        validated_summary = {}
        
        for key in ['critical_count', 'high_count', 'medium_count', 'low_count', 'total_hazards']:
            value = summary.get(key, 0)
            validated_summary[key] = value if isinstance(value, int) and value >= 0 else 0
        
        return validated_summary
    
    def _get_default_risk_summary(self) -> Dict[str, Any]:
        """Get default risk summary"""
        return {
            'critical_count': 0,
            'high_count': 0,
            'medium_count': 0,
            'low_count': 0,
            'total_hazards': 0
        }
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            'overall_risk_level': 'unknown',
            'hazards_by_category': {},
            'risk_summary': self._get_default_risk_summary(),
            'summary': 'Analysis incomplete',
            'urgent_actions': [],
            'confidence_score': 0.0
        }
        return defaults.get(field)