"""Reproducción de música ambiental con listas aleatorias sin repetición inmediata."""

from __future__ import annotations

import random
import threading
import time
from pathlib import Path
from typing import Iterable, Optional

from infrastructure.paths import asset_path

try:
    import pygame
except ImportError:  # pragma: no cover - depende del entorno de ejecución
    pygame = None


class MusicManager:
    """Gestiona música de menú y de partida sin alterar la velocidad original."""

    MENU_TRACKS = (
        asset_path("music", "menu", "menu_cozy_living_room.mp3"),
        asset_path("music", "menu", "menu_tabletop_warmth.mp3"),
    )
    GAMEPLAY_TRACKS = (
        asset_path("music", "gameplay", "gameplay_mariachi_suspense_a.mp3"),
        asset_path("music", "gameplay", "gameplay_mariachi_suspense_b.mp3"),
        asset_path("music", "gameplay", "gameplay_mariachi_suspense_c.mp3"),
        asset_path("music", "gameplay", "gameplay_mariachi_tension.mp3"),
    )

    def __init__(self, *, enabled: bool = True, volume: float = 0.25) -> None:
        self.enabled = enabled
        self.volume = self._clamp_volume(volume)
        self._available = False
        self._mode: Optional[str] = None
        self._tracks: list[Path] = []
        self._queue: list[Path] = []
        self._last_track: Optional[Path] = None
        self._generation = 0
        self._lock = threading.RLock()
        self._worker: Optional[threading.Thread] = None

        self._initialize_audio()

    @property
    def available(self) -> bool:
        """Indica si el backend de audio quedó disponible."""

        return self._available

    def play_menu(self) -> None:
        """Activa la lista ambiental de pantallas no jugables."""

        self._switch_mode("menu", self.MENU_TRACKS)

    def play_gameplay(self) -> None:
        """Activa la lista de partida con variantes divertidas."""

        self._switch_mode("gameplay", self.GAMEPLAY_TRACKS)

    def set_enabled(self, enabled: bool) -> None:
        """Habilita o silencia por completo la música de fondo."""

        with self._lock:
            self.enabled = bool(enabled)
            if not self._available:
                return
            if not self.enabled:
                pygame.mixer.music.fadeout(500)
                return

            pygame.mixer.music.set_volume(self.volume)
            if self._mode and not pygame.mixer.music.get_busy():
                self._play_next_locked()

    def set_volume(self, volume: float) -> None:
        """Ajusta el volumen entre 0.0 y 1.0 sin tocar tempo ni tono."""

        with self._lock:
            self.volume = self._clamp_volume(volume)
            if self._available:
                pygame.mixer.music.set_volume(self.volume)

    def stop(self, fade_ms: int = 800) -> None:
        """Detiene la música con un desvanecimiento corto."""

        with self._lock:
            self._generation += 1
            self._mode = None
            self._tracks = []
            self._queue = []
            if self._available:
                pygame.mixer.music.fadeout(max(0, fade_ms))

    def shutdown(self) -> None:
        """Libera el mixer cuando la aplicación termina."""

        self.stop(fade_ms=300)
        if self._available:
            try:
                pygame.mixer.quit()
            except Exception:
                pass

    def _initialize_audio(self) -> None:
        if pygame is None:
            return
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
            self._available = True
        except Exception:
            self._available = False

    def _switch_mode(self, mode: str, tracks: Iterable[Path]) -> None:
        valid_tracks = [path for path in tracks if path.exists()]
        with self._lock:
            if self._mode == mode and self._tracks == valid_tracks:
                return

            self._generation += 1
            generation = self._generation
            self._mode = mode
            self._tracks = valid_tracks
            self._queue = []

            if not self._available or not self.enabled or not self._tracks:
                return

            was_busy = pygame.mixer.music.get_busy()
            self._refill_queue_locked()
            if was_busy:
                pygame.mixer.music.fadeout(500)
                threading.Thread(
                    target=self._start_after_fade,
                    args=(generation, 0.55),
                    name="music-transition",
                    daemon=True,
                ).start()
            else:
                self._play_next_locked(fade_ms=900)
                self._ensure_worker_locked(generation)

    def _start_after_fade(self, generation: int, delay_seconds: float) -> None:
        time.sleep(delay_seconds)
        with self._lock:
            if generation != self._generation or self._mode is None:
                return
            if self._available and self.enabled and self._tracks:
                self._play_next_locked(fade_ms=900)
                self._ensure_worker_locked(generation)

    def _ensure_worker_locked(self, generation: int) -> None:
        # Cada cambio de contexto inicia un vigilante nuevo; el anterior sale
        # por sí solo al detectar que cambió ``_generation``.
        self._worker = threading.Thread(
            target=self._playlist_worker,
            args=(generation,),
            name="music-playlist",
            daemon=True,
        )
        self._worker.start()

    def _playlist_worker(self, generation: int) -> None:
        while True:
            time.sleep(0.25)
            with self._lock:
                if generation != self._generation or self._mode is None:
                    return
                if not self._available or not self.enabled or not self._tracks:
                    continue
                if not pygame.mixer.music.get_busy():
                    self._play_next_locked(fade_ms=700)

    def _play_next_locked(self, fade_ms: int = 700) -> None:
        if not self._available or not self.enabled or not self._tracks:
            return
        if not self._queue:
            self._refill_queue_locked()
        if not self._queue:
            return

        track = self._queue.pop(0)
        try:
            pygame.mixer.music.load(str(track))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops=0, fade_ms=max(0, fade_ms))
            self._last_track = track
        except Exception:
            # Se descarta una pista defectuosa y se intenta la siguiente.
            if self._queue:
                self._play_next_locked(fade_ms=fade_ms)

    def _refill_queue_locked(self) -> None:
        queue = list(self._tracks)
        random.shuffle(queue)

        if self._last_track is not None and len(queue) > 1 and queue[0] == self._last_track:
            queue[0], queue[1] = queue[1], queue[0]

        self._queue = queue

    @staticmethod
    def _clamp_volume(volume: float) -> float:
        return max(0.0, min(1.0, float(volume)))
