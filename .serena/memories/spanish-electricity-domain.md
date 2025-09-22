# Spanish Electricity Domain

## CUPS (Universal Supply Point Code)
- **Format**: ES + 20-22 alphanumeric characters
- **Example**: ES1234567890123456789012AB
- **Historical issue**: Validation removed in v0.4.1, restored in v0.4.2
- **Current decision**: SDK validates format, API validates existence

## Spanish Distributors
Numeric codes 1-8 main ones:
1. **Viesgo** - Northern Spain
2. **E-distribución** (Endesa) - National
3. **Iberdrola Distribución** - National
4. **Naturgy Distribución** - National
5. **EDP Distribución** - Asturias, etc.
6. **CIDE** - Ceuta y Melilla
7. **Other regional operators**
8. **Minor distributors**

## Point Types (point_type)
- **1-3**: Domestic/commercial/industrial consumption
- **4**: Self-consumption with surplus
- **5**: Alternative auxiliary services (added v0.4.2)

## Monthly Dates
- **API Format**: YYYY/MM (NO days)
- **Recurring problem**: Users try YYYY/MM/DD
- **Resolution**: Strict validation rejecting dates with days
- **Support**: Automatic conversion from datetime/date

## Measurement Types
- **0**: Active consumption (kWh) - default
- **1**: Maximum power (kW)
- **2**: Reactive energy (kVArh) - V2 only

## Datadis API Limitations
- **History**: Maximum 2 years back
- **Date format**: Only monthly for most endpoints
- **Authentication**: JWT token with expiration
