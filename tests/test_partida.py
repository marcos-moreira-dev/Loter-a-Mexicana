"""Pruebas de flujo principal de partida."""

from pathlib import Path
import random
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from model.carton import Carton
from model.configuracion import ConfiguracionPartida, ModoPartida
from model.mazo import Mazo
from model.partida import EstadoPartida, Partida, ResultadoLoteria, ResultadoMarcado
from model.reglas import Alineacion


class PartidaTest(unittest.TestCase):
    def crear_partida(
        self,
        modo: ModoPartida,
        alineacion: Alineacion | None = None,
    ) -> Partida:
        partida = Partida(
            mazo=Mazo(),
            configuracion=ConfiguracionPartida(
                nombre_jugador="Marco",
                modo_partida=modo,
                alineacion_preferida=alineacion,
            ),
            repositorio_reportes=None,
            rng=random.Random(1234),
        )
        partida.iniciar()
        return partida

    def test_partida_respeta_alineacion_configurada(self) -> None:
        partida = self.crear_partida(modo=ModoPartida.SOLO_HUMANO, alineacion=Alineacion.COMPLETO)
        self.assertEqual(partida.alineacion_actual, Alineacion.COMPLETO)

    def test_humano_solo_puede_marcar_la_carta_actual(self) -> None:
        partida = self.crear_partida(modo=ModoPartida.SOLO_HUMANO)
        assert partida.jugador_humano is not None

        partida.jugador_humano.carton = Carton(partida.mazo.cartas[:16])
        carta_actual = partida.mazo.obtener_carta_por_id(5)
        assert carta_actual is not None
        partida.carta_actual = carta_actual

        self.assertEqual(
            partida.marcar_carta_humano(6),
            ResultadoMarcado.CARTA_NO_ACTUAL,
        )
        self.assertEqual(
            partida.marcar_carta_humano(5),
            ResultadoMarcado.MARCADA,
        )
        self.assertEqual(
            partida.marcar_carta_humano(5),
            ResultadoMarcado.YA_MARCADA,
        )

    def test_humano_gana_al_reclamar_loteria_con_alineacion_valida(self) -> None:
        partida = self.crear_partida(modo=ModoPartida.SOLO_HUMANO)
        assert partida.jugador_humano is not None

        partida.alineacion_actual = Alineacion.ESQUINA
        partida.jugador_humano.carton = Carton(partida.mazo.cartas[:16])
        for indice in (0, 3, 12, 15):
            casilla = partida.jugador_humano.carton.obtener_casilla_por_indice(indice)
            assert casilla is not None
            casilla.marcar()

        self.assertEqual(partida.cantar_loteria_humano(), ResultadoLoteria.GANADA)
        self.assertEqual(partida.estado, EstadoPartida.GANADA)
        self.assertEqual(partida.ganador, partida.jugador_humano)

    def test_oponente_automatico_puede_ganar_en_su_turno(self) -> None:
        partida = self.crear_partida(modo=ModoPartida.HUMANO_VS_COMPUTADORA)
        assert partida.jugador_oponente is not None

        partida.alineacion_actual = Alineacion.INSIDE
        partida.jugador_oponente.carton = Carton(partida.mazo.cartas[:16])
        for indice in (5, 6, 9):
            casilla = partida.jugador_oponente.carton.obtener_casilla_por_indice(indice)
            assert casilla is not None
            casilla.marcar()

        carta_ganadora = partida.jugador_oponente.carton.obtener_casilla_por_indice(10)
        assert carta_ganadora is not None
        partida.mazo._cartas_restantes = [carta_ganadora.carta]

        partida.cantar_siguiente_carta()

        self.assertEqual(partida.estado, EstadoPartida.GANADA)
        self.assertEqual(partida.ganador, partida.jugador_oponente)

    def test_computadora_vs_computadora_bloquea_interaccion_manual(self) -> None:
        partida = self.crear_partida(modo=ModoPartida.COMPUTADORA_VS_COMPUTADORA)
        self.assertIsNone(partida.jugador_humano)
        self.assertTrue(partida.permite_interaccion_humana is False)
        self.assertEqual(partida.marcar_carta_humano(1), ResultadoMarcado.PARTIDA_NO_DISPONIBLE)

    def test_computadora_principal_puede_ganar_automaticamente(self) -> None:
        partida = self.crear_partida(modo=ModoPartida.COMPUTADORA_VS_COMPUTADORA)
        assert partida.jugador_principal is not None

        partida.alineacion_actual = Alineacion.ESQUINA
        partida.jugador_principal.carton = Carton(partida.mazo.cartas[:16])
        for indice in (0, 3, 12):
            casilla = partida.jugador_principal.carton.obtener_casilla_por_indice(indice)
            assert casilla is not None
            casilla.marcar()

        carta_ganadora = partida.jugador_principal.carton.obtener_casilla_por_indice(15)
        assert carta_ganadora is not None
        partida.mazo._cartas_restantes = [carta_ganadora.carta]

        partida.cantar_siguiente_carta()

        self.assertEqual(partida.estado, EstadoPartida.GANADA)
        self.assertEqual(partida.ganador, partida.jugador_principal)


if __name__ == "__main__":
    unittest.main()
