import pytest
from exporter.exporter import Exporter

def test_export_not_implemented():
    exporter = Exporter()
    with pytest.raises(NotImplementedError, match="Subclasses should implement this method"):
        exporter.export()
