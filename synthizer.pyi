from enum import Enum
from typing import ContextManager, Iterator, List, Optional, Tuple, Union

StringOrBytes = Union[str, bytes]
EventSourceType = Union["Source", "Generator"]

class LoggingBackend(Enum):
    STDERR: int = ...

class LogLevel(Enum):
    DEBUG: int = ...
    ERROR: int = ...
    INFO: int = ...
    WARN: int = ...

class DistanceModel(Enum):
    NONE: int = ...
    LINEAR: int = ...
    EXPONENTIAL: int = ...
    INVERSE: int = ...

class NoiseType(Enum):
    FILTERED_BROWN: int = ...
    UNIFORM: int = ...
    VM: int = ...

class PannerStrategy(Enum):
    HRTF: int = ...
    STEREO: int = ...

# Initialization functions:

def initialized(
    log_level: LogLevel = ...,
    logging_backend: LoggingBackend = ...,
    libsndfile_path: StringOrBytes = ...,
) -> ContextManager[None]: ...
def initialize(
    log_level: LogLevel = ...,
    logging_backend: LoggingBackend = ...,
    libsndfile_path: StringOrBytes = ...,
) -> None: ...
def shutdown() -> None: ...

class BiquadConfig:
    @staticmethod
    def design_identity() -> "BiquadConfig": ...
    @staticmethod
    def design_lowpass(frequency: float, q: float = ...) -> "BiquadConfig": ...
    @staticmethod
    def design_highpass(frequency: float, q: float = ...) -> "BiquadConfig": ...
    @staticmethod
    def design_bandpass(frequency: float, bandwidth: float) -> "BiquadConfig": ...


class IntProperty(_PropertyBase): ...

class DoubleProperty(_PropertyBase): ...

class Double3Property(_PropertyBase): ...

class Double6Property(_PropertyBase): ...

class BiquadProperty(_PropertyBase): ...

class ObjectProperty(_PropertyBase): ...

class _BaseObject:
    def __init__(self, _handle: int) -> None: ...
    def dec_ref(self) -> None: ...
    def get_userdata(self) -> object: ...
    def set_userdata(self, data: object) -> None: ...
    def config_delete_behavior(self, linger: bool = ..., linger_timeout: float = ...): ...

class Pausable(_BaseObject):
    def pause(self) -> None: ...
    def play(self) -> None: ...

# Hard to type factory here.
def register_stream_protocol(protocol: str, factory): ...

class StreamHandle(_BaseObject):
    @staticmethod
    def from_file(path: StringOrBytes) -> "StreamHandle": ...
    @staticmethod
    def from_stream_params(
        protocol: StringOrBytes, path: StringOrBytes, param: int
    ) -> "StreamHandle": ...
    # Can't type Cython memoryviews.
    @staticmethod
    def from_memory(data) -> "StreamHandle": ...

class Buffer(_BaseObject):
    @staticmethod
    def from_stream_params(
        protocol: StringOrBytes,
        path: StringOrBytes,
    ) -> "Buffer": ...
    @staticmethod
    def from_file(path: StringOrBytes) -> "Buffer": ...
    # Note that we can't exactly type Cython memoryviews.
    @staticmethod
    def from_encoded_data(data) -> "Buffer": ...
    # again, we can't type CYthon memoryviews.
    @staticmethod
    def from_float_array(sr: int, channels: int, data) -> "Buffer": ...
    @staticmethod
    def from_stream_handle(stream: StreamHandle) -> "Buffer": ...
    def get_channels(self) -> int: ...
    def get_length_in_samples(self) -> int: ...
    def get_length_in_seconds(self) -> float: ...
    def get_size_in_bytes(self) -> float: ...

class Generator(Pausable):
    gain: DoubleProperty = ...
    pitch_bend: DoubleProperty = ...

class Source(Pausable):
    gain: DoubleProperty = ...
    filter: BiquadProperty = ...
    def add_generator(self, generator: Generator) -> None: ...
    def remove_generator(self, generator: Generator) -> None: ...

class GlobalEffect(_BaseObject):
    gain: DoubleProperty = ...
    filter_input: BiquadProperty = ...
    def reset(self) -> None: ...

