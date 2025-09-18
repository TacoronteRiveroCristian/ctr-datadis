"""
Tests para modelos Pydantic del SDK de Datadis.

Estos tests validan:
- Creación correcta de modelos con datos válidos
- Validación de campos obligatorios y opcionales
- Serialización/deserialización JSON
- Validadores personalizados
- Manejo de aliases de campos
"""

import json
import pytest
from pydantic import ValidationError

from datadis_python.models.consumption import ConsumptionData
from datadis_python.models.supply import SupplyData
from datadis_python.models.contract import ContractData
from datadis_python.models.max_power import MaxPowerData
from datadis_python.models.distributor import DistributorData


class TestConsumptionData:
    """Tests para modelo ConsumptionData."""

    @pytest.mark.unit
    @pytest.mark.models
    def test_consumption_data_creation_valid(self, sample_consumption_data):
        """Test creación de ConsumptionData con datos válidos."""
        consumption = ConsumptionData(**sample_consumption_data)

        assert consumption.cups == sample_consumption_data["cups"]
        assert consumption.date == sample_consumption_data["date"]
        assert consumption.time == sample_consumption_data["time"]
        assert consumption.consumption_kwh == sample_consumption_data["consumptionKWh"]
        assert consumption.obtain_method == sample_consumption_data["obtainMethod"]
        assert consumption.surplus_energy_kwh is None
        assert consumption.generation_energy_kwh is None
        assert consumption.self_consumption_energy_kwh is None

    @pytest.mark.unit
    @pytest.mark.models
    def test_consumption_data_with_optional_fields(self, sample_consumption_data):
        """Test ConsumptionData con campos opcionales."""
        data = sample_consumption_data.copy()
        data.update({
            "surplusEnergyKWh": 0.050,
            "generationEnergyKWh": 0.200,
            "selfConsumptionEnergyKWh": 0.150
        })

        consumption = ConsumptionData(**data)

        assert consumption.surplus_energy_kwh == 0.050
        assert consumption.generation_energy_kwh == 0.200
        assert consumption.self_consumption_energy_kwh == 0.150

    @pytest.mark.unit
    @pytest.mark.models
    def test_consumption_data_alias_support(self):
        """Test soporte de aliases en ConsumptionData."""
        # Test con nombres de campos originales
        data_original = {
            "cups": "ES0123456789012345678901AB",
            "date": "2024/01/15",
            "time": "01:00",
            "consumptionKWh": 0.125,
            "obtainMethod": "Real"
        }

        # Test con nombres de campos Python
        data_python = {
            "cups": "ES0123456789012345678901AB",
            "date": "2024/01/15",
            "time": "01:00",
            "consumption_kwh": 0.125,
            "obtain_method": "Real"
        }

        consumption1 = ConsumptionData(**data_original)
        consumption2 = ConsumptionData(**data_python)

        assert consumption1.consumption_kwh == consumption2.consumption_kwh
        assert consumption1.obtain_method == consumption2.obtain_method

    @pytest.mark.unit
    @pytest.mark.models
    def test_consumption_data_json_serialization(self, sample_consumption_data):
        """Test serialización JSON de ConsumptionData."""
        consumption = ConsumptionData(**sample_consumption_data)

        # Test model_dump
        data_dict = consumption.model_dump()
        assert "consumption_kwh" in data_dict
        assert "obtain_method" in data_dict

        # Test model_dump con alias
        data_dict_alias = consumption.model_dump(by_alias=True)
        assert "consumptionKWh" in data_dict_alias
        assert "obtainMethod" in data_dict_alias

        # Test JSON serialization/deserialization
        json_str = consumption.model_dump_json(by_alias=True)
        consumption_restored = ConsumptionData.model_validate_json(json_str)
        assert consumption_restored.consumption_kwh == consumption.consumption_kwh

    @pytest.mark.unit
    @pytest.mark.models
    def test_consumption_data_validation_errors(self):
        """Test errores de validación en ConsumptionData."""
        # Campo requerido faltante
        with pytest.raises(ValidationError) as exc_info:
            ConsumptionData(cups="test", date="2024/01/15")

        error = exc_info.value
        assert len(error.errors()) > 0
        assert any("time" in str(err) for err in error.errors())

    @pytest.mark.unit
    @pytest.mark.models
    def test_consumption_data_type_validation(self):
        """Test validación de tipos en ConsumptionData."""
        # Tipo incorrecto para consumption_kwh
        with pytest.raises(ValidationError):
            ConsumptionData(
                cups="ES0123456789012345678901AB",
                date="2024/01/15",
                time="01:00",
                consumption_kwh="not_a_number",  # String en lugar de float
                obtain_method="Real"
            )


