import pytest
from exporter.exporter import Exporter

# TODO  move it ,to utils lib

def test_export_not_implemented():
    exporter = Exporter()
    with pytest.raises(NotImplementedError, match="Subclasses should implement this method"):
        exporter.export()
