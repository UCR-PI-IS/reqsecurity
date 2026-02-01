# Task

Extract security requirements from the provided functional requirement by applying security pattern logic.

## System Context

```

<CONTEXT>

```

## Functional Requirement

```

<REQUIREMENT>

```

## Execution Logic (Strict and Mandatory Order)

You must perform the following steps sequentially.
Skipping, reordering, or combining steps is not allowed.

### 1 Identifying Elements

Extract the subject, action, and resource from the given functional requirement and
store the values â€‹â€‹as `subject`, `action`, and `resource`.

These elements are constants and MUST be treated as immutable tokens.
They must be reused verbatim and without reinterpretation.

### 2 Analyzing Conditions

Analyze the conditions of the security patterns and verify that they are met.

### 3 Creating Security Requirements

If the conditions are met, generate the security requirement following the template.

### 4 Related Patterns

Review the related patterns and start step 1 again.

### 5 Counting Phase

Count the total number of derived security requirements.
Store the value as `num_rows`.

### 6 Validation Phase

Validate that ALL conditions are met:
- `id` is unique and sequential
- `objective_id` is valid
- `reasoning` is not empty

If the requirement text semantically implies a different subject, action, or resource, the result is INVALID and MUST be corrected.

## Output Constraints

### Exclusive Output
  
Output **ONLY** a valid **TOON** (Token-Oriented Object Notation) code block. Do not include any text, markdown, or commentary outside the block.

### Header Integrity
  
You **must** start the block with the count calculated in step 2: `[num_rows]{id,objective_id,pattern_id,subject,action,resource,requirement,reasoning}:`.

### Row-Count Accuracy
  
The `num_rows` integer must be mathematically equal to the number of lines of data provided.

### Indentation & Spacing
  
* Every data row must begin with exactly two spaces (  ).

### Formatting
  
* Fields: Enclosed in double quotes (`"`).
* Separators: Comma (`,`).
* **Line End:** The line MUST terminate immediately after the closing double quote (") of the reasoning field.

### Negative Constraint (Critical)

* NEVER append a comma (,) at the end of a line.
* NEVER append ," at the end of a line.
* Never return anything other than the TOON.
* The last character of every row must be ".

### Domain Limits
  
* `objective_id`: Strictly restricted to `{c, i, ia, a, ay, pr}`.
* `pattern_id`: Strictly numeric.
* `id`: Sequential integer starting from "1".

## Mandatory Output Schema (TOON)

```toon
[num_rows]{id,objective_id,pattern_id,subject,action,resource,requirement,reasoning}:
  <id_i>,<objective_id_i>,<pattern_id_i>,<subject>,<action>,<resource>,<requirement_i>,<reasoning_i>
  <id_i>,<objective_id_i>,<pattern_id_i>,<subject>,<action>,<resource>,<requirement_i>,<reasoning_i>
```

### Example

#### Input

```txt
A member can make a payment to another member by sending just one SMS to the organization number/short code.
```

#### Output
```toon
[2]{id,objective_id,pattern_id,subject,action,resource,requirement,reasoning}:
  "1","c","1","member","make","payment","The system shall enforce access privileges that enable member to make a payment.; The system shall encrypt payment and store payment in encrypted format using an industry approved encryption algorithm.; The system shall transmit payment data in encrypted format to and from the authorized member.; The system shall monitor the status and location of system components that may contain unencrypted payment data.","It is important because it protects payment data confidentiality, integrity, and authorized use throughout its lifecycle. Enforcing access privileges ensures that only legitimate members can initiate payments, reducing the risk of unauthorized transactions and fraud."
  "2","ay","3","member","make","payment","The system shall log every time payment happens.;At a minimum, the system shall capture the following information for the log entry: timestamp, payment;The system shall prevent all users from modifying the log entry.;The system shall allow only authorized auditors to view the log entry.","It is important because it ensures accountability, traceability, and integrity of all payment-related activities within the system."
```