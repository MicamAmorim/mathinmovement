from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import ENEMSolutionScene
from specs import SPECS

class Resolucao05(ENEMSolutionScene):
    SPEC=SPECS[4]

