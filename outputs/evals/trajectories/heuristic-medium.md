# Trajectory: heuristic / medium

- Score: `0.010`
- Path: `landing -> student_services -> forms_library -> financial_aid_forms -> paying_for_college -> financial_aid_forms -> paying_for_college -> financial_aid_forms -> paying_for_college`

```mermaid
graph TD
    node_landing["Northstar University"]
    class node_landing start,visited
    node_landing -->|"Student Services"| node_student_services:::pathEdge
    node_landing -->|"Paying for College"| node_paying_for_college
    node_landing -->|"Campus Life"| node_campus_life
    node_student_services["Student Services"]
    class node_student_services visited
    node_student_services -->|"Forms Library"| node_forms_library:::pathEdge
    node_student_services -->|"Registrar Help"| node_registrar_help
    node_student_services -->|"Student Accounts"| node_student_accounts
    node_forms_library["Forms Library"]
    class node_forms_library visited
    node_forms_library -->|"Tuition and Billing Forms"| node_tuition_billing_forms
    node_forms_library -->|"Financial Aid Forms"| node_financial_aid_forms:::pathEdge
    node_forms_library -->|"Student Services"| node_student_services
    node_tuition_billing_forms["Tuition and Billing Forms"]
    node_tuition_billing_forms -->|"Tuition Appeals Form"| node_tuition_appeals_form
    node_tuition_billing_forms -->|"Student Accounts"| node_student_accounts
    node_tuition_billing_forms -->|"Forms Library"| node_forms_library
    node_financial_aid_forms["Financial Aid Forms"]
    class node_financial_aid_forms visited
    node_financial_aid_forms -->|"Paying for College"| node_paying_for_college:::pathEdge
    node_registrar_help["Registrar Help"]
    node_registrar_help -->|"Student Services"| node_student_services
    node_student_accounts["Student Accounts"]
    node_student_accounts -->|"Billing Adjustments"| node_billing_adjustments
    node_student_accounts -->|"Forms Library"| node_forms_library
    node_billing_adjustments["Billing Adjustments"]
    node_billing_adjustments -->|"Student Accounts"| node_student_accounts
    node_paying_for_college["Paying for College"]
    class node_paying_for_college visited
    node_paying_for_college -->|"Financial Aid"| node_financial_aid_forms:::pathEdge
    node_campus_life["Campus Life"]
    node_campus_life -->|"University Home"| node_landing
    node_tuition_appeals_form["Tuition Appeals Form"]
    class node_tuition_appeals_form target
    classDef start fill:#d8f3dc,stroke:#2d6a4f,stroke-width:2px;
    classDef target fill:#ffe5d9,stroke:#bc3908,stroke-width:3px;
    classDef visited fill:#e9f5ff,stroke:#1d4ed8,stroke-width:2px;
    classDef pathEdge stroke:#1d4ed8,stroke-width:3px;
```
