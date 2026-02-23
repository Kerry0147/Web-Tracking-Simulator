from typing import Optional, List, Dict, Any
from app.models import Customer, Device, Warranty, Case, HistoricalSession

def get_customer_profile(customer_id: str, mock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieves customer profile and registered devices.
    Returns dict with 'customer' (Customer model) and 'devices' (List[Device]).
    """
    customer_data = mock_data.get("customer")
    if not customer_data or customer_data["id"] != customer_id:
        return None
    
    # Get devices linked to this customer
    all_devices = mock_data.get("devices", [])
    user_devices = [d for d in all_devices if d["customer_id"] == customer_id]
    
    return {
        "customer": Customer(**customer_data),
        "devices": [Device(**d) for d in user_devices]
    }

def check_warranty_status(identifier: str, mock_data: Dict[str, Any], is_serial: bool = False) -> List[Warranty]:
    """
    Retrieves warranty records.
    If is_serial=True, identifier is a serial number (returns list of 1).
    If is_serial=False, identifier is customer_id (returns all warranties for customer).
    """
    all_warranties = mock_data.get("warranties", [])
    
    if is_serial:
        # First find device by serial to get device_id
        all_devices = mock_data.get("devices", [])
        device = next((d for d in all_devices if d["serial_number"] == identifier), None)
        if not device:
            return []
        
        # Find warranty for this device
        return [Warranty(**w) for w in all_warranties if w["device_id"] == device["id"]]
    else:
        # Find all warranties for customer
        return [Warranty(**w) for w in all_warranties if w["customer_id"] == identifier]

def get_customer_history(customer_id: str, mock_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieves historical sessions and support cases.
    """
    all_sessions = mock_data.get("historical_sessions", [])
    user_sessions = [HistoricalSession(**s) for s in all_sessions if s["customer_id"] == customer_id]
    
    all_cases = mock_data.get("cases", [])
    user_cases = [Case(**c) for c in all_cases if c["customer_id"] == customer_id]
    
    return {
        "sessions": user_sessions,
        "cases": user_cases
    }