# Req2Seq

Req2Seq analyzes project documentation, user stories, functional requirements, and informal software statements in order to identify security-relevant statements and interpret their implied security needs.

The server generates clear, testable, and traceable security requirements for software systems by mapping statements to one or more security objectives:

- Confidentiality (C)
- Integrity (I)
- Identification & Authentication (IA)
- Availability (A)
- Accountability (AY)
- Privacy (PR)

The generated requirements must use precise and unambiguous language that supports verification, auditability, and long-term system resilience.

## Security Patterns

### Confidentiality (C)

| Pattern ID | Pattern Name |
|---|---|
| C1 | Data |

The objective focuses on ensuring that sensitive information is disclosed only as intended.

---

### Integrity (I)

| Pattern ID | Pattern Name |
|---|---|
| I1 | Read-type Actions |
| I2 | Write-type Actions |
| I3 | Deletion |
| I4 | Unchangeable Objects |

The objective focuses on preventing unauthorized modification of sensitive information and ensuring consistent and correct handling of data.

---

### Identification & Authentication (IA)

| Pattern ID | Pattern Name |
|---|---|
| IA1 | Select Context for Role |
| IA2 | Unique Accounts |

The objective focuses on establishing and verifying the identity of users, processes, or devices.

---

### Availability (A)

| Pattern ID | Pattern Name |
|---|---|
| A1 | Data |
| A2 | Response Time |
| A3 | Service |
| A4 | Backup and Recovery |
| A5 | Capacity and Performance |

The objective focuses on ensuring that systems and resources remain operational and accessible when required.

---

### Accountability (AY)

| Pattern ID | Pattern Name |
|---|---|
| AY1 | Logging Transactions of Sensitive Data |
| AY2 | Logging Authentication Events |
| AY3 | Logging System Events |

The objective focuses on ensuring that actions and events affecting software assets can be traced to the responsible actor.

---

### Privacy (PR)

| Pattern ID | Pattern Name |
|---|---|
| PR1 | Usage of Personal Information |

The objective focuses on allowing individuals to understand and control how their personal information is collected, used, disclosed, and managed.

## Security Patterns

The server classifies requirements using predefined security patterns associated with the security objectives.

When the conditions of a security pattern are satisfied, the corresponding template must be applied as a single security requirement. Minor modifications may be made to improve readability and contextual consistency while preserving the original security intent.

## Generated Security Requirements

The generated security requirements should:

1. identify the applicable security objectives
2. identify the matching security patterns and their IDs
3. generate one or more security requirements derived from the detected patterns
4. preserve the intent and context of the original statement
5. remain actionable and verifiable