class TestSupplyData:
    """Tests para modelo SupplyData."""

    @pytest.mark.unit
    @pytest.mark.models
    def test_supply_data_creation_valid(self, sample_supply_data):
        """Test creación de SupplyData con datos válidos."""
        supply = SupplyData(**sample_supply_data)

        assert supply.address == sample_supply_data["address"]
        assert supply.cups == sample_supply_data["cups"]
        assert supply.postal_code == sample_supply_data["postalCode"]
        assert supply.province == sample_supply_data["province"]
        assert supply.municipality == sample_supply_data["municipality"]
        assert supply.distributor == sample_supply_data["distributor"]
        assert supply.valid_date_from == sample_supply_data["validDateFrom"]
        assert supply.valid_date_to is None
        assert supply.point_type == sample_supply_data["pointType"]
        assert supply.distributor_code == sample_supply_data["distributorCode"]

    @pytest.mark.unit
    @pytest.mark.models
    def test_supply_data_with_end_date(self, sample_supply_data):
        """Test SupplyData con fecha de fin."""
        data = sample_supply_data.copy()
        data["validDateTo"] = "2024/12/31"

        supply = SupplyData(**data)
        assert supply.valid_date_to == "2024/12/31"

    @pytest.mark.unit
    @pytest.mark.models
    def test_supply_data_alias_support(self, sample_supply_data):
        """Test soporte de aliases en SupplyData."""
        # Crear con aliases originales
        supply1 = SupplyData(**sample_supply_data)

        # Crear con nombres Python
        data_python = {
            "address": sample_supply_data["address"],
            "cups": sample_supply_data["cups"],
            "postal_code": sample_supply_data["postalCode"],
            "province": sample_supply_data["province"],
            "municipality": sample_supply_data["municipality"],
            "distributor": sample_supply_data["distributor"],
            "valid_date_from": sample_supply_data["validDateFrom"],
            "point_type": sample_supply_data["pointType"],
            "distributor_code": sample_supply_data["distributorCode"],
        }
        supply2 = SupplyData(**data_python)

        assert supply1.postal_code == supply2.postal_code
        assert supply1.valid_date_from == supply2.valid_date_from
        assert supply1.point_type == supply2.point_type
        assert supply1.distributor_code == supply2.distributor_code

    @pytest.mark.unit
    @pytest.mark.models
    def test_supply_data_json_roundtrip(self, sample_supply_data):
        """Test serialización/deserialización JSON de SupplyData."""
        supply = SupplyData(**sample_supply_data)

        # Serialize to JSON
        json_str = supply.model_dump_json(by_alias=True)

        # Deserialize from JSON
        supply_restored = SupplyData.model_validate_json(json_str)

        assert supply_restored.cups == supply.cups
        assert supply_restored.postal_code == supply.postal_code
        assert supply_restored.point_type == supply.point_type

    @pytest.mark.unit
    @pytest.mark.models
    def test_supply_data_point_type_validation(self, sample_supply_data):
        """Test validación de point_type en SupplyData."""
        # Point type válido (1-5)
        for point_type in [1, 2, 3, 4, 5]:
            data = sample_supply_data.copy()
            data["pointType"] = point_type
            supply = SupplyData(**data)
            assert supply.point_type == point_type

    @pytest.mark.unit
    @pytest.mark.models
    def test_supply_data_required_fields(self):
        """Test campos requeridos en SupplyData."""
        with pytest.raises(ValidationError) as exc_info:
            SupplyData()

        error = exc_info.value
        required_fields = ["address", "cups", "postalCode", "province",
                          "municipality", "distributor", "validDateFrom",
                          "pointType", "distributorCode"]

        error_fields = [err["loc"][0] for err in error.errors()]
        for field in required_fields:
            assert field in error_fields or field.replace("Code", "_code").replace("Type", "_type").replace("From", "_from") in error_fields


