from zxfermion.tableaus.rules import cx_rules
from zxfermion.types import GateType


class Tableau:
    def __init__(self, start, finish):
        match [start.type, finish.type]:
            case [GateType.GADGET, GateType.CX]:
                self.gadget_cx(start, finish)
            case [GateType.GADGET, GateType.CZ]:
                pass
            case [GateType.CX, GateType.GADGET]:
                pass
            case [GateType.CZ, GateType.GADGET]:
                pass

    def gadget_cx(self, start, finish) -> GateType:
        control_type, target_type = cx_rules[(start.type, finish.type)]

    def gadget_cz(self) -> GateType:
        pass

    def cx_gadget(self) -> GateType:
        pass

    def cz_gadget(self) -> GateType:
        pass

    def conjugate_single(self, qubit: int, rules: dict):
        leg_type, multiplier = rules[self.legs[qubit].type]
        self.legs[qubit] = LegType.return_object(type=leg_type, qubit=qubit)
        self.phase_node.phase *= multiplier

    def conjugate_multi(self, control_qubit: int, target_qubit: int, rules: dict):
        control_type, target_type = rules[(self.legs[control_qubit].type, self.legs[target_qubit].type)]
        self.legs[control_qubit] = LegType.return_object(qubit=control_qubit, type=control_type)
        self.legs[target_qubit] = LegType.return_object(qubit=target_qubit, type=target_type)

    def conjugate_x(self, qubit: int):
        self.conjugate_single(qubit=qubit, rules=x_rules)

    def conjugate_z(self, qubit: int):
        self.conjugate_single(qubit=qubit, rules=z_rules)

    def conjugate_cx(self, control: int, target: int):
        self.conjugate_multi(control_qubit=control, target_qubit=target, rules=cx_rules)

    def conjugate_cz(self, control: int, target: int):
        self.conjugate_multi(control_qubit=control, target_qubit=target, rules=cz_rules)
