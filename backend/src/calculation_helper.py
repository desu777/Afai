"""
Calculation Helper Module - VERSION 1.0
Safe and accurate calculations for aquarium dosing
"""
from typing import Dict, Optional, Tuple
import re
from config import TEST_ENV, debug_print

class CalculationHelper:
    """Helper class for aquarium-related calculations"""
    
    @staticmethod
    def extract_volume_from_query(query: str) -> Optional[int]:
        """Extract aquarium volume from query text"""
        patterns = [
            r'(\d+)\s*[lL](?:iters?)?',
            r'(\d+)\s*(?:liters?)',
            r'for\s+(\d+)\s*[lL]',
            r'aquarium\s+(\d+)\s*[lL]',
            r'tank\s+(\d+)\s*[lL]',
            r'tank\s+(\d+)\s*[lL]',
            r'(\d+)L\s+tank',
            r'(\d+)L\s+aquarium'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                volume = int(match.group(1))
                debug_print(f"[INFO] [CalculationHelper] Extracted volume: {volume}L")
                return volume
        return None
    
    @staticmethod
    def calculate_dosage(base_dose: float, base_volume: float, target_volume: float, 
                        unit: str = "ml", precision: int = 1) -> Dict[str, any]:
        """
        Calculate dosage for target volume based on base dosage
        
        Args:
            base_dose: Base dosage amount
            base_volume: Base volume (usually 100L)
            target_volume: Target aquarium volume
            unit: Unit of measurement (ml, drops, etc.)
            precision: Decimal places for result
            
        Returns:
            Dict with calculation details
        """
        try:
            # Calculate proportional dosage
            dosage = (base_dose / base_volume) * target_volume
            
            # Round to specified precision
            dosage_rounded = round(dosage, precision)
            
            # Format calculation string
            calculation_str = f"{base_dose} {unit}/{base_volume}L × {target_volume}L = {dosage_rounded} {unit}"
            
            result = {
                "success": True,
                "dosage": dosage_rounded,
                "unit": unit,
                "calculation": calculation_str,
                "formula": f"({base_dose} ÷ {base_volume}) × {target_volume}",
                "base_concentration": f"{base_dose} {unit} per {base_volume}L"
            }
            
            debug_print(f"[OK] [CalculationHelper] Calculated: {calculation_str}")
            return result
            
        except Exception as e:
            debug_print(f"[ERROR] [CalculationHelper] Calculation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "dosage": 0,
                "unit": unit
            }
    
    @staticmethod
    def calculate_parameter_change(dose_amount: float, dose_volume: float, 
                                 tank_volume: float, change_per_dose: float,
                                 parameter: str, current_value: Optional[float] = None) -> Dict[str, any]:
        """
        Calculate parameter change in aquarium
        
        Args:
            dose_amount: Amount to dose
            dose_volume: Volume for which the dose is specified
            tank_volume: Aquarium volume
            change_per_dose: Change in parameter per dose
            parameter: Parameter name (Ca, Mg, KH, etc.)
            current_value: Current parameter value (optional)
            
        Returns:
            Dict with calculation details
        """
        try:
            # Calculate expected change
            change = (dose_amount / dose_volume) * tank_volume * change_per_dose
            change_rounded = round(change, 2)
            
            result = {
                "success": True,
                "parameter": parameter,
                "expected_change": change_rounded,
                "calculation": f"{dose_amount}ml will raise {parameter} by ~{change_rounded} ppm",
                "dose_amount": dose_amount,
                "tank_volume": tank_volume
            }
            
            if current_value is not None:
                result["current_value"] = current_value
                result["expected_value"] = round(current_value + change_rounded, 1)
                result["calculation"] += f" (from {current_value} to {result['expected_value']} ppm)"
            
            debug_print(f"[OK] [CalculationHelper] Parameter change: {result['calculation']}")
            return result
            
        except Exception as e:
            debug_print(f"[ERROR] [CalculationHelper] Parameter calculation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "parameter": parameter
            }
    
    @staticmethod
    def calculate_water_change(tank_volume: float, change_percentage: float) -> Dict[str, any]:
        """Calculate water change volume"""
        try:
            change_volume = tank_volume * (change_percentage / 100)
            change_volume_rounded = round(change_volume, 1)
            
            result = {
                "success": True,
                "tank_volume": tank_volume,
                "change_percentage": change_percentage,
                "change_volume": change_volume_rounded,
                "calculation": f"{change_percentage}% of {tank_volume}L = {change_volume_rounded}L"
            }
            
            debug_print(f"[OK] [CalculationHelper] Water change: {result['calculation']}")
            return result
            
        except Exception as e:
            debug_print(f"[ERROR] [CalculationHelper] Water change calculation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def validate_dosage_safety(product_name: str, calculated_dose: float, 
                             tank_volume: float, frequency: str = "daily") -> Dict[str, any]:
        """
        Validate if calculated dosage is within safe limits
        
        Returns:
            Dict with safety validation results
        """
        # Define maximum safe doses per 100L (examples)
        max_doses_per_100l = {
            "Ca Plus": 20.0,  # ml
            "Mg Plus": 20.0,  # ml
            "KH Plus": 10.0,  # ml
            "AF Amino Mix": 2.0,  # drops
            "AF Build": 2.0,  # drops
            "AF Energy": 2.0,  # drops
            "AF NitraPhos Minus": 5.0,  # ml
            "Components Pro": 25.0  # ml
        }
        
        # Check if product has defined limits
        if product_name in max_doses_per_100l:
            max_dose = (max_doses_per_100l[product_name] / 100) * tank_volume
            
            if calculated_dose > max_dose:
                return {
                    "safe": False,
                    "warning": f"Calculated dose ({calculated_dose}) exceeds safe maximum ({round(max_dose, 1)})",
                    "recommendation": f"Split into multiple smaller doses or reduce to {round(max_dose, 1)}"
                }
            else:
                return {
                    "safe": True,
                    "message": f"Dosage is within safe limits (max: {round(max_dose, 1)})"
                }
        
        # No specific limits defined - provide general guidance
        return {
            "safe": True,
            "message": "Follow manufacturer's recommendations and observe livestock response"
        }
    
    @staticmethod
    def format_dosing_schedule(daily_dose: float, unit: str = "ml", 
                             split_doses: int = 1) -> Dict[str, any]:
        """Format dosing schedule with split doses"""
        if split_doses <= 1:
            return {
                "schedule": f"{daily_dose} {unit} once daily",
                "doses": [{"time": "Once daily", "amount": daily_dose}]
            }
        
        dose_per_time = round(daily_dose / split_doses, 2)
        times = ["Morning", "Noon", "Evening", "Night"][:split_doses]
        
        return {
            "schedule": f"{dose_per_time} {unit} × {split_doses} times daily",
            "doses": [{"time": time, "amount": dose_per_time} for time in times],
            "total_daily": daily_dose
        }


# Singleton instance for easy access
calculation_helper = CalculationHelper()