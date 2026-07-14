import sys
from pathlib import Path
# make `import engine` (backtest/) and `import alpha_factory.*` resolvable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
