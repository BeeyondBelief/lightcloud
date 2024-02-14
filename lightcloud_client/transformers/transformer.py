import abc


class BackwardTransformer(abc.ABC):

    @abc.abstractmethod
    def reverse(self, data: bytes) -> bytes:
        ...


class ForwardTransformer(abc.ABC):

    @abc.abstractmethod
    def transform(self, data: bytes) -> bytes:
        ...


class Transformer(ForwardTransformer, BackwardTransformer, abc.ABC):
    ...