class Context(Pausable):
    default_closeness_boost: DoubleProperty = ...
    default_closeness_boost_distance: DoubleProperty = ...
    default_distance_max: DoubleProperty = ...
    default_distance_model: IntProperty = ...
    default_distance_ref: DoubleProperty = ...
    default_gain: DoubleProperty = ...
    default_orientation: Double6Property = ...
    default_panner_strategy: IntProperty = ...
    default_position: Double3Property = ...
    default_rolloff: DoubleProperty = ...
    def __init__(self, enable_events: bool = ...) -> None: ...
    def config_route(
        self,
        output: Source,
        input: GlobalEffect,
        gain: float = ...,
        fade_time: float = ...,
        filter: BiquadConfig = ...,
    ) -> None: ...
    def enable_events(self) -> None: ...
    def get_events(self, limit: int = ...) -> Iterator["Event"]: ...
    def remove_route(
        self, output: Source, input: GlobalEffect, fade_time: float = ...
    ) -> None: ...

class DirectSource(Source):
    def __init__(self, context: "Context") -> None: ...

class AngularPannedSource(Source):
    azimuth: DoubleProperty = ...
    elevation: DoubleProperty = ...
    panning_scalar: DoubleProperty = ...
    def __init__(
        self,
        context: "Context",
        panner_strategy: "PannerStrategy" = ...,
        azimuth: float = ...,
        elevation: float = ...,
    ) -> None: ...

class ScalarPannedSource(Source):
    panning_scalar: DoubleProperty = ...
    def __init__(
        self,
        context: "Context",
        panner_strategy: "PannerStrategy" = ...,
        panning_scalar: float = ...,
    ) -> None: ...

class Source3D(Source):
    closeness_boost: DoubleProperty = ...
    closeness_boost_distance: DoubleProperty = ...
    distance_max: DoubleProperty = ...
    distance_model: IntProperty = ...
    distance_ref: DoubleProperty = ...
    orientation: Double6Property = ...
    position: Double3Property = ...
    rolloff: DoubleProperty = ...
    def __init__(
        self,
        context: "Context",
        panner_strategy: "PannerStrategy" = ...,
        position: Tuple[float, float, float] = ...,
    ) -> None: ...

class BufferGenerator(Generator):
    buffer: ObjectProperty = ...
    looping: IntProperty = ...
    playback_position: DoubleProperty = ...
    def __init__(self, context: Context) -> None: ...

class EchoTapConfig:
    delay: float
    gain_l: float
    gain_r: float
    def __init__(self, delay: float, gain_l: float, gain_r: float) -> None: ...

class Event:
    context: Context
    source: Optional[EventSourceType]
    # __init__ shouldn't be used by user code, but can't easily be made private to Cython.

class FinishedEvent(Event):
    pass

class LoopedEvent(Event):
    pass

class GlobalEcho(GlobalEffect):
    def __init__(self, context: Context) -> None: ...
    def set_taps(self, taps: List[EchoTapConfig]) -> None: ...

class GlobalFdnReverb(GlobalEffect):
    late_reflections_delay: DoubleProperty = ...
    late_reflections_diffusion: DoubleProperty = ...
    late_reflections_hf_reference: DoubleProperty = ...
    late_reflections_hf_rolloff: DoubleProperty = ...
    late_reflections_lf_reference: DoubleProperty = ...
    late_reflections_lf_rolloff: DoubleProperty = ...
    late_reflections_modulation_depth: DoubleProperty = ...
    late_reflections_modulation_frequency: DoubleProperty = ...
    mean_free_path: DoubleProperty = ...
    t60: DoubleProperty = ...
    def __init__(self, context: Context) -> None: ...

class NoiseGenerator(Generator):
    noise_type: IntProperty = ...
    def __init__(self, context: Context, channels: int = ...) -> None: ...

class StreamingGenerator(Generator):
    looping: IntProperty = ...
    playback_position: DoubleProperty = ...

    @staticmethod
    def from_stream_params(
        context: Context,
        protocol: StringOrBytes,
        path: StringOrBytes,
        options: StringOrBytes = ...,
    ) -> StreamingGenerator: ...
    
    @staticmethod
    def from_file(path: StringOrBytes) -> StreamingGenerator: ...

    @staticmethod
    def from_stream_handle(context: Context, stream: StreamHandle) -> StreamingGenerator: ...


class SynthizerError(Exception): ...
