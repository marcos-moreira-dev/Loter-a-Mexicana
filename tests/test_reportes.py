"""Pruebas del repositorio de reportes."""

from pathlib import Path
import sys
import unittest
import uuid


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from model.reportes import RegistroPartida, RepositorioReportes


class RepositorioReportesTest(unittest.TestCase):
    def crear_ruta_temporal(self) -> Path:
        data_dir = PROJECT_ROOT / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir / f"test_reportes_{uuid.uuid4().hex}.json"

    def test_guardar_y_cargar_registros(self) -> None:
        ruta = self.crear_ruta_temporal()
        try:
            repositorio = RepositorioReportes(ruta)
            registro = RegistroPartida(
                fecha_iso="2026-03-23T10:00:00",
                ganador="Jugador 1",
                alineacion="COMPLETO",
                descripcion_alineacion="Carton completo",
                duracion_segundos=120,
                cartas_cantadas=22,
                participantes=2,
            )

            repositorio.guardar(registro)
            registros = repositorio.cargar()

            self.assertEqual(len(registros), 1)
            self.assertEqual(registros[0].ganador, "Jugador 1")
            self.assertEqual(registros[0].descripcion_alineacion, "Carton completo")
        finally:
            ruta.unlink(missing_ok=True)

    def test_eliminar_todos_vacia_el_historial(self) -> None:
        ruta = self.crear_ruta_temporal()
        try:
            repositorio = RepositorioReportes(ruta)
            repositorio.guardar(
                RegistroPartida(
                    fecha_iso="2026-03-23T10:00:00",
                    ganador="Jugador 1",
                    alineacion="LINEA",
                    descripcion_alineacion="Cualquier fila",
                    duracion_segundos=80,
                    cartas_cantadas=15,
                    participantes=1,
                )
            )

            repositorio.eliminar_todos()

            self.assertEqual(repositorio.cargar(), [])
            self.assertFalse(ruta.exists())
        finally:
            ruta.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
