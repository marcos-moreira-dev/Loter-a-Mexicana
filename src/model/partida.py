"""Modelo principal de la partida."""

from __future__ import annotations

from datetime import datetime
from enum import Enum, auto
import random
import time
from typing import List, Optional, Set

from model.carta import Carta
from model.carton import Carton
from model.configuracion import ConfiguracionPartida, ModoPartida
from model.jugador import Jugador
from model.mazo import Mazo
from model.reglas import Alineacion, obtener_definicion, obtener_oficiales, verificar_carton
from model.reportes import RegistroPartida, RepositorioReportes


class EstadoPartida(Enum):
    """Estados permitidos de la partida."""

    NO_INICIADA = auto()
    EN_CURSO = auto()
    GANADA = auto()
    FINALIZADA = auto()


class ResultadoMarcado(Enum):
    """Resultados posibles al intentar marcar una casilla humana."""

    MARCADA = auto()
    SIN_CARTA_ACTUAL = auto()
    CARTA_NO_ACTUAL = auto()
    CARTA_NO_EN_CARTON = auto()
    YA_MARCADA = auto()
    PARTIDA_NO_DISPONIBLE = auto()


class ResultadoLoteria(Enum):
    """Resultados posibles al reclamar loteria."""

    GANADA = auto()
    ALINEACION_INCOMPLETA = auto()
    PARTIDA_NO_DISPONIBLE = auto()


