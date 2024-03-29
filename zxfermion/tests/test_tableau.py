from zxfermion.gadgets import CX, Gadget
from zxfermion.tableaus import Tableau


def test_tableau_cx():
    tableau = Tableau(CX())
    assert tableau.apply_tableau(Gadget('XX')) == Gadget('XI')
    # assert tableau.apply_tableau(Gadget('XY')) == Gadget('YZ')
    # assert tableau.apply_tableau(Gadget('XZ')) == Gadget('YY')
    # assert tableau.apply_tableau(Gadget('XI')) == Gadget('XX')
