from zxfermion.types import GateType


class Tableau:
    def __init__(self, start: GateType, finish: GateType):
        match [start.type, finish.type]:
            case [GateType.GADGET, GateType.CX]:
                self.gadget_cx()
            case [GateType.GADGET, GateType.CZ]:
                pass
            case [GateType.CX, GateType.GADGET]:
                pass
            case [GateType.CZ, GateType.GADGET]:
                pass

    def gadget_cx(self) -> GateType:
        pass

    def gadget_cz(self) -> GateType:
        pass

    def cx_gadget(self) -> GateType:
        pass

    def cz_gadget(self) -> GateType:
        pass
