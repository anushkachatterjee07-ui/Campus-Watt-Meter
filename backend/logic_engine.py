from typing import Dict, Any, List

class Rule:
    """Base logic rule."""
    def evaluate(self, state: Dict[str, Any]) -> tuple[bool, str]:
        """Returns (triggered_bool, alert_message)."""
        raise NotImplementedError

class WastageRule(Rule):
    """
    Flags if the room is empty (Person_Count == 0) and the appliance is ON.
    """
    def evaluate(self, state: Dict[str, Any]) -> tuple[bool, str]:
        person_count = state.get("person_count", 0)
        light_status = state.get("light_status", "off")
        power = state.get("appliance_power_watts", 0.0)
        
        # IF Person_Count == 0 AND Appliance_State == ON then trigger alert
        if person_count == 0 and (light_status == "on" or power > 5.0):
            return True, f"Lights/Appliance left ON in empty room {state.get('room_id', 'Unknown')}"
            
        return False, ""

class OvercrowdingRule(Rule):
    """
    Flags an alert if the room exceeds a specific capacity threshold.
    """
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        
    def evaluate(self, state: Dict[str, Any]) -> tuple[bool, str]:
        person_count = state.get("person_count", 0)
        if person_count > self.capacity:
            return True, f"Overcrowding alert: {person_count} persons detected (Capacity: {self.capacity})"
        return False, ""

class PhantomDrawRule(Rule):
    """
    Flags if the appliance is marked as 'off' but is unexpectedly pulling power.
    """
    def evaluate(self, state: Dict[str, Any]) -> tuple[bool, str]:
        light_status = state.get("light_status", "off")
        power = state.get("appliance_power_watts", 0.0)
        
        if light_status == "off" and power > 2.0:
            return True, f"Phantom power draw detected: {power}W even when device is marked OFF"
        return False, ""

class LogicEngine:
    """
    Evaluates system states against predefined rules to trigger alerts or actions.
    """
    def __init__(self):
        self.rules: Dict[str, Rule] = {
            "wastage": WastageRule(),
            "phantom_draw": PhantomDrawRule(),
            "overcrowding": OvercrowdingRule(capacity=7)  # Example capacity limit 
        }
        
    def evaluate_state(self, state: Dict[str, Any]) -> tuple[bool, List[tuple[str, str]]]:
        """
        Takes a room state dictionary and checks it against all rules.
        Returns (is_wastage_flag, list_of_triggered_alerts_with_messages)
        where alerts is a list of (rule_name, alert_message).
        """
        triggered_alerts = []
        is_wastage = False
        
        for rule_name, rule in self.rules.items():
            triggered, message = rule.evaluate(state)
            if triggered:
                triggered_alerts.append((rule_name, message))
                if rule_name == "wastage":
                    is_wastage = True
                    
        return is_wastage, triggered_alerts

# Export a default instance for route use
logic_engine = LogicEngine()

if __name__ == "__main__":
    # Test cases to demonstrate the new explicit logic
    test_empty = {
        "person_count": 0,
        "light_status": "on",
        "appliance_power_watts": 15.0
    }
    test_occupied = {
        "person_count": 3,
        "light_status": "on",
        "appliance_power_watts": 15.0
    }
    test_overcrowded = {
        "person_count": 10,
        "light_status": "on",
        "appliance_power_watts": 15.0
    }
    
    print("--- Logic Engine Tests ---")
    
    print("\nState 1: Empty Room (0 people), Appliance ON")
    is_wastage, alerts = logic_engine.evaluate_state(test_empty)
    print(f"Result -> Wastage: {is_wastage} | Triggered: {alerts}")
    
    print("\nState 2: Occupied Room (3 people), Appliance ON")
    is_wastage, alerts = logic_engine.evaluate_state(test_occupied)
    print(f"Result -> Wastage: {is_wastage} | Triggered: {alerts}")

    print("\nState 3: Overcrowded Room (10 people), Appliance ON")
    is_wastage, alerts = logic_engine.evaluate_state(test_overcrowded)
    print(f"Result -> Wastage: {is_wastage} | Triggered: {alerts}")
