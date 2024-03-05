from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, Union, Type
from enum import Enum


class VertexType:
    Z: int = 1
    X: int = 2
    H: int = 3


class EdgeType:
    S: int = 1
    H: int = 2


class LegType(str, Enum):
    I = 'I'
    X = 'X'
    Y = 'Y'
    Z = 'Z'

    @staticmethod
    def get_object(type: LegType, qubit: int) -> Union[LegX, LegY, LegZ, None]:
        return {
            LegType.I: LegI(qubit),
            LegType.X: LegX(qubit),
            LegType.Y: LegY(qubit),
            LegType.Z: LegZ(qubit),
        }[type]


class Node(BaseModel):
    row: int
    qubit: int
    type: Optional[int] = None
    phase: Optional[float] = None


class LegI:
    def __init__(self, qubit: int):
        self.qubit = qubit
        self.type = LegType.I
        self.middle = None
        self.left = None
        self.right = None
        self.nodes = None


class LegX:
    def __init__(self, qubit: int):
        self.qubit = qubit
        self.type = LegType.X
        self.middle = Node(row=2, qubit=self.qubit, type=VertexType.Z)
        self.left = Node(row=1, qubit=self.qubit, type=VertexType.H)
        self.right = Node(row=3, qubit=self.qubit, type=VertexType.H)
        self.nodes = [self.left, self.middle, self.right]


class LegY:
    def __init__(self, qubit: int):
        self.qubit = qubit
        self.type = LegType.Y
        self.middle = Node(row=2, qubit=self.qubit, type=VertexType.Z)
        self.left = Node(row=1, qubit=self.qubit, type=VertexType.X, phase=1/2)
        self.right = Node(row=3, qubit=self.qubit, type=VertexType.X, phase=-1/2)
        self.nodes = [self.left, self.middle, self.right]


class LegZ:
    def __init__(self, qubit: int):
        self.qubit = qubit
        self.type = LegType.Z
        self.middle = Node(row=2, qubit=self.qubit, type=VertexType.Z)
        self.left = None
        self.right = None
        self.nodes = [self.middle]
