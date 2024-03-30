from zxfermion.gates import CX, Gadget
from zxfermion.tableau import Tableau


def test_tableau_cx():
    tableau = Tableau(CX())
    assert tableau(Gadget('XX')) == Gadget('XX')
    # assert tableau(Gadget('XY')) == Gadget('YZ')
    # assert tableau(Gadget('XZ')) == Gadget('YY')
    # assert tableau(Gadget('XI')) == Gadget('XX')


# assert correct phases are being applied!

# something dodgy going on with Y conjugated by XMinus/XPlus