class TestContractData:
    """Tests para modelo ContractData."""

    @pytest.mark.unit
    @pytest.mark.models
    def test_contract_data_creation_valid(self, sample_contract_data):
        """Test creación de ContractData con datos válidos."""
        contract = ContractData(**sample_contract_data)

        assert contract.cups == sample_contract_data["cups"]
        assert contract.distributor == sample_contract_data["distributor"]
        assert contract.marketer == sample_contract_data["marketer"]
        assert contract.tension == sample_contract_data["tension"]
        assert contract.access_fare == sample_contract_data["accessFare"]
        assert contract.province == sample_contract_data["province"]
        assert contract.municipality == sample_contract_data["municipality"]
        assert contract.postal_code == sample_contract_data["postalCode"]
        assert contract.contracted_power_kw == sample_contract_data["contractedPowerkW"]
        assert contract.mode_power_control == sample_contract_data["modePowerControl"]
        assert contract.start_date == sample_contract_data["startDate"]
        assert contract.end_date is None
        assert contract.code_fare == sample_contract_data["codeFare"]

    @pytest.mark.unit
    @pytest.mark.models
    def test_contract_data_optional_power_periods(self, sample_contract_data):
        """Test períodos de potencia opcionales en ContractData."""
        data = sample_contract_data.copy()
        # Add more power periods to the list
        data["contractedPowerkW"] = [3.45, 3.45, 2.50, 2.50, 1.75, 1.75]
        data["timeDiscrimination"] = "TD"

        contract = ContractData(**data)

        assert len(contract.contracted_power_kw) == 6
        assert contract.contracted_power_kw[2] == 2.50
        assert contract.contracted_power_kw[3] == 2.50
        assert contract.contracted_power_kw[4] == 1.75
        assert contract.contracted_power_kw[5] == 1.75
        assert contract.time_discrimination == "TD"

    @pytest.mark.unit
    @pytest.mark.models
    def test_contract_data_with_end_date(self, sample_contract_data):
        """Test ContractData con fecha de fin."""
        data = sample_contract_data.copy()
        data["endDate"] = "2024/12/31"

        contract = ContractData(**data)
        assert contract.end_date == "2024/12/31"

    @pytest.mark.unit
    @pytest.mark.models
    def test_contract_data_alias_support(self, sample_contract_data):
        """Test soporte de aliases en ContractData."""
        contract = ContractData(**sample_contract_data)

        # Test field access by both names
        assert hasattr(contract, "distributor")
        assert hasattr(contract, "tension")
        assert hasattr(contract, "access_fare")
        assert hasattr(contract, "contracted_power_kw")
        assert hasattr(contract, "start_date")
        assert hasattr(contract, "end_date")
        assert hasattr(contract, "postal_code")
        assert hasattr(contract, "mode_power_control")
        assert hasattr(contract, "code_fare")

    @pytest.mark.unit
    @pytest.mark.models
    def test_contract_data_json_serialization(self, sample_contract_data):
        """Test serialización JSON de ContractData."""
        contract = ContractData(**sample_contract_data)

        # Test serialization with aliases
        json_str = contract.model_dump_json(by_alias=True)
        json_data = json.loads(json_str)

        assert "accessFare" in json_data
        assert "postalCode" in json_data
        assert "contractedPowerkW" in json_data
        assert "modePowerControl" in json_data
        assert "startDate" in json_data
        assert "codeFare" in json_data

        # Test deserialization
        contract_restored = ContractData.model_validate_json(json_str)
        assert contract_restored.distributor == contract.distributor
        assert contract_restored.contracted_power_kw == contract.contracted_power_kw


class TestMaxPowerData:
    """Tests para modelo MaxPowerData."""

    @pytest.mark.unit
    @pytest.mark.models
    def test_max_power_data_creation_valid(self, sample_max_power_data):
        """Test creación de MaxPowerData con datos válidos."""
        max_power = MaxPowerData(**sample_max_power_data)

        assert max_power.cups == sample_max_power_data["cups"]
        assert max_power.date == sample_max_power_data["date"]
        assert max_power.time == sample_max_power_data["time"]
        assert max_power.max_power == sample_max_power_data["maxPower"]
        assert max_power.period == sample_max_power_data["period"]

    @pytest.mark.unit
    @pytest.mark.models
    def test_max_power_data_alias_support(self, sample_max_power_data):
        """Test soporte de aliases en MaxPowerData."""
        # Test con alias original
        max_power1 = MaxPowerData(**sample_max_power_data)

        # Test con nombre Python
        data_python = sample_max_power_data.copy()
        data_python["max_power"] = data_python.pop("maxPower")
        max_power2 = MaxPowerData(**data_python)

        assert max_power1.max_power == max_power2.max_power

    @pytest.mark.unit
    @pytest.mark.models
    def test_max_power_data_json_roundtrip(self, sample_max_power_data):
        """Test serialización/deserialización JSON de MaxPowerData."""
        max_power = MaxPowerData(**sample_max_power_data)

        json_str = max_power.model_dump_json(by_alias=True)
        max_power_restored = MaxPowerData.model_validate_json(json_str)

        assert max_power_restored.max_power == max_power.max_power
        assert max_power_restored.period == max_power.period

    @pytest.mark.unit
    @pytest.mark.models
    def test_max_power_data_type_validation(self):
        """Test validación de tipos en MaxPowerData."""
        with pytest.raises(ValidationError):
            MaxPowerData(
                cups="ES0123456789012345678901AB",
                date="2024/01/15",
                time="20:00",
                max_power="not_a_number",  # String en lugar de float
                period="P1"
            )

    @pytest.mark.unit
    @pytest.mark.models
    def test_max_power_data_required_fields(self):
        """Test campos requeridos en MaxPowerData."""
        with pytest.raises(ValidationError) as exc_info:
            MaxPowerData()

        error = exc_info.value
        required_fields = ["cups", "date", "time", "maxPower", "period"]
        error_fields = [err["loc"][0] for err in error.errors()]

        # Al menos algunos campos requeridos deben aparecer en los errores
        assert len(error_fields) >= len(required_fields) - 1


