import time
import random
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

class ApplianceMonitor(ABC):
    """Abstract Base Class for Appliance Status Recognition Module"""
    
    @abstractmethod
    def get_status(self) -> dict:
        """
        Returns a dictionary containing:
        - is_on: bool (True if the appliance is turned ON)
        - power_watts: float (Current power draw in watts, if applicable)
        - additional_info: dict (Any other relevant telemetry data)
        """
        pass

class SimulatedSmartPlug(ApplianceMonitor):
    """
    A simulated IoT power meter that flips between ON/OFF states for testing.
    """
    def __init__(self, appliance_name="Room Light", base_power=15.0):
        self.appliance_name = appliance_name
        self.base_power = base_power
        self.is_on = True

    def get_status(self) -> dict:
        # Occasionally toggle state to simulate real-world usage (5% chance per call)
        if random.random() < 0.05:
            self.is_on = not self.is_on
            logging.info(f"{self.appliance_name} state changed to {'ON' if self.is_on else 'OFF'}")

        # Simulate small power fluctuations
        current_power = (self.base_power + random.uniform(-0.5, 0.5)) if self.is_on else 0.0

        return {
            "source": "simulated",
            "is_on": self.is_on,
            "power_watts": round(current_power, 2)
        }

class KasaSmartPlug(ApplianceMonitor):
    """
    Integration for TP-Link Kasa smart plugs.
    Requires: pip install python-kasa
    """
    def __init__(self, ip_address: str):
        self.ip_address = ip_address
        self.plug = None
        self._init_plug()

    def _init_plug(self):
        try:
            import asyncio
            from kasa import SmartPlug
            # Using synchronous wrapper for simple integration
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.plug = SmartPlug(self.ip_address)
            loop.run_until_complete(self.plug.update())
        except ImportError:
            logging.error("python-kasa is not installed. Run: pip install python-kasa")
        except Exception as e:
            logging.error(f"Failed to connect to Kasa plug at {self.ip_address}: {e}")

    def get_status(self) -> dict:
        if not self.plug:
            return {"source": "kasa", "is_on": False, "power_watts": 0.0, "error": "Plug not initialized"}

        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.plug.update())
            
            is_on = self.plug.is_on
            # Emeeter usage (if supported by plug)
            power = self.plug.emeter_realtime.power if hasattr(self.plug, 'emeter_realtime') and self.plug.emeter_realtime else 0.0
            
            return {
                "source": f"kasa_{self.ip_address}",
                "is_on": is_on,
                "power_watts": round(power, 2)
            }
        except Exception as e:
            logging.error(f"Error fetching status from Kasa plug: {e}")
            return {"source": "kasa", "is_on": False, "power_watts": 0.0, "error": str(e)}

class MQTTApplianceMonitor(ApplianceMonitor):
    """
    Integration for MQTT-based IoT devices (like Tasmota, Shelly, or Zigbee2MQTT).
    Requires: pip install paho-mqtt
    """
    def __init__(self, broker_url: str, topic: str, port=1883):
        self.broker_url = broker_url
        self.topic = topic
        self.port = port
        self.is_on = False
        self.power_watts = 0.0
        self._init_mqtt()

    def _init_mqtt(self):
        try:
            import paho.mqtt.client as mqtt
            import json

            def on_message(client, userdata, msg):
                try:
                    payload = json.loads(msg.payload.decode())
                    # Assuming payload structure like {"state": "ON", "energy": {"power": 12.5}}
                    state_str = payload.get("state", "OFF").upper()
                    self.is_on = (state_str == "ON")
                    
                    if "energy" in payload and "power" in payload["energy"]:
                        self.power_watts = float(payload["energy"]["power"])
                except Exception as e:
                    logging.warning(f"Error parsing MQTT message: {e}")

            client = mqtt.Client()
            client.on_message = on_message
            client.connect(self.broker_url, self.port, 60)
            client.subscribe(self.topic)
            client.loop_start()  # Run in background thread
        except ImportError:
            logging.error("paho-mqtt is not installed. Run: pip install paho-mqtt")
        except Exception as e:
            logging.error(f"Failed to setup MQTT broker connection: {e}")

    def get_status(self) -> dict:
        return {
            "source": f"mqtt_{self.topic}",
            "is_on": self.is_on,
            "power_watts": round(self.power_watts, 2)
        }

# Factory to get the appropriate monitor
def create_appliance_monitor(source_type="simulated", config=None) -> ApplianceMonitor:
    """
    Factory function to initialize the desired IoT appliance monitor.
    source_type: "simulated", "kasa", or "mqtt"
    config: dict containing connection info (ip_address, broker_url, etc.)
    """
    if source_type == "simulated":
        return SimulatedSmartPlug()
    elif source_type == "kasa" and config and "ip_address" in config:
        return KasaSmartPlug(config["ip_address"])
    elif source_type == "mqtt" and config and "broker_url" in config and "topic" in config:
        return MQTTApplianceMonitor(config["broker_url"], config["topic"])
    else:
        logging.warning("Invalid source_type or missing config. Defaulting to SimulatedSmartPlug.")
        return SimulatedSmartPlug()

if __name__ == "__main__":
    # Test the module locally
    print("Testing Appliance Status Recognition Module...")
    
    # 1. Test simulated plug
    sim_plug = create_appliance_monitor("simulated")
    for _ in range(3):
        print("Simulated Plug:", sim_plug.get_status())
        time.sleep(1)