class Partida:
    """Coordina una partida profesional de Loteria Mexicana."""

    def __init__(
        self,
        mazo: Mazo,
        configuracion: ConfiguracionPartida,
        repositorio_reportes: Optional[RepositorioReportes] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.mazo = mazo
        self.configuracion = configuracion
        self.repositorio_reportes = repositorio_reportes
        self._rng = rng or random.Random()

        self.estado = EstadoPartida.NO_INICIADA
        self.jugadores: List[Jugador] = []
        self.carta_actual: Optional[Carta] = None
        self.historial_cartas: List[Carta] = []
        self.ganador: Optional[Jugador] = None
        self.alineacion_actual: Optional[Alineacion] = None

        self._fecha_inicio: Optional[datetime] = None
        self._inicio_monotonic: Optional[float] = None
        self._duracion_final_segundos: Optional[int] = None
        self._resultado_reportado = False

    def iniciar(self) -> None:
        """Prepara una partida nueva usando la configuracion activa."""

        self.mazo.reiniciar()
        self.historial_cartas = []
        self.carta_actual = None
        self.ganador = None
        self.alineacion_actual = (
            self.configuracion.alineacion_preferida
            or self._rng.choice(list(obtener_oficiales()))
        )
        self._duracion_final_segundos = None
        self._resultado_reportado = False

        jugador_principal = Jugador(
            nombre=(
                self.configuracion.nombre_jugador
                if self.configuracion.permite_interaccion_humana
                else "Computadora 1"
            ),
            carton=Carton.generar_aleatorio(self.mazo.cartas, self._rng),
            es_automatico=self.configuracion.primer_jugador_es_automatico,
        )
        jugadores = [jugador_principal]

        if self.configuracion.incluir_oponente_automatico:
            oponente = Jugador(
                nombre=(
                    "Computadora 2"
                    if self.configuracion.modo_partida == ModoPartida.COMPUTADORA_VS_COMPUTADORA
                    else self.configuracion.nombre_oponente
                ),
                carton=Carton.generar_aleatorio(self.mazo.cartas, self._rng),
                es_automatico=True,
            )
            jugadores.append(oponente)

        self.jugadores = jugadores
        self.estado = EstadoPartida.EN_CURSO
        self._fecha_inicio = datetime.now().astimezone()
        self._inicio_monotonic = time.monotonic()

    def reiniciar(self) -> None:
        """Reinicia la partida actual."""

        self.iniciar()

    def cantar_siguiente_carta(self) -> Optional[Carta]:
        """Canta la siguiente carta disponible del mazo."""

        if self.estado != EstadoPartida.EN_CURSO:
            return None

        if self.mazo.esta_vacio():
            self._finalizar_sin_ganador()
            return None

        self.carta_actual = self.mazo.siguiente_carta()
        if self.carta_actual is None:
            self._finalizar_sin_ganador()
            return None

        self.historial_cartas.append(self.carta_actual)
        self._procesar_jugadores_automaticos()
        return self.carta_actual

    def marcar_carta_humano(self, id_carta: int) -> ResultadoMarcado:
        """Marca la carta del humano solo si coincide con la carta actual."""

        if self.estado != EstadoPartida.EN_CURSO:
            return ResultadoMarcado.PARTIDA_NO_DISPONIBLE

        if not self.permite_interaccion_humana:
            return ResultadoMarcado.PARTIDA_NO_DISPONIBLE

        if self.carta_actual is None:
            return ResultadoMarcado.SIN_CARTA_ACTUAL

        if self.carta_actual.id != id_carta:
            return ResultadoMarcado.CARTA_NO_ACTUAL

        humano = self.jugador_humano
        if humano is None:
            return ResultadoMarcado.PARTIDA_NO_DISPONIBLE

        if not humano.carton.contiene(id_carta):
            return ResultadoMarcado.CARTA_NO_EN_CARTON

        if not humano.marcar_carta(id_carta):
            return ResultadoMarcado.YA_MARCADA

        return ResultadoMarcado.MARCADA

    def cantar_loteria_humano(self) -> ResultadoLoteria:
        """Permite al humano reclamar loteria cuando crea cumplir la alineacion."""

        if self.estado != EstadoPartida.EN_CURSO:
            return ResultadoLoteria.PARTIDA_NO_DISPONIBLE

        humano = self.jugador_humano
        if humano is None or self.alineacion_actual is None:
            return ResultadoLoteria.PARTIDA_NO_DISPONIBLE

        if verificar_carton(humano.carton, self.alineacion_actual):
            self._declarar_ganador(humano)
            return ResultadoLoteria.GANADA

        return ResultadoLoteria.ALINEACION_INCOMPLETA

    def obtener_cartas_cantadas_ids(self) -> Set[int]:
        """Conjunto de ids ya cantados."""

        return {carta.id for carta in self.historial_cartas}

    def _procesar_jugadores_automaticos(self) -> None:
        """Marca automaticamente las cartas de los jugadores controlados por la maquina."""

        if self.carta_actual is None:
            return

        if self.alineacion_actual is None:
            return

        for jugador in self.jugadores:
            if not jugador.es_automatico:
                continue

            if jugador.carton.contiene(self.carta_actual.id):
                jugador.marcar_carta(self.carta_actual.id)

            if verificar_carton(jugador.carton, self.alineacion_actual):
                self._declarar_ganador(jugador)
                break

    def _declarar_ganador(self, jugador: Jugador) -> None:
        """Declara al ganador y registra el resultado."""

        jugador.declarar_ganador()
        self.ganador = jugador
        self.estado = EstadoPartida.GANADA
        self._duracion_final_segundos = self._calcular_duracion_segundos()
        self._guardar_reporte()

    def _finalizar_sin_ganador(self) -> None:
        """Cierra la partida sin ganador."""

        self.estado = EstadoPartida.FINALIZADA
        self._duracion_final_segundos = self._calcular_duracion_segundos()
        self._guardar_reporte()

    def _calcular_duracion_segundos(self) -> int:
        """Retorna la duracion transcurrida en segundos."""

        if self._inicio_monotonic is None:
            return 0
        return max(0, int(time.monotonic() - self._inicio_monotonic))

    def _guardar_reporte(self) -> None:
        """Persiste el resumen de la partida si existe repositorio."""

        if self._resultado_reportado or self.repositorio_reportes is None:
            return

        alineacion = self.alineacion_actual or Alineacion.FILA
        definicion = obtener_definicion(alineacion)
        fecha = self._fecha_inicio or datetime.now().astimezone()

        self.repositorio_reportes.guardar(
            RegistroPartida(
                fecha_iso=fecha.isoformat(),
                ganador=self.ganador.nombre if self.ganador else None,
                alineacion=alineacion.value,
                descripcion_alineacion=definicion.nombre,
                duracion_segundos=self.duracion_segundos,
                cartas_cantadas=len(self.historial_cartas),
                participantes=self.configuracion.cantidad_participantes,
            )
        )
        self._resultado_reportado = True

    @property
    def jugador_principal(self) -> Optional[Jugador]:
        return self.jugadores[0] if self.jugadores else None

    @property
    def jugador_humano(self) -> Optional[Jugador]:
        jugador = self.jugador_principal
        if jugador is None or jugador.es_automatico:
            return None
        return jugador

    @property
    def jugador_oponente(self) -> Optional[Jugador]:
        return self.jugadores[1] if len(self.jugadores) > 1 else None

    @property
    def permite_interaccion_humana(self) -> bool:
        return self.configuracion.permite_interaccion_humana

    @property
    def descripcion_alineacion(self) -> str:
        if self.alineacion_actual is None:
            return ""
        return obtener_definicion(self.alineacion_actual).descripcion

    @property
    def nombre_alineacion(self) -> str:
        if self.alineacion_actual is None:
            return ""
        return obtener_definicion(self.alineacion_actual).nombre

    @property
    def cartas_restantes(self) -> int:
        return self.mazo.cartas_restantes

    @property
    def duracion_segundos(self) -> int:
        if self._duracion_final_segundos is not None:
            return self._duracion_final_segundos
        return self._calcular_duracion_segundos()

    @property
    def partida_finalizada(self) -> bool:
        return self.estado in (EstadoPartida.GANADA, EstadoPartida.FINALIZADA)

    @property
    def partida_en_curso(self) -> bool:
        return self.estado == EstadoPartida.EN_CURSO

    def __str__(self) -> str:
        return (
            f"Partida(estado={self.estado.name}, alineacion={self.nombre_alineacion}, "
            f"cartas_cantadas={len(self.historial_cartas)})"
        )
