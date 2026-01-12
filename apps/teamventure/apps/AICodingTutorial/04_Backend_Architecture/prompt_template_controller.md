# How to Generate Backend Code (Prompt Template)

## Prompt Template

```markdown
# Context
Please refer to:
1. @architecture_guardrails.md (For COLA structure)
2. @api_specification.yaml (For Interface definition)
3. @final_schema.sql (For Database fields)

# Task
Implement the **Booking** feature backend code.

# Step 1: Domain Layer
Create the `Session` entity in the Domain layer.
- It should have methods like `isFull()` and `book(employeeId)`.
- **Constraint**: Pure Java, no Annotations.

# Step 2: Infrastructure Layer
Create the `SessionMapper` (MyBatis-Plus) and `SessionGatewayImpl`.
- **Constraint**: Convert DO (Data Object) to Entity here.

# Step 3: Application Layer
Create `BookingAppService`.
- Implement the logic defined in @interaction_flows.md (Flow 1).
- Handle the Optimistic Lock retry if necessary.

# Step 4: Adapter Layer
Create `BookingController` implementing the API defined in YAML.
```
