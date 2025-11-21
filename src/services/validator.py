"""
SHACL-style validation logic for KBE action execution.
Validates action parameters against ontology constraints.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.models import ValidationRequest, ValidationResponse

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation configuration is invalid."""
    pass


class ActionValidator:
    """
    Validates building automation actions against ontology constraints.

    Implements SHACL-style validation for:
    - Parameter types and ranges
    - Zone capabilities
    - Temporal constraints
    - Safety rules
    """

    def __init__(self):
        """Initialize the validator with ontology-based rules."""
        self._validation_rules = self._load_validation_rules()
        logger.info("ActionValidator initialized with validation rules")

    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Load validation rules from ontology.
        In production, this would load from RDF/SHACL shapes.
        """
        return {
            "setTemperature": {
                "required_params": ["setpoint"],
                "optional_params": ["mode"],
                "validations": {
                    "setpoint": {
                        "type": "number",
                        "min": 55.0,
                        "max": 85.0,
                        "unit": "fahrenheit"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["heat", "cool", "auto", "off"]
                    }
                }
            },
            "setOccupancyMode": {
                "required_params": ["mode"],
                "optional_params": [],
                "validations": {
                    "mode": {
                        "type": "string",
                        "enum": ["occupied", "unoccupied", "standby"]
                    }
                }
            },
            "adjustVentilation": {
                "required_params": ["rate"],
                "optional_params": ["mode"],
                "validations": {
                    "rate": {
                        "type": "number",
                        "min": 0,
                        "max": 10000,
                        "unit": "cfm"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["constant", "demand-based", "scheduled"]
                    }
                }
            },
            "enableEconomizer": {
                "required_params": ["enabled"],
                "optional_params": ["min_outdoor_temp", "max_outdoor_temp"],
                "validations": {
                    "enabled": {
                        "type": "boolean"
                    },
                    "min_outdoor_temp": {
                        "type": "number",
                        "min": -20,
                        "max": 120
                    },
                    "max_outdoor_temp": {
                        "type": "number",
                        "min": -20,
                        "max": 120
                    }
                }
            },
            "setLightingLevel": {
                "required_params": ["level"],
                "optional_params": ["duration", "fade_time"],
                "validations": {
                    "level": {
                        "type": "number",
                        "min": 0,
                        "max": 100,
                        "unit": "percent"
                    },
                    "duration": {
                        "type": "number",
                        "min": 0,
                        "max": 86400,
                        "unit": "seconds"
                    },
                    "fade_time": {
                        "type": "number",
                        "min": 0,
                        "max": 300,
                        "unit": "seconds"
                    }
                }
            }
        }

    async def validate_action(
        self,
        action_type: str,
        parameters: Dict[str, Any],
        target_zone: str
    ) -> ValidationResponse:
        """
        Validate an action against ontology constraints.

        Args:
            action_type: Type of action to validate
            parameters: Action parameters
            target_zone: Target zone ID

        Returns:
            ValidationResponse with validation results
        """
        errors: List[str] = []
        warnings: List[str] = []

        logger.debug(
            f"Validating action {action_type} with parameters {parameters} "
            f"for zone {target_zone}"
        )

        # Check if action type is supported
        if action_type not in self._validation_rules:
            errors.append(f"Unsupported action type: {action_type}")
            return ValidationResponse(is_valid=False, errors=errors)

        rules = self._validation_rules[action_type]

        # Validate required parameters
        missing_params = [
            param for param in rules["required_params"]
            if param not in parameters
        ]
        if missing_params:
            errors.append(f"Missing required parameters: {', '.join(missing_params)}")

        # Validate parameter values
        for param_name, param_value in parameters.items():
            if param_name in rules["validations"]:
                param_errors = self._validate_parameter(
                    param_name,
                    param_value,
                    rules["validations"][param_name]
                )
                errors.extend(param_errors)
            elif param_name not in rules.get("optional_params", []):
                warnings.append(f"Unknown parameter: {param_name}")

        # Validate zone capabilities (placeholder)
        zone_warnings = await self._validate_zone_capabilities(
            target_zone,
            action_type
        )
        warnings.extend(zone_warnings)

        # Check temporal constraints (placeholder)
        temporal_warnings = await self._validate_temporal_constraints(
            action_type,
            parameters
        )
        warnings.extend(temporal_warnings)

        is_valid = len(errors) == 0

        if is_valid:
            logger.info(f"Validation passed for action {action_type}")
        else:
            logger.warning(f"Validation failed for action {action_type}: {errors}")

        return ValidationResponse(
            is_valid=is_valid,
            errors=errors if errors else None,
            warnings=warnings if warnings else None
        )

    def _validate_parameter(
        self,
        param_name: str,
        param_value: Any,
        validation_rules: Dict[str, Any]
    ) -> List[str]:
        """
        Validate a single parameter against its rules.

        Args:
            param_name: Parameter name
            param_value: Parameter value
            validation_rules: Validation rules for this parameter

        Returns:
            List of validation error messages
        """
        errors: List[str] = []

        # Type validation
        expected_type = validation_rules.get("type")
        if expected_type:
            type_valid = self._check_type(param_value, expected_type)
            if not type_valid:
                errors.append(
                    f"Parameter '{param_name}' must be of type {expected_type}, "
                    f"got {type(param_value).__name__}"
                )
                return errors  # Skip further validation if type is wrong

        # Enum validation
        if "enum" in validation_rules:
            if param_value not in validation_rules["enum"]:
                errors.append(
                    f"Parameter '{param_name}' must be one of "
                    f"{validation_rules['enum']}, got '{param_value}'"
                )

        # Range validation for numbers
        if expected_type == "number":
            if "min" in validation_rules and param_value < validation_rules["min"]:
                errors.append(
                    f"Parameter '{param_name}' must be >= {validation_rules['min']}, "
                    f"got {param_value}"
                )
            if "max" in validation_rules and param_value > validation_rules["max"]:
                errors.append(
                    f"Parameter '{param_name}' must be <= {validation_rules['max']}, "
                    f"got {param_value}"
                )

        return errors

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_map = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list
        }

        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip validation

        return isinstance(value, expected_python_type)

    async def _validate_zone_capabilities(
        self,
        zone_id: str,
        action_type: str
    ) -> List[str]:
        """
        Validate that the zone supports the requested action.

        Args:
            zone_id: Zone identifier
            action_type: Type of action

        Returns:
            List of warning messages
        """
        warnings: List[str] = []

        # Placeholder implementation
        # In production, this would query the building ontology
        # to check if the zone has the required equipment/capabilities

        # Example: Check if zone has HVAC for temperature control
        if action_type == "setTemperature":
            # Would query: "Does zone have HVAC equipment?"
            pass

        return warnings

    async def _validate_temporal_constraints(
        self,
        action_type: str,
        parameters: Dict[str, Any]
    ) -> List[str]:
        """
        Validate temporal constraints (schedules, rate limits, etc.).

        Args:
            action_type: Type of action
            parameters: Action parameters

        Returns:
            List of warning messages
        """
        warnings: List[str] = []

        # Placeholder implementation
        # In production, this would check:
        # - Rate limits (max actions per time period)
        # - Scheduled maintenance windows
        # - Business rules (e.g., no temp changes during certain hours)

        return warnings

    async def validate_request(self, request: ValidationRequest) -> ValidationResponse:
        """
        Validate a complete validation request.

        Args:
            request: ValidationRequest to validate

        Returns:
            ValidationResponse with results
        """
        return await self.validate_action(
            request.action_type,
            request.parameters,
            request.target_zone
        )
