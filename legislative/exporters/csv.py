from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from legislative.reports import BillReport, LegislatorReport


@dataclass(frozen=True)
class CsvReportExporter:
    path: Path
    protected_paths: tuple[Path, ...]

    def validate_path(self) -> None:
        for protected in self.protected_paths:
            if self.path.resolve() == protected.resolve() or (
                self.path.exists() and protected.exists() and self.path.samefile(protected)
            ):
                raise ValueError(f"Output must not overwrite input: {self.path}")

    def export(self, report: LegislatorReport | BillReport) -> None:
        self.validate_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                    dir=self.path.parent, delete=False) as destination:
                temporary = Path(destination.name)
                report.data.to_csv(destination, index=False)
            temporary.replace(self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
