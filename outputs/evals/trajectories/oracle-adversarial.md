# Trajectory: oracle / adversarial

- Score: `0.990`
- Path: `city_home -> utilities -> service_interruptions -> restoration_reconnection -> emergency_restoration -> after_hours_reversal_requests -> after_hours_shutoff_reversal_form`

```mermaid
graph TD
    node_city_home["Rivermark City Services"]
    class node_city_home start,visited
    node_city_home -->|"Utilities"| node_utilities:::pathEdge
    node_city_home -->|"Resident Help Center"| node_resident_help_center
    node_city_home -->|"Emergency Updates"| node_emergency_updates
    node_utilities["Utilities"]
    class node_utilities visited
    node_utilities -->|"Service Interruptions"| node_service_interruptions:::pathEdge
    node_utilities -->|"Billing and Payments"| node_billing_and_payments
    node_utilities -->|"Utility Forms Library"| node_utility_forms_library
    node_service_interruptions["Service Interruptions"]
    class node_service_interruptions visited
    node_service_interruptions -->|"Restoration and Reconnection"| node_restoration_reconnection:::pathEdge
    node_service_interruptions -->|"Outage Map"| node_outage_map
    node_service_interruptions -->|"Utility Forms Library"| node_utility_forms_library
    node_restoration_reconnection["Restoration and Reconnection"]
    class node_restoration_reconnection visited
    node_restoration_reconnection -->|"Emergency Restoration"| node_emergency_restoration:::pathEdge
    node_restoration_reconnection -->|"Standard Reconnection Request"| node_standard_reconnection_request
    node_restoration_reconnection -->|"Billing and Payments"| node_billing_and_payments
    node_emergency_restoration["Emergency Restoration"]
    class node_emergency_restoration visited
    node_emergency_restoration -->|"After-Hours Reversal Requests"| node_after_hours_reversal_requests:::pathEdge
    node_emergency_restoration -->|"Life-Safety Restoration"| node_life_safety_restoration
    node_emergency_restoration -->|"Storm and Outage Recovery"| node_storm_outage_recovery
    node_after_hours_reversal_requests["After-Hours Reversal Requests"]
    class node_after_hours_reversal_requests visited
    node_after_hours_reversal_requests -->|"After-Hours Utility Shutoff Reversal Form"| node_after_hours_shutoff_reversal_form:::pathEdge
    node_after_hours_reversal_requests -->|"After-Hours Eligibility Checklist"| node_after_hours_eligibility_checklist
    node_after_hours_reversal_requests -->|"Emergency Restoration"| node_emergency_restoration
    node_resident_help_center["Resident Help Center"]
    node_resident_help_center -->|"Account Support"| node_account_support
    node_resident_help_center -->|"Utilities"| node_utilities
    node_emergency_updates["Emergency Updates"]
    node_emergency_updates -->|"Outage Map"| node_outage_map
    node_emergency_updates -->|"City Services Home"| node_city_home
    node_billing_and_payments["Billing and Payments"]
    node_billing_and_payments -->|"Payment Plan Request"| node_payment_plan_request
    node_billing_and_payments -->|"Utilities"| node_utilities
    node_utility_forms_library["Utility Forms Library"]
    node_utility_forms_library -->|"Reconnection Forms"| node_reconnection_forms
    node_utility_forms_library -->|"Utilities"| node_utilities
    node_outage_map["Outage Map"]
    node_outage_map -->|"Emergency Updates"| node_emergency_updates
    node_standard_reconnection_request["Standard Reconnection Request"]
    node_standard_reconnection_request -->|"Restoration and Reconnection"| node_restoration_reconnection
    node_life_safety_restoration["Life-Safety Restoration"]
    node_life_safety_restoration -->|"Emergency Restoration"| node_emergency_restoration
    node_storm_outage_recovery["Storm and Outage Recovery"]
    node_storm_outage_recovery -->|"Emergency Updates"| node_emergency_updates
    node_after_hours_eligibility_checklist["After-Hours Eligibility Checklist"]
    node_after_hours_eligibility_checklist -->|"After-Hours Reversal Requests"| node_after_hours_reversal_requests
    node_account_support["Account Support"]
    node_account_support -->|"Resident Help Center"| node_resident_help_center
    node_payment_plan_request["Payment Plan Request"]
    node_payment_plan_request -->|"Billing and Payments"| node_billing_and_payments
    node_reconnection_forms["Reconnection Forms"]
    node_reconnection_forms -->|"After-Hours Utility Reversal Packet"| node_after_hours_reversal_packet
    node_reconnection_forms -->|"Utility Forms Library"| node_utility_forms_library
    node_after_hours_reversal_packet["After-Hours Utility Reversal Packet"]
    node_after_hours_reversal_packet -->|"After-Hours Reversal Requests"| node_after_hours_reversal_requests
    node_after_hours_shutoff_reversal_form["After-Hours Utility Shutoff Reversal Form"]
    class node_after_hours_shutoff_reversal_form target,visited
    classDef start fill:#d8f3dc,stroke:#2d6a4f,stroke-width:2px;
    classDef target fill:#ffe5d9,stroke:#bc3908,stroke-width:3px;
    classDef visited fill:#e9f5ff,stroke:#1d4ed8,stroke-width:2px;
    classDef pathEdge stroke:#1d4ed8,stroke-width:3px;
```
