# Trajectory: heuristic / expert

- Score: `0.990`
- Path: `provider_home -> authorizations -> prior_authorization_center -> exception_escalation_requests -> clinical_escalation_forms -> prior_auth_escalation -> prior_auth_escalation_worksheet`

```mermaid
graph TD
    node_provider_home["HarborCare Provider Portal"]
    class node_provider_home start,visited
    node_provider_home -->|"Authorizations"| node_authorizations:::pathEdge
    node_provider_home -->|"Claims and Appeals"| node_claims_appeals
    node_provider_home -->|"Coverage Policies"| node_coverage_policies
    node_authorizations["Authorizations"]
    class node_authorizations visited
    node_authorizations -->|"Prior Authorization Center"| node_prior_authorization_center:::pathEdge
    node_authorizations -->|"Claims and Appeals"| node_claims_appeals
    node_authorizations -->|"Authorization Policies"| node_authorization_policies
    node_prior_authorization_center["Prior Authorization Center"]
    class node_prior_authorization_center visited
    node_prior_authorization_center -->|"Status and Documentation"| node_status_and_documentation
    node_prior_authorization_center -->|"Exception and Escalation Requests"| node_exception_escalation_requests:::pathEdge
    node_prior_authorization_center -->|"Coverage Policies"| node_coverage_policies
    node_exception_escalation_requests["Exception and Escalation Requests"]
    class node_exception_escalation_requests visited
    node_exception_escalation_requests -->|"Clinical Escalation Forms"| node_clinical_escalation_forms:::pathEdge
    node_exception_escalation_requests -->|"Network Exception Request"| node_network_exception_request
    node_exception_escalation_requests -->|"Appeals Intake"| node_appeals_intake
    node_clinical_escalation_forms["Clinical Escalation Forms"]
    class node_clinical_escalation_forms visited
    node_clinical_escalation_forms -->|"Prior Authorization Escalation"| node_prior_auth_escalation:::pathEdge
    node_clinical_escalation_forms -->|"Peer-to-Peer Escalation"| node_peer_review_escalation
    node_clinical_escalation_forms -->|"Exception and Escalation Requests"| node_exception_escalation_requests
    node_prior_auth_escalation["Prior Authorization Escalation"]
    class node_prior_auth_escalation visited
    node_prior_auth_escalation -->|"Prior Authorization Escalation Worksheet"| node_prior_auth_escalation_worksheet:::pathEdge
    node_prior_auth_escalation -->|"Escalation Submission Checklist"| node_escalation_submission_checklist
    node_prior_auth_escalation -->|"Clinical Escalation Forms"| node_clinical_escalation_forms
    node_claims_appeals["Claims and Appeals"]
    node_claims_appeals -->|"Appeals Intake"| node_appeals_intake
    node_claims_appeals -->|"Corrected Claims"| node_corrected_claims
    node_coverage_policies["Coverage Policies"]
    node_coverage_policies -->|"Authorizations"| node_authorizations
    node_authorization_policies["Authorization Policies"]
    node_authorization_policies -->|"Prior Authorization Center"| node_prior_authorization_center
    node_status_and_documentation["Status and Documentation"]
    node_status_and_documentation -->|"Prior Authorization Center"| node_prior_authorization_center
    node_network_exception_request["Network Exception Request"]
    node_network_exception_request -->|"Exception and Escalation Requests"| node_exception_escalation_requests
    node_appeals_intake["Appeals Intake"]
    node_appeals_intake -->|"Claims and Appeals"| node_claims_appeals
    node_corrected_claims["Corrected Claims"]
    node_corrected_claims -->|"Claims and Appeals"| node_claims_appeals
    node_peer_review_escalation["Peer-to-Peer Escalation"]
    node_peer_review_escalation -->|"Clinical Escalation Forms"| node_clinical_escalation_forms
    node_escalation_submission_checklist["Escalation Submission Checklist"]
    node_escalation_submission_checklist -->|"Prior Authorization Escalation"| node_prior_auth_escalation
    node_prior_auth_escalation_worksheet["Prior Authorization Escalation Worksheet"]
    class node_prior_auth_escalation_worksheet target,visited
    classDef start fill:#d8f3dc,stroke:#2d6a4f,stroke-width:2px;
    classDef target fill:#ffe5d9,stroke:#bc3908,stroke-width:3px;
    classDef visited fill:#e9f5ff,stroke:#1d4ed8,stroke-width:2px;
    classDef pathEdge stroke:#1d4ed8,stroke-width:3px;
```