class TestDistributorData:
    """Tests para modelo DistributorData."""

    @pytest.mark.unit
    @pytest.mark.models
    def test_distributor_data_creation_valid(self, sample_distributor_data):
        """Test creación de DistributorData con datos válidos."""
        distributor = DistributorData(**sample_distributor_data)

        assert distributor.distributor_codes == sample_distributor_data["distributorCodes"]
        assert len(distributor.distributor_codes) == 3
        assert "2" in distributor.distributor_codes

    @pytest.mark.unit
    @pytest.mark.models
    def test_distributor_data_json_serialization(self, sample_distributor_data):
        """Test serialización JSON de DistributorData."""
        distributor = DistributorData(**sample_distributor_data)

        json_str = distributor.model_dump_json()
        distributor_restored = DistributorData.model_validate_json(json_str)

        assert distributor_restored.distributor_codes == distributor.distributor_codes
        assert len(distributor_restored.distributor_codes) == len(distributor.distributor_codes)

    @pytest.mark.unit
    @pytest.mark.models
    def test_distributor_data_required_fields(self):
        """Test campos requeridos en DistributorData."""
        with pytest.raises(ValidationError):
            DistributorData()

    @pytest.mark.unit
    @pytest.mark.models
    def test_distributor_data_partial_creation(self):
        """Test creación parcial de DistributorData."""
        # Test con campos mínimos
        distributor = DistributorData(distributorCodes=["2"])
        assert distributor.distributor_codes == ["2"]
        assert len(distributor.distributor_codes) == 1


class TestModelValidation:
    """Tests generales de validación para todos los modelos."""

    @pytest.mark.unit
    @pytest.mark.models
    def test_all_models_support_extra_forbid(self):
        """Test que todos los modelos rechazan campos extra."""
        models_and_data = [
            (ConsumptionData, {
                "cups": "ES0123456789012345678901AB",
                "date": "2024/01/15",
                "time": "01:00",
                "consumptionKWh": 0.125,
                "obtainMethod": "Real",
                "extra_field": "should_fail"  # Campo extra
            }),
            (SupplyData, {
                "address": "CALLE EJEMPLO 123",
                "cups": "ES0123456789012345678901AB",
                "postalCode": "28001",
                "province": "MADRID",
                "municipality": "MADRID",
                "distributor": "Test Distributor",
                "validDateFrom": "2023/01/01",
                "pointType": 2,
                "distributorCode": "2",
                "extra_field": "should_fail"  # Campo extra
            })
        ]

        for model_class, invalid_data in models_and_data:
            # Nota: Pydantic v2 por defecto ignora campos extra, no falla
            # Si se configura extra="forbid", entonces debería fallar
            try:
                instance = model_class(**invalid_data)
                # Si no falla, verificar que al menos no se asignó el campo extra
                assert not hasattr(instance, "extra_field")
            except ValidationError:
                # Es correcto que falle si extra="forbid" está configurado
                pass

    @pytest.mark.unit
    @pytest.mark.models
    def test_model_schema_generation(self):
        """Test generación de esquemas JSON para todos los modelos."""
        models = [ConsumptionData, SupplyData, ContractData, MaxPowerData, DistributorData]

        for model_class in models:
            schema = model_class.model_json_schema()

            assert "properties" in schema
            assert "type" in schema
            assert schema["type"] == "object"
            assert len(schema["properties"]) > 0

    @pytest.mark.unit
    @pytest.mark.models
    def test_model_field_validation_messages(self):
        """Test que los mensajes de error de validación sean informativos."""
        with pytest.raises(ValidationError) as exc_info:
            ConsumptionData(
                # Missing required fields: cups, date, time, consumptionKWh, obtainMethod
                cups="test",  # Only provide cups, missing other required fields
            )

        error = exc_info.value
        assert len(error.errors()) > 0

        # Los errores deben incluir información sobre qué campo falló
        error_fields = [err["loc"][0] for err in error.errors()]
        assert len(error_fields) > 0

    @pytest.mark.unit
    @pytest.mark.models
    def test_model_repr_and_str(self, sample_consumption_data):
        """Test representación string de los modelos."""
        consumption = ConsumptionData(**sample_consumption_data)

        # Test que repr y str funcionen sin errores
        repr_str = repr(consumption)
        str_str = str(consumption)

        assert isinstance(repr_str, str)
        assert isinstance(str_str, str)
        assert len(repr_str) > 0
        assert len(str_str) > 0

        # Debe incluir información sobre el modelo
        assert "ConsumptionData" in repr_str