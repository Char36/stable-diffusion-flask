from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ImageData(_message.Message):
    __slots__ = ["chunk_data", "seed"]
    CHUNK_DATA_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    chunk_data: bytes
    seed: str
    def __init__(self, seed: _Optional[str] = ..., chunk_data: _Optional[bytes] = ...) -> None: ...

class ImagineRequest(_message.Message):
    __slots__ = ["C", "H", "W", "ddim_steps", "f", "from_file", "n_iter", "n_rows", "n_samples", "prompt", "scale", "seed", "turbo"]
    C: int
    C_FIELD_NUMBER: _ClassVar[int]
    DDIM_STEPS_FIELD_NUMBER: _ClassVar[int]
    FROM_FILE_FIELD_NUMBER: _ClassVar[int]
    F_FIELD_NUMBER: _ClassVar[int]
    H: int
    H_FIELD_NUMBER: _ClassVar[int]
    N_ITER_FIELD_NUMBER: _ClassVar[int]
    N_ROWS_FIELD_NUMBER: _ClassVar[int]
    N_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    SCALE_FIELD_NUMBER: _ClassVar[int]
    SEED_FIELD_NUMBER: _ClassVar[int]
    TURBO_FIELD_NUMBER: _ClassVar[int]
    W: int
    W_FIELD_NUMBER: _ClassVar[int]
    ddim_steps: int
    f: int
    from_file: bool
    n_iter: int
    n_rows: int
    n_samples: int
    prompt: str
    scale: int
    seed: int
    turbo: bool
    def __init__(self, prompt: _Optional[str] = ..., from_file: bool = ..., ddim_steps: _Optional[int] = ..., n_iter: _Optional[int] = ..., H: _Optional[int] = ..., W: _Optional[int] = ..., C: _Optional[int] = ..., f: _Optional[int] = ..., n_samples: _Optional[int] = ..., n_rows: _Optional[int] = ..., seed: _Optional[int] = ..., turbo: bool = ..., scale: _Optional[int] = ...) -> None: ...

class ImagineResponse(_message.Message):
    __slots__ = ["image_data"]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    image_data: _containers.RepeatedCompositeFieldContainer[ImageData]
    def __init__(self, image_data: _Optional[_Iterable[_Union[ImageData, _Mapping]]] = ...) -> None: ...
